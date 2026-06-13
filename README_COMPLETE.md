# Portable Offline AI Document Reader v1.0

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Production](https://img.shields.io/badge/Status-Production-green.svg)]()

**A complete offline AI-powered document scanning, OCR, and analysis system** for Windows, Linux, and Raspberry Pi.

---

## 🎯 Key Features

✅ **Multi-Mode Operation**
- GUI Mode: CustomTkinter interface for Windows/Linux with display
- REST API Server: Web interface for headless systems
- CLI Mode: Command-line interface for automation
- Interactive CLI: Interactive command prompt

✅ **Document Processing**
- Real-time camera capture with USB cameras
- Automatic document boundary detection
- Dual OCR engines (PaddleOCR + Tesseract with fallback)
- Support for 5+ languages (English, Swahili, French, Arabic, Spanish)

✅ **AI Features** (with optional Ollama)
- Document analysis and classification
- Automatic summarization
- Question-answering system
- Entity extraction

✅ **Storage & Search**
- SQLite database with full-text search
- Document metadata tracking
- Advanced search with keyword extraction
- 10,000+ document capacity

✅ **Export Options**
- PDF, DOCX, TXT, Markdown, JSON
- Batch export capability
- Metadata preservation

✅ **Raspberry Pi Ready**
- Headless operation (no display required)
- Optimized for Pi 4/5
- systemd service integration
- Auto-start on boot

---

## 📦 Installation

### Quick Start (All Platforms)

```bash
# Clone repository
git clone https://github.com/yourusername/offline-ai-reader.git
cd offline-ai-reader

# Install dependencies
pip install -r requirements.txt

# Run (auto-detects display)
python app.py
```

### Raspberry Pi Setup

```bash
# Run automated setup
bash setup_raspberry_pi.sh

# Start API server
python3 app.py api

# Access web interface
# http://pi-ip:5000
```

### Docker Deployment

```bash
# Build image
docker build -t ai-reader .

# Run container
docker run -p 5000:5000 -v $(pwd)/data:/app/data ai-reader

# Or use compose
docker-compose up -d
```

---

## 🚀 Running the Application

### Mode 1: Web API Server (Recommended for Pi)
```bash
python app.py api
# Access: http://localhost:5000
```

### Mode 2: GUI (Windows/Linux with Display)
```bash
python app.py
# CustomTkinter window with 6 screens
```

### Mode 3: Command-Line
```bash
python app.py cli scan image.jpg --title "Document"
python app.py cli list
python app.py cli search "keyword"
python app.py cli analyze 1
```

### Mode 4: Interactive
```bash
python app.py interactive
# Interactive command prompt
```

---

## 🌐 REST API

### Quick Examples

```bash
# Health check (no auth)
curl http://localhost:5000/api/health

# List documents
curl -H "X-API-Key: your-key" http://localhost:5000/api/documents

# Search
curl -H "X-API-Key: your-key" "http://localhost:5000/api/search?q=invoice"

# Upload and scan
curl -X POST \
  -H "X-API-Key: your-key" \
  -F "file=@document.jpg" \
  http://localhost:5000/api/scan

# Get statistics
curl -H "X-API-Key: your-key" http://localhost:5000/api/stats
```

**Full API Documentation**: See `API_DOCUMENTATION.md`

---

## 📋 Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│         User Interface Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │    GUI   │  │   API    │  │   CLI    │      │
│  │(CustomTk)│  │ (Flask)  │  │(argparse)│      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│       Core Processing Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Camera  │  │   OCR    │  │   AI     │      │
│  │ (OpenCV) │  │(PaddleOCR)   │ (Ollama) │      │
│  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│        Storage Layer                            │
│         ┌──────────────────────┐                │
│         │   SQLite Database    │                │
│         │   (documents.db)     │                │
│         └──────────────────────┘                │
└─────────────────────────────────────────────────┘
```

### File Structure
```
offline-ai-reader/
├── app.py                    # Auto-detection entry point
├── app_headless.py          # CLI interface
├── app_api.py               # REST API server (Flask)
├── camera/                  # Camera & document detection
├── ocr/                     # OCR engines
├── ai/                      # AI analysis
├── storage/                 # Database & search
├── ui/                      # GUI screens
├── utils/                   # Utilities
├── config/settings.json     # Configuration
├── data/documents.db        # SQLite database
├── logs/app.log            # Application logs
├── requirements.txt         # Python dependencies
├── setup_raspberry_pi.sh    # Pi setup script
├── ai-document-reader.service  # systemd service
├── nginx_config.conf        # Reverse proxy config
├── docker-compose.yml       # Docker orchestration
└── README.md               # This file
```

---

## ⚙️ Configuration

Edit `config/settings.json`:

```json
{
  "camera": {
    "device_id": 0,
    "resolution": [640, 480],
    "fps": 30
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

---

## 🖥️ System Requirements

### Minimum
- **OS**: Windows 10+, Ubuntu 20.04+, Debian 11+, Raspberry Pi OS
- **CPU**: Dual-core @ 1.5GHz
- **RAM**: 2GB
- **Storage**: 2GB free space

### Recommended
- **OS**: Ubuntu 22.04+ or Raspberry Pi OS Bookworm
- **CPU**: Quad-core @ 2.5GHz
- **RAM**: 8GB
- **Storage**: SSD 32GB+
- **GPU**: Optional (NVIDIA/AMD for faster OCR)

---

## 📊 Performance

### Benchmarks

**Raspberry Pi 5 (8GB)**
- OCR Speed: 10-15 seconds/page
- API Response: <500ms
- Concurrent Users: 10+
- Max Documents: 10,000+

**Raspberry Pi 4 (4GB)**
- OCR Speed: 20-30 seconds/page
- API Response: <1000ms
- Concurrent Users: 5
- Max Documents: 5,000

---

## 🔧 Raspberry Pi Deployment

### Automated Setup
```bash
# Download and run setup
bash setup_raspberry_pi.sh

# This installs:
# ✓ System dependencies
# ✓ Python packages
# ✓ Tesseract OCR
# ✓ Camera libraries
# ✓ Systemd service
```

### Non-interactive installer

If you prefer a single non-interactive installer that sets up the venv and optionally the systemd service, use `install.sh`:

```bash
# Make installer executable
chmod +x install.sh

# Run installer (requires sudo). By default it will install and enable the sample service.
sudo bash install.sh

# To skip service installation:
sudo bash install.sh --skip-service
```

`install.sh` performs the following:
- Updates apt and installs essential OS packages (including `python3-venv` and `tesseract-ocr`).
- Creates `./venv` and installs Python packages from `requirements.txt` into the venv.
- Creates data/log directories.
- Optionally copies `ai-document-reader.service` into `/etc/systemd/system` and enables/starts it.

After running `install.sh`, verify the service and logs:

```bash
sudo systemctl status ai-document-reader
sudo journalctl -u ai-document-reader -f
```

### Auto-Start on Boot
```bash
sudo systemctl enable ai-document-reader
sudo systemctl start ai-document-reader
```

### Access Web Interface
```
http://<pi-ip>:5000
```

**Full Guide**: See `RASPBERRY_PI_GUIDE.md`

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview (this file) |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Complete REST API reference |
| [RASPBERRY_PI_GUIDE.md](RASPBERRY_PI_GUIDE.md) | Pi-specific setup & deployment |
| [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md) | Complete operations guide |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Step-by-step deployment |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute getting started |

---

## 🐛 Troubleshooting

### Common Issues

**"No display" error**
```bash
# Use API or CLI instead of GUI
python app.py api    # REST API
python app.py cli    # Command-line
```

**Camera not detected**
```bash
# Check device
ls /dev/video*

# Test
python3 app.py cli capture
```

**Slow OCR**
```bash
# Switch to Tesseract in config/settings.json
"ocr": { "engine": "tesseract" }
```

**Out of memory**
```bash
# Check usage
free -h

# Restart service
sudo systemctl restart ai-document-reader
```

---

## 🔐 Security

### Important Security Steps

1. **Change API Key**
   ```bash
   # Edit app_api.py
   API_KEY = "your-secure-key"
   ```

2. **Enable Firewall**
   ```bash
   sudo ufw enable
   sudo ufw allow 5000/tcp
   ```

3. **Setup HTTPS**
   ```bash
   # See OPERATIONS_MANUAL.md for SSL setup
   ```

4. **Regular Backups**
   ```bash
   tar -czf backup-$(date +%Y%m%d).tar.gz data/
   ```

---

## 📈 Scalability

### Single Instance
- 5,000-10,000 documents
- 10-50 concurrent users
- ~512MB memory

### Multiple Instances
```bash
# Run load-balanced setup
docker-compose up --scale api=3

# Or with nginx reverse proxy
# See nginx_config.conf
```

---

## 🆚 Comparison: Modes

| Feature | GUI | API | CLI |
|---------|-----|-----|-----|
| Display Required | ✓ | ✗ | ✗ |
| Remote Access | ✗ | ✓ | ✗ |
| Web Dashboard | ✗ | ✓ | ✗ |
| Automation | ✗ | ✓ | ✓ |
| Performance | Good | Best | Medium |
| Ease of Use | Easiest | Easy | Medium |

---

## 💾 Dependencies

### Core Libraries
- **Python 3.10+**: Runtime
- **OpenCV 4.8+**: Computer vision
- **PaddleOCR 2.7+**: Primary OCR
- **pytesseract 0.3+**: Fallback OCR
- **SQLite3**: Database
- **Flask 2.3+**: REST API

### Optional
- **Ollama**: Local LLM
- **Nginx**: Reverse proxy
- **Docker**: Containerization

Full list: See `requirements.txt`

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📞 Support

- **Documentation**: See docs/ folder
- **Issues**: GitHub Issues
- **Email**: support@example.com
- **Discussions**: GitHub Discussions

---

## 🎓 Learning Resources

### For Beginners
- Start with GUI mode: `python app.py`
- Explore API with curl: `curl http://localhost:5000/api/health`
- Read QUICKSTART.md

### For Raspberry Pi
- Follow RASPBERRY_PI_GUIDE.md
- Run: `bash setup_raspberry_pi.sh`
- Access web interface at pi-ip:5000

### For Developers
- See OPERATIONS_MANUAL.md
- Review API_DOCUMENTATION.md
- Check source code comments

---

## 🗺️ Roadmap

### v1.1 (Q2 2024)
- [ ] GPU acceleration support
- [ ] Multiple camera support
- [ ] Advanced UI improvements
- [ ] Enhanced AI models

### v1.2 (Q3 2024)
- [ ] Cloud sync option
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Batch processing

### v2.0 (Q4 2024)
- [ ] Distributed processing
- [ ] Real-time collaboration
- [ ] Advanced security
- [ ] Enterprise features

---

## 📝 Changelog

### v1.0.0 (2024-01-15)
- ✨ Initial release
- ✅ Raspberry Pi support
- ✅ REST API server
- ✅ Multi-mode operation
- ✅ Full documentation

---

## 🙏 Acknowledgments

- OpenCV community
- PaddleOCR team
- Tesseract community
- CustomTkinter developers
- Flask team

---

## 📊 Project Statistics

- **Total Files**: 39+
- **Lines of Code**: 4,500+
- **Documentation Pages**: 5+
- **Supported Formats**: 5+ (PDF, DOCX, TXT, MD, JSON)
- **Supported Languages**: 5+ (EN, SW, FR, AR, ES)
- **OCR Engines**: 2 (PaddleOCR, Tesseract)

---

## 🎯 Quick Links

- [API Documentation](API_DOCUMENTATION.md)
- [Raspberry Pi Guide](RASPBERRY_PI_GUIDE.md)
- [Operations Manual](OPERATIONS_MANUAL.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [Quick Start](QUICKSTART.md)

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2024-01-15  
**Maintained By**: Your Organization

---

## ⭐ Show Your Support

If you found this project helpful, please give it a star! ⭐

```bash
# Quick start
git clone https://github.com/yourusername/offline-ai-reader.git
cd offline-ai-reader
pip install -r requirements.txt
python app.py api
```

**Ready to get started?** Check out [QUICKSTART.md](QUICKSTART.md) or run `bash setup_raspberry_pi.sh`!
