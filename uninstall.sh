#!/bin/bash
# BirdFM Uninstallation Script

echo "======================================"
echo "BirdFM Uninstallation Script"
echo "======================================"
echo ""

# Stop the service if running
echo "Stopping BirdFM service..."
sudo systemctl stop birdfm.service 2>/dev/null || echo "Service not running"

# Disable the service
echo "Disabling BirdFM service..."
sudo systemctl disable birdfm.service 2>/dev/null || echo "Service not enabled"

# Remove systemd service file
echo "Removing systemd service file..."
sudo rm -f /etc/systemd/system/birdfm.service

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "BirdFM service removed successfully!"
echo ""
echo "Note: Application files in $(pwd) were NOT removed."
echo "To completely remove BirdFM, delete this directory manually:"
echo "  rm -rf $(pwd)"
echo ""
