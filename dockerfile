# Dockerfile - Railway optimized
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Create directories and set permissions
RUN mkdir -p templates static sample_emails && \
    chmod -R 755 /app

# Expose port (Railway auto-detects this)
EXPOSE 3000

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start command
CMD ["python", "app.py"]