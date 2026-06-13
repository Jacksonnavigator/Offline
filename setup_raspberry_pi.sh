#!/bin/bash
# Raspberry Pi Setup Script for Portable Offline AI Document Reader
# Run: bash setup_raspberry_pi.sh

set -e

echo "=========================================="
echo "🍓 Raspberry Pi Setup Script"
echo "Portable Offline AI Document Reader"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}⚠️  This script is designed for Raspberry Pi${NC}"
    echo "   Some steps may not work on other systems"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo -e "${GREEN}[1/7] Updating system packages...${NC}"
sudo apt-get update || {
    echo -e "${RED}⚠️  apt-get update failed. Attempting to fix...${NC}"
    sudo apt-get clean
    sudo apt-get update
}
sudo apt-get upgrade -y || echo -e "${YELLOW}⚠️  Some packages could not be upgraded${NC}"

# Install system dependencies
echo -e "${GREEN}[2/7] Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libopenblas-dev \
    libopenblas0 \
    liblapack-dev \
    libblas-dev \
    gfortran \
    python3-numpy \
    python3-scipy \
    libatlas3-base \
    libtiff6 \
    libopenjp2-7 \
    libwebp7 \
    libharfbuzz0b \
    python3-opencv \
    python3-pil \
    libopencv-dev

# Install Tesseract OCR with ALL available language packs
echo -e "${GREEN}[3/7] Installing Tesseract OCR with all languages...${NC}"
echo "    Installing: English, Swahili, French, Arabic, Spanish, German,"
echo "    Chinese, Japanese, Korean, Russian, Portuguese, Dutch, Polish, Thai,"
echo "    Vietnamese, Hindi, Bengali, Turkish, Hebrew, and 100+ more languages"
sudo apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-all \
    libtesseract-dev || {
        echo -e "${YELLOW}⚠️  Some tesseract packages may not be available on this system${NC}"
        echo "    Installing base tesseract OCR..."
        sudo apt-get install -y tesseract-ocr libtesseract-dev || true
    }

# Install optional camera support
echo -e "${GREEN}[4/7] Installing camera libraries...${NC}"
sudo apt-get install -y \
    libopencv-dev \
    libopencv4.5-dev || true

# Install audio and text-to-speech support
echo -e "${GREEN}[4b/7] Installing audio and TTS libraries...${NC}"
sudo apt-get install -y \
    alsa-utils \
    pulseaudio \
    espeak-ng \
    libopus0 \
    libopusfile0 || {
        echo -e "${YELLOW}⚠️  Some audio packages may not be available${NC}"
        echo "    Installing essential audio packages..."
        sudo apt-get install -y alsa-utils espeak-ng || true
    }

# Install Python packages inside a virtual environment
echo -e "${GREEN}[5/7] Preparing Python virtual environment and installing packages...${NC}"
# Ensure venv support and full Python available
sudo apt-get install -y python3-venv python3-full || echo -e "${YELLOW}Could not install python3-venv/python3-full; proceeding if venv exists${NC}"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment at ./venv"
    python3 -m venv venv
fi

echo "Installing Python packages into ./venv"
./venv/bin/python -m pip install --upgrade pip setuptools wheel
./venv/bin/pip install -r requirements.txt --upgrade

# Install TTS voice models (will download automatically on first use)
echo -e "${GREEN}[5b/7] Setting up text-to-speech voices (using venv python)...${NC}"
mkdir -p ~/.local/share/piper-tts/voices
./venv/bin/python -c "import piper; print('Piper TTS ready')" 2>/dev/null || echo "Piper will download voices on first use"

# Create data directory
echo -e "${GREEN}[6/7] Creating data directories...${NC}"
mkdir -p data
mkdir -p logs
mkdir -p uploads
mkdir -p images
chmod 755 data logs uploads images

# Setup systemd service (optional)
echo -e "${GREEN}[7/7] Setting up systemd service...${NC}"
read -p "Setup systemd service for auto-start? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo bash setup_service.sh
fi

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Test the application:"
echo "   python3 app.py api"
echo ""
echo "2. Access web interface:"
echo "   http://localhost:5000"
echo ""
echo "3. For command-line mode:"
echo "   python3 app.py cli --help"
echo ""
echo "4. For interactive mode:"
echo "   python3 app.py interactive"
echo ""
echo "To enable auto-start on boot:"
echo "   sudo systemctl enable ai-document-reader"
echo "   sudo systemctl start ai-document-reader"
