# Complete Operations Manual

## Portable Offline AI Document Reader v1.0

**For Raspberry Pi and Headless Systems**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Deployment Methods](#deployment-methods)
3. [System Architecture](#system-architecture)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [REST API](#rest-api)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)
10. [Security](#security)
11. [Disaster Recovery](#disaster-recovery)
12. [Advanced Topics](#advanced-topics)

---

## Quick Start

### For Windows/Linux with Display
```bash
# Install
pip install -r requirements.txt

# Run GUI
python app.py
```

### For Raspberry Pi (No Display)
```bash
# Setup
bash setup_raspberry_pi.sh

# Run API Server
python app.py api

# Access: http://pi-ip:5000
```

### For Docker
```bash
# Build
docker build -t ai-reader .

# Run
docker run -p 5000:5000 -v $(pwd)/data:/app/data ai-reader

# Or with compose
docker-compose up
```

---

## Deployment Methods

### Method 1: Native Installation (Recommended for Pi)

**Pros**: Best performance, lowest overhead, native USB camera support  
**Cons**: Manual dependency management

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Clone application
git clone https://github.com/yourrepo/offline-ai-reader.git
cd offline-ai-reader

# 3. Run setup
bash setup_raspberry_pi.sh

# 4. Start
python3 app.py api

# 5. Access
# http://pi-ip:5000
```

### Method 2: Docker Deployment

**Pros**: Isolated environment, portable, reproducible  
**Cons**: Slight performance overhead, container complexity

```bash
# 1. Install Docker
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi

# 2. Clone and build
git clone https://github.com/yourrepo/offline-ai-reader.git
cd offline-ai-reader
docker build -t ai-reader .

# 3. Run
docker run -p 5000:5000 -v /home/pi/data:/app/data ai-reader

# 4. Or use compose
docker-compose up -d

# 5. Access
# http://pi-ip:5000
```

### Method 3: Virtual Environment (Development)

**Pros**: Isolated Python environment, good for testing  
**Cons**: Requires manual startup

```bash
# 1. Create venv
python3 -m venv venv
source venv/bin/activate

# 2. Install
pip install -r requirements.txt

# 3. Run
python app.py api

# 4. Access
# http://localhost:5000
```

---

## System Architecture

### Application Structure
```
offline-ai-reader/
├── app.py                          # Auto-detection entry point
├── app_headless.py                # CLI interface
├── app_api.py                     # REST API server
├── camera/                        # Camera module
│   ├── capture.py
│   └── document_detection.py
├── ocr/                          # OCR engines
│   ├── ocr_engine.py
│   ├── paddle_ocr.py
│   └── tesseract_ocr.py
├── ai/                           # AI features
│   ├── document_analyzer.py
│   ├── document_summarizer.py
│   └── question_answering.py
├── storage/                      # Database
│   ├── database.py
│   ├── document_manager.py
│   └── search_engine.py
├── ui/                          # GUI (for systems with display)
│   └── *.py (screen modules)
├── utils/                       # Utilities
│   ├── image_utils.py
│   ├── export.py
│   └── logger.py
├── config/                      # Configuration
│   └── settings.json
├── data/                        # Database and documents
│   └── documents.db
├── logs/                        # Application logs
└── docker-compose.yml           # Docker config
```

### Data Flow
```
Image Upload
    ↓
Document Detection (OpenCV)
    ↓
OCR (PaddleOCR → Tesseract)
    ↓
Text Extraction
    ↓
AI Analysis (Ollama)
    ↓
Database Storage (SQLite)
    ↓
Search Index
```

---

## Configuration

### Main Settings File: `config/settings.json`

```json
{
  "camera": {
    "device_id": 0,
    "resolution": [640, 480],
    "fps": 30,
    "auto_focus": true,
    "brightness": 50,
    "contrast": 50
  },
  "ocr": {
    "engine": "paddleocr",
    "fallback_engine": "tesseract",
    "languages": ["en", "sw", "fr", "ar", "es"],
    "enable_gpu": false
  },
  "ai": {
    "enabled": true,
    "model": "llama2",
    "ollama_url": "http://localhost:11434"
  },
  "storage": {
    "db_path": "./data/documents.db",
    "image_storage": "./data/images"
  }
}
```

### Environment Variables

```bash
# Set in systemd service or .bashrc
PYTHONUNBUFFERED=1              # Unbuffered output
TESSDATA_PREFIX=/path/to/tessdata
OMP_NUM_THREADS=4               # OpenMP threads
FLASK_ENV=production            # Flask mode
```

---

## Running the Application

### GUI Mode (Windows/Linux with Display)
```bash
python app.py
```
Creates CustomTkinter window with 6 screens:
- Dashboard
- Scan Document
- Document Library
- Search
- AI Assistant
- Settings

### API Server Mode (Recommended for Pi)
```bash
python app.py api
```
Starts Flask REST API on port 5000:
- Web dashboard at http://localhost:5000
- API endpoints at http://localhost:5000/api
- All features via REST calls

### Command-Line Mode
```bash
python app.py cli <command> [args]

# Examples
python app.py cli scan image.jpg --title "Document"
python app.py cli list
python app.py cli search "keyword"
python app.py cli analyze 1
python app.py cli export 1 --format pdf
```

### Interactive CLI Mode
```bash
python app.py interactive

# Interactive prompt
>>> list
>>> search invoice
>>> get 1
>>> analyze 1
>>> quit
```

---

## REST API

### Quick API Reference

```bash
# Health check (no auth)
curl http://localhost:5000/api/health

# List documents
curl -H "X-API-Key: your-key" http://localhost:5000/api/documents

# Search
curl -H "X-API-Key: your-key" "http://localhost:5000/api/search?q=keyword"

# Scan image
curl -X POST \
  -H "X-API-Key: your-key" \
  -F "file=@image.jpg" \
  http://localhost:5000/api/scan

# Get stats
curl -H "X-API-Key: your-key" http://localhost:5000/api/stats
```

See `API_DOCUMENTATION.md` for complete reference.

---

## Performance Optimization

### For Raspberry Pi 4

**Memory Usage**: 4GB minimum, 8GB recommended

```bash
# Monitor memory
free -h

# Reduce memory usage
# 1. Use Tesseract instead of PaddleOCR
# 2. Reduce image resolution
# 3. Enable memory swapping
# 4. Close unused services
```

**CPU Optimization**

```bash
# Check CPU cores
nproc

# Limit threads
export OMP_NUM_THREADS=2
```

**Storage Optimization**

```bash
# Use external SSD for better performance
sudo mount /dev/sda1 /mnt/ssd

# Update storage path in config
# "storage": { "db_path": "/mnt/ssd/documents.db" }
```

**Database Optimization**

```bash
# Rebuild indexes
sqlite3 data/documents.db "REINDEX;"

# Vacuum database
sqlite3 data/documents.db "VACUUM;"

# Analyze tables
sqlite3 data/documents.db "ANALYZE;"
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "No display" error on GUI startup
```bash
# Use API or CLI mode instead
python app.py api    # API server
python app.py cli    # Command-line
```

#### Issue: Camera not detected
```bash
# Check camera
ls /dev/video*

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"

# Add user to video group
sudo usermod -a -G video $(whoami)
sudo reboot
```

#### Issue: OCR slow or failing
```bash
# Switch to Tesseract in config/settings.json
"ocr": { "engine": "tesseract" }

# Or reduce image resolution
"camera": { "resolution": [320, 240] }
```

#### Issue: Out of memory
```bash
# Check memory
free -h

# Kill hanging processes
sudo killall python3

# Restart service
sudo systemctl restart ai-document-reader

# Increase swap (if needed)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Issue: Database locked
```bash
# Remove lock files
rm -f data/documents.db-wal
rm -f data/documents.db-shm

# Restart
sudo systemctl restart ai-document-reader
```

#### Issue: API not responding
```bash
# Check status
sudo systemctl status ai-document-reader

# View logs
sudo journalctl -u ai-document-reader -f

# Restart
sudo systemctl restart ai-document-reader

# Test port
netstat -tlnp | grep 5000
```

### Debug Logging

```bash
# View application logs
tail -f logs/app.log

# View API logs
tail -f logs/api.log

# View system logs
sudo journalctl -u ai-document-reader -f

# Set debug level in settings
# "logging": { "level": "DEBUG" }
```

---

## Maintenance

### Daily Tasks
```bash
# Monitor disk space
df -h

# Check service status
sudo systemctl status ai-document-reader

# Verify API health
curl http://localhost:5000/api/health
```

### Weekly Tasks
```bash
# Update OS packages
sudo apt-get update && sudo apt-get upgrade -y

# Backup database
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Check logs for errors
sudo journalctl -u ai-document-reader --since "7 days ago" | grep ERROR
```

### Monthly Tasks
```bash
# Full system backup
tar -czf full-backup-$(date +%Y%m%d).tar.gz . --exclude=.git --exclude=venv

# Clean logs
sudo journalctl --vacuum=30d

# Verify backups
tar -tzf backup-*.tar.gz | head
```

### Yearly Tasks
```bash
# OS upgrade
sudo apt-get dist-upgrade

# Python dependency updates
pip install --upgrade -r requirements.txt

# Full system audit
sudo apt list --upgradable
```

---

## Security

### API Security

**1. Change Default API Key**
```bash
# Edit app_api.py
nano app_api.py

# Change line:
API_KEY = "your-unique-32-char-minimum-key"

# Restart
sudo systemctl restart ai-document-reader
```

**2. HTTPS Configuration**
```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365

# Update app_api.py to use SSL
# See advanced topics below
```

**3. Rate Limiting** (Already implemented)
- 30 requests/minute per IP
- 100 requests/minute per API key
- 500+ concurrent requests possible

### System Security

**1. Firewall**
```bash
# Enable firewall
sudo ufw enable

# Allow specific ports
sudo ufw allow 22/tcp        # SSH
sudo ufw allow 5000/tcp      # API
sudo ufw allow 80/tcp        # HTTP
sudo ufw allow 443/tcp       # HTTPS

# Check status
sudo ufw status
```

**2. SSH Security**
```bash
# Disable password login
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
# PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart ssh
```

**3. User Permissions**
```bash
# Run as limited user (not root)
sudo useradd -m -s /bin/bash aiapp
sudo chown -R aiapp:aiapp /app/data

# Edit systemd service
# User=aiapp
```

### Data Security

**1. Encryption at Rest**
```bash
# Enable full disk encryption
sudo apt-get install cryptsetup

# Or encrypt data directory
gpg --symmetric data/documents.db
```

**2. Regular Backups**
```bash
# Automated backup script
#!/bin/bash
tar -czf /backup/ai-reader-$(date +%Y%m%d).tar.gz \
  /home/pi/offline-ai-reader/data/

# Add to crontab
# 0 2 * * * /usr/local/bin/backup-ai-reader.sh
```

---

## Disaster Recovery

### Backup Strategy

**Daily Incremental**
```bash
# Backup only changed files
tar -czf backup-inc-$(date +%Y%m%d).tar.gz \
  --newer-mtime-than backup-prev.tar.gz data/
```

**Weekly Full**
```bash
# Complete backup
tar -czf backup-full-$(date +%Y%m%d-%A).tar.gz \
  data/ config/
```

**Off-Site Storage**
```bash
# Copy to external drive or cloud
cp backup-*.tar.gz /mnt/external/backups/
scp backup-*.tar.gz user@backup-server:/backups/
```

### Recovery Procedure

**From Full Backup**
```bash
# 1. Stop service
sudo systemctl stop ai-document-reader

# 2. Restore files
tar -xzf backup-full-20240115-Monday.tar.gz

# 3. Verify database
sqlite3 data/documents.db "SELECT COUNT(*) FROM documents;"

# 4. Restart
sudo systemctl start ai-document-reader

# 5. Verify
curl http://localhost:5000/api/health
```

---

## Advanced Topics

### Running Multiple Instances

```bash
# Create separate config directory
mkdir ~/.ai-reader-instance-2
cp config/settings.json ~/.ai-reader-instance-2/

# Run on different port
CONFIG_DIR=~/.ai-reader-instance-2 python app.py api --port 5001
```

### Reverse Proxy with Nginx

```bash
# Install nginx
sudo apt-get install nginx

# Copy config
sudo cp nginx_config.conf /etc/nginx/sites-available/ai-reader

# Enable
sudo ln -s /etc/nginx/sites-available/ai-reader /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### HTTPS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Update nginx config
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
```

### Load Balancing

```bash
# Use multiple app instances behind nginx
upstream ai_cluster {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}

server {
    listen 80;
    location / {
        proxy_pass http://ai_cluster;
    }
}
```

### Monitoring & Alerting

```bash
# Setup Prometheus monitoring
docker run -p 9090:9090 prom/prometheus

# Setup log aggregation
sudo apt-get install filebeat

# Setup alerting
# Configure alertmanager
```

### Integration with Ollama

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull llama2

# Start service
ollama serve

# Update config
# "ai": { "ollama_url": "http://localhost:11434" }
```

---

## Support & Resources

### Documentation Files
- `README.md` - Project overview
- `API_DOCUMENTATION.md` - Complete API reference
- `RASPBERRY_PI_GUIDE.md` - Pi-specific guide
- `DEPLOYMENT_CHECKLIST.md` - Deployment steps
- `OPERATIONS_MANUAL.md` - This file

### Getting Help
- **GitHub Issues**: Report bugs
- **Discussions**: Ask questions
- **Email**: support@example.com

### Useful Commands Reference

```bash
# Service management
sudo systemctl start/stop/restart ai-document-reader
sudo systemctl status ai-document-reader
sudo systemctl enable/disable ai-document-reader

# Logging
sudo journalctl -u ai-document-reader -f
sudo journalctl -u ai-document-reader --since "1 hour ago"

# Database
sqlite3 data/documents.db ".tables"
sqlite3 data/documents.db ".schema documents"
sqlite3 data/documents.db "SELECT COUNT(*) FROM documents;"

# Network
curl -H "X-API-Key: key" http://localhost:5000/api/health
netstat -tlnp | grep 5000
lsof -i :5000

# Performance
top
htop
free -h
df -h
```

---

## Changelog

### v1.0.0 (2024-01-15)
- Initial release
- Raspberry Pi support
- REST API server
- Web dashboard
- Multi-format export
- Offline AI features
- SQLite database
- Dual OCR engines

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Maintained By**: Your Organization  
**Support Email**: support@example.com
