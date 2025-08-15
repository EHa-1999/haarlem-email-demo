# 🏛️ Email Archivering Demo - Gemeente Haarlem

Een werkende demonstratie van MinIO-gebaseerde email archivering voor Nederlandse gemeenten.

## 🚀 1-Click Deploy naar Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-link)

## ✨ Demo Features

- **📧 Email Archivering** - Simulatie van real-time email opslag naar MinIO object storage
- **🔍 Geavanceerd Zoeken** - Nederlandse volledige-tekst zoeken in PostgreSQL metadata
- **🏛️ WOO Compliance** - Geautomatiseerde verwerking van Wet Open Overheid verzoeken
- **🔒 Data Classificatie** - Beveiligingsniveaus: openbaar, intern, vertrouwelijk
- **📊 Management Dashboard** - Real-time statistieken en systeemstatus
- **🔐 Audit Logging** - Complete logging van alle acties voor compliance

## 🎯 Demo Doelgroep

### Voor Bestuurders (5 minuten)
- **Dashboard**: Overzicht email statistieken en WOO status
- **Compliance**: Automatische WOO verzoek verwerking
- **Kostenbesparing**: Geen Exchange storage limieten meer

### Voor IT Management (15 minuten)
- **Architectuur**: PostgreSQL + MinIO + Python web interface
- **Performance**: Sub-seconde zoekresultaten over duizenden emails
- **Security**: Classificatie, encryption-ready, audit trails

### Voor Eindgebruikers (3 minuten)
- **Vertrouwde Interface**: Lijkt op huidige email zoeken
- **Enhanced Search**: Betere filters en zoekresultaten
- **Transparantie**: Duidelijke classificatie en status

## 📋 Technische Specificaties

### Architecture Stack
- **Backend**: Python Flask web application
- **Database**: PostgreSQL (metadata storage)
- **Storage**: MinIO-compatible object storage (email content)
- **Frontend**: Bootstrap 5 responsive web interface
- **Deployment**: Docker containerized, Railway.app ready

### Sample Data
- 5 realistische demo emails met verschillende classificaties
- 1 WOO verzoek in processing status
- Complete audit trails voor alle acties
- Nederlandse content voor authentieke demonstratie

## 🛠️ Lokale Development

### Vereisten
- Python 3.11+
- PostgreSQL database
- MinIO server (optioneel voor volledige demo)

### Setup
```bash
# Clone repository
git clone https://github.com/jouwusername/haarlem-email-demo.git
cd haarlem-email-demo

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/emailarchive"

# Run application
python app.py
```

Application beschikbaar op: http://localhost:3000

## 🌐 Railway Deployment

### Automatische Deployment
1. **Fork deze repository** naar je eigen GitHub account
2. **Ga naar Railway.app** en login met GitHub
3. **Klik "Deploy from GitHub repo"** en selecteer je fork
4. **Voeg PostgreSQL database toe** via Railway dashboard
5. **Deploy!** - Je app is binnen 3 minuten live

### Custom Domain (Optioneel)
- Railway → Settings → Custom Domain
- Configureer je eigen subdomain voor professionele demo

## 📊 Demo Scenarios

### Scenario 1: WOO Verzoek Verwerking
1. **Open WOO Dashboard** → Bekijk pending request
2. **Klik "Verwerk Verzoek"** → Automatische email matching
3. **Resultaat:** Snelle identificatie relevante emails + privacy filtering

### Scenario 2: Email Search & Discovery
1. **Open Search Interface** → Voer zoekterm in (bijv. "DMS")
2. **Pas filters toe** → Classificatie, datum range
3. **Resultaat:** Instant search results met metadata

### Scenario 3: Compliance & Audit
1. **Dashboard bekijken** → Statistieken en system status
2. **Zoek actie uitvoeren** → Automatische audit log entry
3. **Resultaat:** Complete traceability van alle acties

## 🔒 Security & Privacy

### Data Classificatie
- **Openbaar**: Publiceerbaar onder WOO
- **Intern**: Interne gemeentelijke communicatie
- **Vertrouwelijk**: Extra beveiliging, uitgesloten van WOO

### Audit Trail
- Alle search acties worden gelogd
- Complete user activity tracking
- Onweerlegbare logs voor compliance

### Privacy by Design
- Sample data bevat geen echte persoonsinformatie
- Encryptie-ready architectuur
- Nederlandse hosting voor data sovereignty

## 💰 Kosten & Planning

### Demo Hosting (Railway.app)
- **Development**: $0/maand (Hobby plan)
- **Productie demo**: $5/maand
- **Enterprise ready**: $20/maand

### Productie Implementatie
- **Phase 1**: Proof of Concept (50 gebruikers) - €50k
- **Phase 2**: Common Ground samenwerking - kostenreductie
- **Phase 3**: Full deployment (2000 gebruikers) - €350k (gedeeld)

## 🤝 Common Ground Ready

Deze demo is ontworpen als Common Ground component:
- **Herbruikbare architectuur** voor alle Nederlandse gemeenten
- **Open source approach** met gedeelde ontwikkelkosten
- **Standaard compliance** met Nederlandse overheidsrichtlijnen
- **Modulaire opzet** voor eenvoudige aanpassingen

## 📞 Support & Contact

### Demo Issues
- GitHub Issues voor technische problemen
- Railway support voor hosting vragen

### Business Vragen
- Email: [je-email@haarlem.nl]
- Voor implementatie gesprekken en business case

### Implementatie Partners
- **Base44**: Nederlandse cloud hosting en support
- **TransIP**: VPS hosting met Nederlandse support
- **Common Ground Community**: Samenwerking met andere gemeenten

## 🎯 Next Steps

### Voor Stakeholder Buy-in
1. **Share demo URL** met besluitvormers
2. **Plan guided demo sessions** (10-15 minuten)
3. **Verzamel feedback** via GitHub issues of email
4. **Verfijn business case** op basis van demo insights

### Voor Productie Planning
1. **Common Ground partners** identificeren
2. **Technical deep dive** met IT teams
3. **Compliance review** met privacy officers
4. **Implementatie roadmap** opstellen

---

**🚀 Ready to Deploy? Klik de Railway button hierboven!**

*Deze demo toont de kernfunctionaliteit van de voorgestelde email archivering architectuur. Voor productie implementatie zijn aanvullende security, monitoring en integratie features vereist.*

---

# .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Local development
instance/
.webassets-cache
local_settings.py

# Database
*.db
*.sqlite3

# Temporary files
*.tmp
temp/