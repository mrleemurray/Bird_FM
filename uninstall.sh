#!/bin/bash
# BirdFM Uninstallation Script

echo "======================================"
echo "BirdFM Uninstallation Script"
echo "======================================"
echo ""

# Stop the services if running
echo "Stopping BirdFM services..."
sudo systemctl stop birdfm.service 2>/dev/null || echo "BirdFM service not running"
sudo systemctl stop birdfm-web.service 2>/dev/null || echo "Web service not running"

# Disable the services
echo "Disabling BirdFM services..."
sudo systemctl disable birdfm.service 2>/dev/null || echo "BirdFM service not enabled"
sudo systemctl disable birdfm-web.service 2>/dev/null || echo "Web service not enabled"

# Remove systemd service files
echo "Removing systemd service files..."
sudo rm -f /etc/systemd/system/birdfm.service
sudo rm -f /etc/systemd/system/birdfm-web.service

# Remove sudo permissions file
echo "Removing sudo permissions..."
sudo rm -f /etc/sudoers.d/birdfm-web

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "BirdFM services removed successfully!"
echo ""
echo "Note: Application files in $(pwd) were NOT removed."
echo "To completely remove BirdFM, delete this directory manually:"
echo "  rm -rf $(pwd)"
echo ""
