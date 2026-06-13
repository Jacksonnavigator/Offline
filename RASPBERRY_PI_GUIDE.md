# Raspberry Pi Deployment Guide

## Portable Offline AI Document Reader - Headless Edition

This guide covers deploying the application to Raspberry Pi 5 or similar systems without a display.

---

## System Requirements

### Hardware
- **Raspberry Pi 5** (8GB RAM recommended) or Pi 4 (4GB minimum)
- **USB Camera** (Logitech, Microsoft, or compatible)
- **USB Storage** (external SSD recommended for performance)
- **Power Supply** (5A USB-C for Pi 5, or 3A for Pi 4)
- **Network Connection** (Ethernet or WiFi)

### Storage
- **Minimum**: 4GB free space
- **Recommended**: 32GB+ (for document database and models)
- **Optimal**: SSD via USB 3.0 (much faster)

### OS
- **Raspberry Pi OS Lite** (recommended, no desktop GUI)
- Debian 12 (Bookworm) or later
- Ubuntu 22.04 Server (alternative)

---

## Installation Steps

### 1. Prepare Raspberry Pi OS

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Expand filesystem (if needed)
sudo raspi-config
# Select: Advanced Options > Expand Filesystem > Finish > Reboot
```

### 2. Clone/Download Application

```bash
# Option A: Clone from Git
git clone https://github.com/yourusername/offline-ai-reader.git
cd offline-ai-reader

# Option B: Copy files via SCP
scp -r offline/ pi@192.168.1.100:~/
```

### 3. Run Automated Setup

```bash
# Make setup script executable
chmod +x setup_raspberry_pi.sh

# Run setup
bash setup_raspberry_pi.sh
```

The script will:
- ✅ Install system dependencies
- ✅ Install Tesseract OCR
- ✅ Install Python packages
- ✅ Create necessary directories
- ✅ Setup systemd service (optional)

### 4. Verify Installation

```bash
# Check Python
python3 --version

# Check dependencies
pip3 list | grep -E "flask|opencv|paddleocr"

# Test basic functionality
python3 app.py api
```

---

## Running Modes

### Mode 1: REST API Server (Recommended)

Run the application as a web server accessible from other devices:

```bash
# Start server
python3 app.py api

# Or with custom port
FLASK_ENV=production python3 app.py api --port 8000
```

**Access:**
- Web Interface: `http://<pi-ip>:5000`
- API Base: `http://<pi-ip>:5000/api`
- Default API Key: `your-api-key-change-me` (change in app_api.py)

### Mode 2: Command-Line Interface

Execute single commands directly:

```bash
# Scan image
python3 app.py cli scan /path/to/image.jpg --title "Document Title"

# List documents
python3 app.py cli list --limit 10

# Search
python3 app.py cli search "keyword"

# Get document
python3 app.py cli get 1

# Analyze
python3 app.py cli analyze 1

# Summarize
python3 app.py cli summarize 1

# Ask question
python3 app.py cli ask 1 "What is the main topic?"

# Export
python3 app.py cli export 1 --format pdf

# Statistics
python3 app.py cli stats
```

### Mode 3: Interactive CLI

Interactive command prompt:

```bash
python3 app.py interactive
```

Commands:
```
>>> list                 # List documents
>>> search keyword       # Search
>>> get 1               # Get document details
>>> stats               # Show statistics
>>> help                # Show commands
>>> quit                # Exit
```

---

## Auto-Start on Boot

### Using systemd (Recommended)

```bash
# Setup service
sudo bash setup_service.sh

# Enable auto-start
sudo systemctl enable ai-document-reader

# Start now
sudo systemctl start ai-document-reader

# Check status
sudo systemctl status ai-document-reader

# View logs
sudo journalctl -u ai-document-reader -f
```

### Using cron

```bash
# Edit crontab
crontab -e

# Add line to start on reboot
@reboot cd /home/pi/offline-ai-reader && python3 app.py api > logs/api.log 2>&1
```

---

## API Usage Examples

### Web Interface
```
http://pi-ip:5000
```

### REST API

**Get health:**
```bash
curl -H "X-API-Key: your-api-key-change-me" http://pi-ip:5000/api/health
```

**List documents:**
```bash
curl -H "X-API-Key: your-api-key-change-me" http://pi-ip:5000/api/documents
```

**Scan image:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key-change-me" \
  -F "file=@image.jpg" \
  -F "title=My Document" \
  http://pi-ip:5000/api/scan
```

**Search:**
```bash
curl -H "X-API-Key: your-api-key-change-me" \
  "http://pi-ip:5000/api/search?q=keyword"
```

**Get document:**
```bash
curl -H "X-API-Key: your-api-key-change-me" http://pi-ip:5000/api/documents/1
```

**Analyze document:**
```bash
curl -X POST \
  -H "X-API-Key: your-api-key-change-me" \
  http://pi-ip:5000/api/documents/1/analyze
```

---

## Performance Optimization

### For Raspberry Pi 4

```bash
# Disable unnecessary services
sudo systemctl disable cups
sudo systemctl disable avahi-daemon

# Increase GPU memory (if using camera)
sudo raspi-config
# Performance Options > GPU Memory > Set to 128MB

# Disable WiFi power saving (if needed)
sudo iwconfig wlan0 power off
```

### Environment Variables

```bash
# Set in ~/.bashrc or service file
export PYTHONUNBUFFERED=1
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
export OMP_NUM_THREADS=4

# For faster OCR (less accuracy)
export PADDLEOCR_MODEL_DIR=/home/pi/.paddleocr/models
```

### Database Optimization

For large document collections:

```bash
# Rebuild search index
python3 app.py cli optimize-db

# Vacuum database
sqlite3 data/documents.db "VACUUM;"

# Analyze tables
sqlite3 data/documents.db "ANALYZE;"
```

---

## Camera Setup

### USB Camera

```bash
# Detect camera
lsusb | grep -i camera

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAILED')"

# List available cameras
for i in {0..5}; do python3 -c "import cv2; print('Camera $i:', cv2.VideoCapture($i).isOpened())" 2>/dev/null; done
```

### Configuration

Edit `config/settings.json`:

```json
{
  "camera": {
    "device_id": 0,
    "resolution": [640, 480],
    "fps": 30,
    "auto_focus": true,
    "brightness": 50,
    "contrast": 50
  }
}
```

---

## Network Configuration

### Find Pi IP Address

```bash
# Method 1
hostname -I

# Method 2
ip addr show | grep inet

# Method 3 (from another computer)
ping raspberrypi.local
```

### Remote Access

```bash
# SSH into Pi
ssh pi@192.168.1.100

# SSH with port forwarding
ssh -L 5000:localhost:5000 pi@192.168.1.100
```

### Firewall

```bash
# Allow API port
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

---

## Troubleshooting

### Issue: Import errors

```bash
# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall

# Check version conflicts
pip3 check
```

### Issue: Camera not detected

```bash
# Check permissions
ls -la /dev/video*

# Add user to video group
sudo usermod -a -G video pi
```

### Issue: Out of memory

```bash
# Check memory usage
free -h

# Monitor processes
top -b -n 1 | head -20

# Restart application
sudo systemctl restart ai-document-reader
```

### Issue: Slow OCR

```bash
# Use lighter OCR model
# Edit config/settings.json:
{
  "ocr": {
    "engine": "tesseract",  # Use Tesseract instead of PaddleOCR
    "languages": ["eng"]
  }
}

---

## venv wrapper and systemd sample

We've added a small run wrapper script and a sample systemd unit in the repository to make running and auto-starting the app more robust:

- `run.sh`: Activates `./venv` if present and runs the app via `app.py api`. Path: [run.sh](run.sh#L1)
- `ai-document-reader.service`: Sample systemd unit that calls `run.sh`. Path: [ai-document-reader.service](ai-document-reader.service#L1)

Usage:

```bash
# Make the wrapper executable
chmod +x run.sh

# Ensure venv exists and dependencies installed
python3 -m venv venv
./venv/bin/python -m pip install --upgrade pip setuptools wheel
./venv/bin/pip install -r requirements.txt

# Install the sample service (modify paths if needed)
sudo cp ai-document-reader.service /etc/systemd/system/ai-document-reader.service
sudo systemctl daemon-reload
sudo systemctl enable --now ai-document-reader

# Check status and logs
sudo systemctl status ai-document-reader
sudo journalctl -u ai-document-reader -f
```

Notes:

- The sample service uses `~` (`%h`) in the unit file as a convenience; update `WorkingDirectory` and `ExecStart` to absolute paths for production installs (e.g., `/home/pi/offline-ai-reader/run.sh`).
- `setup_service.sh` already writes a systemd unit that prefers `./venv/bin/python`. If you prefer the `run.sh` approach, copy the sample unit into `/etc/systemd/system` as shown above.

```

### Issue: Database locked

```bash
# Remove lock file
rm -f data/documents.db-wal
rm -f data/documents.db-shm

# Restart
sudo systemctl restart ai-document-reader
```

### View logs

```bash
# System service logs
sudo journalctl -u ai-document-reader -f

# Application logs
tail -f logs/app.log

# API server logs
tail -f logs/api.log
```

---

## Backup & Restore

### Backup Documents

```bash
# Backup database
cp data/documents.db data/documents.db.backup

# Full backup
tar -czf offline-backup-$(date +%Y%m%d).tar.gz data/ config/

# Copy to external drive
cp offline-backup-*.tar.gz /mnt/external/
```

### Restore

```bash
# Restore database
cp data/documents.db.backup data/documents.db

# Restore from archive
tar -xzf offline-backup-20240101.tar.gz
```

---

## Advanced Configuration

### Running Multiple Instances

```bash
# Create separate config directory
mkdir -p ~/.ai-reader-1
cp -r config ~/.ai-reader-1/

# Run with custom config
CONFIG_DIR=~/.ai-reader-1 python3 app.py api --port 5001
```

### Load Balancing

```bash
# Install nginx
sudo apt-get install nginx

# See nginx_config.conf for setup
sudo cp nginx_config.conf /etc/nginx/sites-available/ai-reader
sudo ln -s /etc/nginx/sites-available/ai-reader /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### HTTPS/SSL

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Run with SSL (update app_api.py)
python3 app.py api --ssl-cert cert.pem --ssl-key key.pem
```

---

## Maintenance

### Regular Tasks

```bash
# Weekly: Update packages
sudo apt-get update && sudo apt-get upgrade -y

# Monthly: Clean package cache
sudo apt-get clean
sudo apt-get autoclean

# Quarterly: Full backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/ config/

# Annually: OS upgrade
sudo apt-get dist-upgrade
```

### Monitor Health

```bash
# Create health check script
while true; do
  curl -s http://localhost:5000/api/health | grep -q healthy && echo "✅ OK" || echo "❌ DOWN"
  sleep 300
done
```

---

## Performance Benchmarks

### Raspberry Pi 5 (8GB)
- OCR Speed: ~10-15 seconds per page
- API Response: <500ms
- Concurrent Users: 10+
- Max Documents: 10,000+

### Raspberry Pi 4 (4GB)
- OCR Speed: ~20-30 seconds per page
- API Response: <1000ms
- Concurrent Users: 5
- Max Documents: 5,000

### Tips for Best Performance
1. Use SSD for storage
2. Reduce OCR resolution
3. Use Tesseract instead of PaddleOCR
4. Enable database indexing
5. Set memory limits
6. Disable auto-brightness

---

## Support & Resources

- **GitHub**: https://github.com/yourusername/offline-ai-reader
- **Issues**: https://github.com/yourusername/offline-ai-reader/issues
- **Discussions**: https://github.com/yourusername/offline-ai-reader/discussions
- **Documentation**: See README.md
- **API Docs**: http://pi-ip:5000/api/docs

---

## Change API Key

**IMPORTANT: Change the default API key before deployment!**

```bash
# Edit app_api.py
nano app_api.py

# Find and change this line:
API_KEY = "your-api-key-change-me"

# To your secure key:
API_KEY = "your-very-secure-api-key-32-characters-or-more"

# Restart service
sudo systemctl restart ai-document-reader
```

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0  
**Maintained by**: Your Organization
