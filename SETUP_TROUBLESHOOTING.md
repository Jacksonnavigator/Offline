# Setup Script Troubleshooting Guide

## Common Installation Issues & Solutions

### Issue 1: "Package 'libatlas-base-dev' has no installation candidate"

**Solution**: This is normal on Raspberry Pi OS Bookworm (Debian 12). The script has been updated to use:
- `libopenblas-dev` instead of `libatlas-base-dev`
- `libopenblas0` for the library
- `libatlas3-base` as a compatibility package

**Status**: ✅ FIXED in latest setup script

---

### Issue 2: "Unable to locate package libjasper-dev"

**Solution**: Jasper library was removed from Debian 12 (Bookworm). Not needed for modern image processing with OpenCV.

The script now uses:
- `python3-opencv` (replaces direct jasper dependency)
- `python3-pil` (for image manipulation)
- `libtiff6` instead of `libtiff5` or `libtiff-dev`

**Status**: ✅ FIXED in latest setup script

---

### Issue 3: "Unable to locate package libwebp6"

**Solution**: Package renamed to `libwebp7` in newer Debian versions.

**Status**: ✅ FIXED in latest setup script

---

### Issue 4: Tesseract all languages not available

**Solution**: The script now has error handling. If `tesseract-ocr-all` fails:
1. It will attempt to install base tesseract-ocr
2. Falls back to what's available
3. Installation continues (doesn't stop entire setup)

**What you can do manually**:
```bash
# Install just base tesseract
sudo apt-get install tesseract-ocr libtesseract-dev

# Then install individual languages you need
sudo apt-get install tesseract-ocr-eng tesseract-ocr-fra tesseract-ocr-ara
```

**Status**: ✅ Automatic fallback added

---

### Issue 5: Audio packages not available

**Solution**: Script now has fallback for audio packages. Essential ones will still be installed:
- `alsa-utils` (audio utilities)
- `espeak-ng` (text-to-speech)

Less critical packages like `pulseaudio`, `libopus0` will skip if not available.

**Status**: ✅ Fallback added

---

## Quick Recovery Steps

If setup fails partway through:

### Step 1: Clean and Update
```bash
sudo apt-get clean
sudo apt-get update
sudo apt-get fix-missing
```

### Step 2: Try Again
```bash
bash setup_raspberry_pi.sh
```

### Step 3: Manual Install (if needed)
```bash
# Core essentials only
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    python3-opencv \
    tesseract-ocr \
    alsa-utils

# Then install Python packages
pip3 install -r requirements.txt
```

---

## Verify Installation

After setup completes, verify key components:

```bash
# Check Python
python3 --version

# Check OCR
tesseract --version

# Check OpenCV
python3 -c "import cv2; print(cv2.__version__)"

# Check pip packages
pip3 list | grep -E "flask|opencv|paddleocr"

# Check tesseract languages
tesseract --list-langs

# Test audio (optional)
speaker-test -t wav -c 2 -l 1 &
sleep 2
pkill speaker-test
```

---

## OS Compatibility

### ✅ Tested & Working
- Raspberry Pi OS Bookworm (Debian 12)
- Ubuntu 22.04 LTS
- Debian 12 Bookworm

### ⚠️ Known Issues
- **Bullseye or older**: Some packages may need manual installation
- **Other Linux distros**: May have different package names

### What to do if OS is older:
```bash
# Check current Debian version
cat /etc/debian_version

# For older systems, manually install core packages:
sudo apt-get install -y python3-pip python3-dev tesseract-ocr

# Then install Python packages
pip3 install -r requirements.txt
```

---

## Clean Uninstall (if needed)

If you need to start fresh:

```bash
# Remove Tesseract
sudo apt-get remove -y tesseract-ocr tesseract-ocr-eng

# Remove other packages
sudo apt-get autoremove -y
sudo apt-get clean

# Clean Python packages
pip3 uninstall -y -r requirements.txt

# Remove application
rm -rf ~/offline-ai-reader
```

---

## Alternative: Docker Installation

If native installation is problematic, use Docker:

```bash
# Install Docker
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker pi

# Run application
docker-compose up
```

---

## Getting Help

If issues persist:

1. **Check logs**:
   ```bash
   tail -f logs/app.log
   ```

2. **Check service status**:
   ```bash
   sudo systemctl status ai-document-reader
   sudo journalctl -u ai-document-reader -f
   ```

3. **Manual verification**:
   ```bash
   python3 app.py api
   ```

4. **Check available packages**:
   ```bash
   apt-cache search tesseract
   apt-cache search libopenblas
   ```

---

## Package Mapping (Old → New)

| Old Package | New Package | Reason |
|-------------|------------|--------|
| libatlas-base-dev | libopenblas-dev | Modern replacement |
| libjasper-dev | (removed) | Not needed with modern OpenCV |
| libwebp6 | libwebp7 | Version update for Debian 12 |
| libtiff-dev | libtiff6 | Version update for Debian 12 |
| python3-matplotlib | (removed) | Not core requirement |

---

**Last Updated**: 2026-06-09  
**Status**: All common issues addressed with fallbacks
