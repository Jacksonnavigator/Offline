#!/bin/bash
# Systemd Service Setup for Auto-Start on Boot
# Run: sudo bash setup_service.sh

set -e

echo "Setting up systemd service for AI Document Reader..."

SERVICE_NAME="ai-document-reader"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER=${SUDO_USER:-$(whoami)}

# Create systemd service file
echo "Creating service file: ${SERVICE_FILE}"
[ -x "${APP_DIR}/venv/bin/python" ] && PYTHON_EXEC="${APP_DIR}/venv/bin/python" || PYTHON_EXEC="/usr/bin/python3"

echo "Using python executable: ${PYTHON_EXEC}"

sudo tee ${SERVICE_FILE} > /dev/null <<EOF
[Unit]
Description=Portable Offline AI Document Reader
Documentation=https://github.com/yourusername/offline-ai-reader
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${PYTHON_EXEC} ${APP_DIR}/app.py api
Restart=on-failure
RestartSec=30
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-doc-reader

# Performance optimizations
Nice=10
MemoryLimit=512M
CPUQuota=75%

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable and start the service now
echo "Enabling and starting ${SERVICE_NAME}..."
sudo systemctl enable --now ${SERVICE_NAME} || echo "Failed to enable/start ${SERVICE_NAME}. Check systemctl status for details."
echo "Service status:"
sudo systemctl status ${SERVICE_NAME} --no-pager || true

echo ""
echo "✅ Service setup complete!"
echo ""
echo "Available commands:"
echo "  sudo systemctl start ${SERVICE_NAME}     - Start service"
echo "  sudo systemctl stop ${SERVICE_NAME}      - Stop service"
echo "  sudo systemctl restart ${SERVICE_NAME}   - Restart service"
echo "  sudo systemctl status ${SERVICE_NAME}    - Check status"
echo "  sudo systemctl enable ${SERVICE_NAME}    - Enable auto-start on boot"
echo "  sudo systemctl disable ${SERVICE_NAME}   - Disable auto-start"
echo ""
echo "View logs:"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "To enable auto-start now:"
echo "  sudo systemctl enable ${SERVICE_NAME}"
echo "  sudo systemctl start ${SERVICE_NAME}"
