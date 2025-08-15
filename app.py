# app.py - Railway optimized Email Archivering Demo
import os
import json
import hashlib
import logging
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.pool
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Railway database URL parsing
def get_db_config():
    """Parse Railway DATABASE_URL or use individual env vars"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse Railway DATABASE_URL (format: postgresql://user:pass@host:port/db)
        parsed = urlparse(database_url)
        return {
            'host': parsed.hostname,
            'database': parsed.path[1:],  # Remove leading /
            'user': parsed.username,
            'password': parsed.password,
            'port': parsed.port or 5432
        }
    else:
        # Fallback to individual env vars
        return {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'database': os.getenv('POSTGRES_DB', 'emailarchive'),
            'user': os.getenv('POSTGRES_USER', 'emailuser'),
            'password': os.getenv('POSTGRES_PASSWORD', 'emailpass123'),
            'port': int(os.getenv('POSTGRES_PORT', 5432))
        }

# Initialize database with retry logic
def init_database():
    """Initialize database with sample data"""
    db_config = get_db_config()
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_metadata (
                    id SERIAL PRIMARY KEY,
                    message_id VARCHAR(255) UNIQUE NOT NULL,
                    sender_email VARCHAR(255) NOT NULL,
                    sender_name VARCHAR(255),
                    recipient_email TEXT NOT NULL,
                    subject TEXT,
                    sent_date TIMESTAMP WITH TIME ZONE,
                    received_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    minio_bucket VARCHAR(100) NOT NULL,
                    minio_object_key VARCHAR(500) NOT NULL,
                    file_size_bytes INTEGER,
                    has_attachments BOOLEAN DEFAULT FALSE,
                    attachment_count INTEGER DEFAULT 0,
                    email_hash VARCHAR(64),
                    classification VARCHAR(50) DEFAULT 'unclassified',
                    retention_date DATE,
                    zaak_id VARCHAR(100),
                    is_confidential BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_audit_log (
                    id SERIAL PRIMARY KEY,
                    email_id INTEGER REFERENCES email_metadata(id),
                    action VARCHAR(50) NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    user_ip INET,
                    action_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    details JSONB
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS woo_requests (
                    id SERIAL PRIMARY KEY,
                    request_id VARCHAR(100) UNIQUE NOT NULL,
                    requester_name VARCHAR(255),
                    requester_email VARCHAR(255),
                    request_description TEXT,
                    search_terms TEXT,
                    request_date DATE DEFAULT CURRENT_DATE,
                    due_date DATE,
                    status VARCHAR(50) DEFAULT 'open',
                    assigned_to VARCHAR(100),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS woo_email_matches (
                    id SERIAL PRIMARY KEY,
                    woo_request_id INTEGER REFERENCES woo_requests(id),
                    email_id INTEGER REFERENCES email_metadata(id),
                    relevance_score DECIMAL(3,2),
                    included_in_response BOOLEAN DEFAULT FALSE,
                    exclusion_reason VARCHAR(255),
                    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_sender ON email_metadata(sender_email);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_subject ON email_metadata USING gin(to_tsvector('english', subject));")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email_date ON email_metadata(sent_date);")
            
            # Insert sample data if table is empty
            cursor.execute("SELECT COUNT(*) FROM email_metadata;")
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info("Inserting sample data...")
                
                sample_emails = [
                    ('demo-001@haarlem.nl', 'j.doe@haarlem.nl', 'John Doe', '["team@haarlem.nl", "manager@haarlem.nl"]',
                     'Project update - DMS implementatie voortgang', '2024-01-15 10:30:00+01', 'user-j-doe',
                     'emails/2024/01/demo-001.eml', 1024, 'ZAAK-2024-001', 'intern'),
                    
                    ('demo-002@haarlem.nl', 'burger@example.com', 'Bezorgde Burger', '["info@haarlem.nl"]',
                     'WOO verzoek - verkeerslichten en verkeersdata gemeente', '2024-01-16 14:20:00+01', 'user-info',
                     'emails/2024/01/demo-002.eml', 2048, 'WOO-2024-002', 'openbaar'),
                    
                    ('demo-003@haarlem.nl', 'wethouder@haarlem.nl', 'Wethouder Smith', '["griffie@haarlem.nl", "pers@haarlem.nl"]',
                     'VERTROUWELIJK: Coalitieoverleg agenda en afspraken', '2024-01-17 09:15:00+01', 'user-wethouder',
                     'emails/2024/01/demo-003.eml', 512, 'RAAD-2024-003', 'vertrouwelijk'),
                    
                    ('demo-004@haarlem.nl', 'projectleider@haarlem.nl', 'Project Manager IT', '["cio@haarlem.nl"]',
                     'MinIO implementatie - status update week 3', '2024-01-18 16:45:00+01', 'user-projectleider',
                     'emails/2024/01/demo-004.eml', 856, 'PROJ-2024-004', 'intern'),
                    
                    ('demo-005@haarlem.nl', 'journalist@haarlemsdagblad.nl', 'Journalist HD', '["woordvoering@haarlem.nl"]',
                     'Vragen over digitalisering gemeente - deadline artikel', '2024-01-19 11:30:00+01', 'user-woordvoering',
                     'emails/2024/01/demo-005.eml', 1500, 'PERS-2024-001', 'openbaar')
                ]
                
                for email_data in sample_emails:
                    cursor.execute("""
                        INSERT INTO email_metadata 
                        (message_id, sender_email, sender_name, recipient_email, subject, sent_date, 
                         minio_bucket, minio_object_key, file_size_bytes, zaak_id, classification)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, email_data)
                
                # Insert sample WOO request
                cursor.execute("""
                    INSERT INTO woo_requests 
                    (request_id, requester_name, requester_email, request_description, search_terms, due_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, ('WOO-2024-001', 'Journalist Haarlems Dagblad', 'journalist@haarlemsdagblad.nl',
                      'Verzoek om alle emails betreffende DMS implementatie en digitalisering projecten',
                      'DMS implementatie digitalisering', '2024-02-15', 'processing'))
                
                # Insert audit logs
                audit_logs = [
                    (1, 'created', 'system', '{"source": "exchange_transport", "automated": true}'),
                    (2, 'created', 'system', '{"source": "external_email", "woo_relevant": true}'),
                    (3, 'created', 'system', '{"source": "internal_email", "classification": "confidential"}'),
                    (4, 'created', 'system', '{"source": "project_email", "automated": true}'),
                    (5, 'created', 'system', '{"source": "external_email", "press_related": true}')
                ]
                
                for log_data in audit_logs:
                    cursor.execute("""
                        INSERT INTO email_audit_log (email_id, action, user_id, details)
                        VALUES (%s, %s, %s, %s)
                    """, log_data)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("Database initialized successfully!")
            return True
            
        except psycopg2.OperationalError as e:
            logger.warning(f"Database connection attempt {retry_count + 1} failed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(2)
            else:
                logger.error("Failed to connect to database after maximum retries")
                raise
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

# Database connection pool
db_config = get_db_config()
try:
    db_pool = psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)
    logger.info("Database pool created successfully")
except Exception as e:
    logger.error(f"Failed to create database pool: {e}")
    db_pool = None

def get_db_connection():
    if db_pool:
        return db_pool.getconn()
    else:
        # Fallback to direct connection
        return psycopg2.connect(**db_config)

def return_db_connection(conn):
    if db_pool:
        db_pool.putconn(conn)
    else:
        conn.close()

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        return_db_connection(conn)
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}, 500

@app.route('/')
def dashboard():
    """Hoofddashboard met overzicht statistieken"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Statistieken ophalen
        cursor.execute("""
            SELECT 
                COUNT(*) as total_emails,
                COUNT(CASE WHEN sent_date >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as emails_last_week,
                COUNT(CASE WHEN classification = 'vertrouwelijk' THEN 1 END) as confidential_emails,
                COUNT(CASE WHEN zaak_id IS NOT NULL THEN 1 END) as linked_to_cases,
                COALESCE(SUM(file_size_bytes), 0) as total_storage_bytes
            FROM email_metadata
        """)
        stats = cursor.fetchone()
        
        # Recente WOO verzoeken
        cursor.execute("""
            SELECT request_id, requester_name, request_description, 
                   request_date, status, due_date
            FROM woo_requests 
            ORDER BY request_date DESC 
            LIMIT 5
        """)
        recent_woo = cursor.fetchall()
        
        return render_template('dashboard.html', stats=stats, recent_woo=recent_woo)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return f"Dashboard tijdelijk niet beschikbaar: {e}", 500
    finally:
        if 'conn' in locals():
            return_db_connection(conn)

@app.route('/search')
def search_page():
    """Email zoekpagina"""
    return render_template('search.html')

@app.route('/api/search', methods=['POST'])
def search_emails():
    """API endpoint voor email zoeken"""
    try:
        data = request.json
        query = data.get('query', '')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        classification = data.get('classification')
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        where_conditions = []
        params = []
        
        if query:
            where_conditions.append("""
                (subject ILIKE %s OR
                 sender_email ILIKE %s OR
                 recipient_email ILIKE %s)
            """)
            params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
        
        if date_from:
            where_conditions.append("sent_date >= %s")
            params.append(date_from)
            
        if date_to:
            where_conditions.append("sent_date <= %s")
            params.append(date_to)
            
        if classification and classification != 'all':
            where_conditions.append("classification = %s")
            params.append(classification)
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        query_sql = f"""
            SELECT id, message_id, sender_email, sender_name, 
                   recipient_email, subject, sent_date, classification,
                   zaak_id, has_attachments, file_size_bytes
            FROM email_metadata
            {where_clause}
            ORDER BY sent_date DESC
            LIMIT 50
        """
        
        cursor.execute(query_sql, params)
        results = cursor.fetchall()
        
        # Log de zoekopdracht voor audit
        cursor.execute("""
            INSERT INTO email_audit_log (email_id, action, user_id, details)
            VALUES (NULL, 'search', %s, %s)
        """, ['demo_user', json.dumps({'query': query, 'results_count': len(results)})])
        conn.commit()
        
        return jsonify({
            'results': [dict(row) for row in results],
            'total': len(results)
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals():
            return_db_connection(conn)

@app.route('/woo')
def woo_dashboard():
    """WOO verzoeken dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT w.*, COUNT(wem.email_id) as matched_emails
            FROM woo_requests w
            LEFT JOIN woo_email_matches wem ON w.id = wem.woo_request_id
            GROUP BY w.id
            ORDER BY w.request_date DESC
        """)
        woo_requests = cursor.fetchall()
        
        return render_template('woo_dashboard.html', requests=woo_requests)
    except Exception as e:
        logger.error(f"WOO dashboard error: {e}")
        return f"WOO dashboard tijdelijk niet beschikbaar: {e}", 500
    finally:
        if 'conn' in locals():
            return_db_connection(conn)

# Initialize database on startup
if __name__ == '__main__':
    logger.info("Starting Email Archiving Demo...")
    
    # Initialize database
    init_database()
    
    # Get port from Railway environment
    port = int(os.getenv('PORT', 3000))
    
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)