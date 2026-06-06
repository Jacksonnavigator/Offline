# Quick Start Guide

## Portable Offline AI Document Reader - Get Started in 5 Minutes

---

## Prerequisites

- Python 3.12 or higher
- At least 2GB RAM free
- 2GB disk space
- USB webcam (for scanning)
- Optional: Ollama installed for AI features

---

## 1️⃣ Installation (2 minutes)

### Windows
```bash
# Clone or download the project
cd offline

# Run automatic setup
python setup.py

# Activate virtual environment
venv\Scripts\activate
```

### Linux / Raspberry Pi
```bash
# Clone or download the project
cd offline

# Run automatic setup
python3 setup.py

# Activate virtual environment
source venv/bin/activate
```

---

## 2️⃣ Start Application (30 seconds)

```bash
python app.py
```

The application window will open in approximately 3-5 seconds.

---

## 3️⃣ First Scan (2 minutes)

1. **Attach USB Webcam**: Connect your camera to computer
2. **Click "Scan Document"** in main menu
3. **Click "Start Camera"** button
4. **Position your document** in the preview
5. **Click "Capture"** when document is detected
6. **Review OCR text** in results panel
7. **Click "Save Document"** to store

✅ Document saved! You can now search it.

---

## 4️⃣ Optional: Enable AI Features

### Install Ollama (for AI Assistant)

1. Download from https://ollama.ai
2. Run installer and start Ollama
3. Download model: `ollama run neural-chat`
4. Return to app, click "AI Assistant"
5. Select a document and ask questions

### Verify Ollama is Running
```bash
curl http://localhost:11434/api/tags
```

---

## 5️⃣ Common Tasks

### Scan Multiple Documents
- Repeat steps in "First Scan" above
- Each document is automatically saved

### Search Documents
1. Click "Search" in menu
2. Enter search term
3. Press Enter or click "Search"
4. Click result to preview

### Export Document
1. Click "Documents" in menu
2. Find document in list
3. Click document (or use search)
4. Look for export option
5. Choose format (TXT, PDF, DOCX)

### Ask AI Questions
1. Click "AI Assistant"
2. Select document from dropdown
3. Click "Load"
4. Type your question
5. Press Enter
6. AI responds based on document

### Change Settings
1. Click "Settings"
2. Modify desired settings (Theme, Language, OCR Engine, etc.)
3. Click "Save Settings"

---

## Configuration

Edit `config/settings.json` to customize:

```json
{
  "camera": {
    "device_id": 0
  },
  "ocr": {
    "engine": "paddle"
  },
  "ai": {
    "ollama_base_url": "http://localhost:11434",
    "model_name": "neural-chat"
  }
}
```

---

## Troubleshooting Quick Fixes

### Camera Not Working
- Check USB connection
- Try changing `device_id` in settings: 0, 1, or 2
- Run: `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`

### OCR Not Working
- Ensure PaddleOCR downloaded (first run auto-downloads)
- Check: `python -c "from paddleocr import PaddleOCR; print('OK')"`

### AI Not Responding
- Verify Ollama running: `curl http://localhost:11434/api/tags`
- Start Ollama: `ollama serve`
- Model exists: `ollama run neural-chat`

### No Documents Found
- Scan at least one document first using "Scan Document" menu
- Wait for OCR to complete
- Check database isn't corrupted: `rm data/documents.db*`

---

## Next: Full Features

- See README.md for complete documentation
- See PROJECT_COMPLETION.md for feature list
- See tests/ for code usage examples

---

## Need Help?

1. **Check logs**: Look in `logs/app.log`
2. **Read docs**: See README.md section "Troubleshooting"
3. **Review code**: Each module has detailed docstrings
4. **Run tests**: `pytest tests/ -v`

---

## What's Next?

After your first scan:

1. **Explore AI Features**: Ask questions about scanned documents
2. **Build Executable**: Run `python build.py --onedir`
3. **Deploy to Raspberry Pi**: Follow README.md "Deployment to Raspberry Pi"
4. **Customize UI**: Edit `ui/*.py` screens
5. **Add Languages**: Add to `config/settings.json`

---

**Happy scanning! 🎉**

**Questions?** Check README.md for comprehensive documentation.

**Found an issue?** Check PROJECT_COMPLETION.md for known limitations.
