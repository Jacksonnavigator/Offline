# Raspberry Pi Deployment Checklist

## Pre-Deployment

- [ ] Hardware ready
  - [ ] Raspberry Pi 5 or Pi 4 (8GB RAM recommended)
  - [ ] USB Camera
  - [ ] Power supply (5A USB-C for Pi 5)
  - [ ] Network cable or WiFi configured
  - [ ] Optional: External SSD via USB 3.0

- [ ] OS installed
  - [ ] Raspberry Pi OS Lite (latest Bookworm)
  - [ ] System updated: `sudo apt-get update && upgrade`
  - [ ] SSH enabled and working
  - [ ] Network configured

- [ ] Source code ready
  - [ ] Application files downloaded/cloned
  - [ ] requirements.txt verified
  - [ ] Configuration templates ready

---

## Installation Phase

- [ ] Run setup script
  - [ ] `chmod +x setup_raspberry_pi.sh`
  - [ ] `bash setup_raspberry_pi.sh`
  - [ ] All packages installed successfully
  - [ ] No errors in output

- [ ] Verify installation
  - [ ] `python3 --version` → 3.10+
  - [ ] `pip3 list | grep flask` → flask 2.3+
  - [ ] `pip3 list | grep opencv` → opencv-python 4.8+
  - [ ] `tesseract --version` → tesseract-ocr installed

- [ ] Test basic functionality
  - [ ] `python3 app.py api` → starts without errors
  - [ ] Access `http://localhost:5000` in browser
  - [ ] Dashboard loads successfully
  - [ ] Stop server: `Ctrl+C`

---

## Configuration Phase

- [ ] Update API key
  - [ ] Edit `app_api.py`
  - [ ] Change `API_KEY = "your-api-key-change-me"` to secure key
  - [ ] Save and verify

- [ ] Configure camera
  - [ ] Connect USB camera
  - [ ] Run: `lsusb | grep -i camera`
  - [ ] Update `config/settings.json` if needed
  - [ ] Test camera: `python3 app.py cli capture`

- [ ] Configure storage
  - [ ] Check disk space: `df -h`
  - [ ] If using SSD: Mount external drive
  - [ ] Update `config/settings.json` storage paths if needed
  - [ ] Verify write permissions on data directory

- [ ] Network configuration
  - [ ] Find Pi's IP: `hostname -I`
  - [ ] Ping from another device: `ping <pi-ip>`
  - [ ] Test remote access: `curl http://<pi-ip>:5000/api/health`

---

## Systemd Service Setup (Optional)

- [ ] Create service
  - [ ] `sudo bash setup_service.sh`
  - [ ] Verify service created: `sudo systemctl status ai-document-reader`

- [ ] Enable auto-start
  - [ ] `sudo systemctl enable ai-document-reader`
  - [ ] Verify enabled: `sudo systemctl is-enabled ai-document-reader`

- [ ] Start service
  - [ ] `sudo systemctl start ai-document-reader`
  - [ ] Check status: `sudo systemctl status ai-document-reader`
  - [ ] View logs: `sudo journalctl -u ai-document-reader -n 20`

- [ ] Test auto-start
  - [ ] Reboot: `sudo reboot`
  - [ ] Wait 30 seconds
  - [ ] Verify running: `sudo systemctl status ai-document-reader`
  - [ ] Test API: `curl http://localhost:5000/api/health`

---

## Testing Phase

- [ ] Web interface
  - [ ] Open `http://<pi-ip>:5000` in browser
  - [ ] Dashboard loads
  - [ ] Navigation works
  - [ ] Stats display correctly

- [ ] Document scanning
  - [ ] Upload test image via web interface
  - [ ] Wait for OCR completion
  - [ ] Verify text extracted
  - [ ] Check document in list

- [ ] Command-line interface
  - [ ] Test help: `python3 app.py cli --help`
  - [ ] List documents: `python3 app.py cli list`
  - [ ] Search: `python3 app.py cli search test`
  - [ ] Get stats: `python3 app.py cli stats`

- [ ] API endpoints
  - [ ] Health: `curl -H "X-API-Key: KEY" http://localhost:5000/api/health`
  - [ ] Documents: `curl -H "X-API-Key: KEY" http://localhost:5000/api/documents`
  - [ ] Search: `curl -H "X-API-Key: KEY" "http://localhost:5000/api/search?q=test"`

- [ ] Camera functionality
  - [ ] Capture from camera: `python3 app.py cli capture --title "Test"`
  - [ ] Verify image saved
  - [ ] Check OCR processed correctly

- [ ] Database
  - [ ] Check file size: `ls -lh data/documents.db`
  - [ ] Verify data integrity: `sqlite3 data/documents.db "SELECT COUNT(*) FROM documents;"`

---

## Performance Tuning

- [ ] Memory optimization
  - [ ] Check usage: `free -h`
  - [ ] Monitor processes: `top -b -n 1 | head`
  - [ ] Adjust memory limits if needed in systemd service

- [ ] OCR optimization
  - [ ] If slow, switch to Tesseract in config.json
  - [ ] Reduce image resolution if needed
  - [ ] Enable image caching

- [ ] Database optimization
  - [ ] Rebuild indexes: `sqlite3 data/documents.db "ANALYZE;"`
  - [ ] Vacuum: `sqlite3 data/documents.db "VACUUM;"`

- [ ] System optimization
  - [ ] Disable unnecessary services
  - [ ] Reduce GPU memory if not needed
  - [ ] Enable swap for larger databases

---

## Security Hardening

- [ ] API security
  - [ ] Change default API key ✅ (done earlier)
  - [ ] Use HTTPS in production
  - [ ] Setup firewall: `sudo ufw enable`
  - [ ] Allow only needed ports: `sudo ufw allow 5000/tcp`

- [ ] System security
  - [ ] Change default Pi password
  - [ ] Disable SSH password login
  - [ ] Setup SSH keys instead
  - [ ] Run: `sudo apt-get install fail2ban`

- [ ] Data security
  - [ ] Backup regularly
  - [ ] Test restore process
  - [ ] Encrypt sensitive data if needed

- [ ] Network security
  - [ ] Hide behind reverse proxy (see nginx_config.conf)
  - [ ] Use SSL/TLS certificates
  - [ ] Implement rate limiting
  - [ ] Setup DDoS protection if public

---

## Backup & Disaster Recovery

- [ ] Backup strategy
  - [ ] Create backup directory
  - [ ] Backup command: `tar -czf backup-$(date +%Y%m%d).tar.gz data/ config/`
  - [ ] Store on external drive
  - [ ] Test restore: `tar -xzf backup-20240115.tar.gz`

- [ ] Documentation
  - [ ] Document Pi hostname
  - [ ] Document IP address
  - [ ] Document API key (secure location)
  - [ ] Document custom configurations

---

## Monitoring & Maintenance

- [ ] Health monitoring
  - [ ] Setup monitoring script
  - [ ] Monitor disk space regularly
  - [ ] Monitor memory usage
  - [ ] Check error logs weekly

- [ ] Regular tasks
  - [ ] Weekly: `sudo apt-get update && upgrade`
  - [ ] Monthly: Full database backup
  - [ ] Quarterly: System health check
  - [ ] Annually: OS upgrade

- [ ] Log management
  - [ ] Monitor: `sudo journalctl -u ai-document-reader -f`
  - [ ] Cleanup old logs: `sudo journalctl --vacuum=30d`
  - [ ] Archive: Backup logs monthly

---

## Post-Deployment

- [ ] Documentation
  - [ ] Record Pi's IP address
  - [ ] Document any custom configurations
  - [ ] Save API key in secure location
  - [ ] Create access instructions

- [ ] User access
  - [ ] Provide access instructions
  - [ ] Test from client devices
  - [ ] Provide API documentation link
  - [ ] Setup authentication if needed

- [ ] Support
  - [ ] Create support contacts list
  - [ ] Document troubleshooting steps
  - [ ] Setup monitoring/alerts
  - [ ] Plan backup recovery procedures

---

## Final Verification

- [ ] All systems operational
  - [ ] Web interface accessible ✅
  - [ ] API responding ✅
  - [ ] Database connected ✅
  - [ ] Camera working ✅
  - [ ] Service auto-starts ✅

- [ ] Performance acceptable
  - [ ] API response <500ms ✅
  - [ ] OCR completes in reasonable time ✅
  - [ ] Memory usage stable ✅
  - [ ] Disk usage growing normally ✅

- [ ] Security measures in place
  - [ ] API key changed ✅
  - [ ] Firewall enabled ✅
  - [ ] Backups automated ✅
  - [ ] Monitoring active ✅

---

## Deployment Sign-Off

- [ ] **Deployer**: ________________________  **Date**: ________
- [ ] **Verified by**: ____________________  **Date**: ________
- [ ] **Approved by**: ___________________  **Date**: ________

---

## Contact Information

- **System Administrator**: 
- **Support Email**: 
- **Emergency Contact**: 
- **Backup Location**: 

---

## Additional Notes

```
[Space for deployment-specific notes, issues encountered, customizations made]




```

---

**Last Updated**: 2024-01-15  
**Template Version**: 1.0.0
