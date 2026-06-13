#!/usr/bin/env bash
set -euo pipefail

# Non-interactive installer for Raspberry Pi (uses sudo)
# Usage: sudo bash install.sh [--skip-service]

SKIP_SERVICE=0
if [ "${1:-}" = "--skip-service" ]; then
  SKIP_SERVICE=1
fi

echo "Starting non-interactive install..."
export DEBIAN_FRONTEND=noninteractive

echo "[1/6] Updating apt cache"
sudo apt-get update -y
sudo apt-get upgrade -y || true

echo "[2/6] Installing OS packages"
sudo apt-get install -y \
    python3-venv python3-full python3-pip python3-dev build-essential \
    libopenblas-dev liblapack-dev libblas-dev gfortran \
    python3-opencv libopencv-dev libtiff6 libopenjp2-7 libwebp7 \
    tesseract-ocr libtesseract-dev \
    alsa-utils pulseaudio espeak-ng libopus0 libopusfile0 || true

echo "[3/6] Creating project venv"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi

echo "[4/6] Installing Python packages into venv"
"$VENV/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV/bin/pip" install -r "$DIR/requirements.txt" --upgrade || true

echo "[5/6] Ensuring data directories"
mkdir -p "$DIR/data" "$DIR/logs" "$DIR/uploads" "$DIR/images"
chmod 755 "$DIR/data" "$DIR/logs" "$DIR/uploads" "$DIR/images"

if [ "$SKIP_SERVICE" -eq 0 ]; then
  echo "[6/6] Installing systemd service (using run.sh wrapper)"
  if [ -f "$DIR/ai-document-reader.service" ]; then
    sudo cp "$DIR/ai-document-reader.service" /etc/systemd/system/ai-document-reader.service
    sudo systemctl daemon-reload
    sudo systemctl enable --now ai-document-reader || echo "Failed to enable/start service"
  else
    echo "Service file not found in $DIR; skipping service install"
  fi
else
  echo "Skipping service installation as requested"
fi

echo "Install complete. To run manually:"
echo "  $DIR/run.sh"
echo "Or start the service: sudo systemctl status ai-document-reader"
