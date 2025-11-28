#!/bin/bash
# Update BirdFM on Raspberry Pi
# Run this script on the Pi to update the code without reinstalling

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "======================================"
echo "BirdFM Update Script"
echo "======================================"
echo ""

# Check if services are running
if systemctl is-active --quiet birdfm.service 2>/dev/null; then
    echo "Stopping BirdFM service (requires sudo)..."
    sudo systemctl stop birdfm.service
    RESTART_BIRDFM=true
else
    echo "BirdFM service not running"
    RESTART_BIRDFM=false
fi

if systemctl is-active --quiet birdfm-web.service 2>/dev/null; then
    echo "Stopping BirdFM web service (requires sudo)..."
    sudo systemctl stop birdfm-web.service
    RESTART_WEB=true
else
    echo "BirdFM web service not running"
    RESTART_WEB=false
fi

# Update Python packages if requirements changed
if [ -f "requirements.txt" ]; then
    echo ""
    echo "Updating Python packages..."
    source venv/bin/activate
    pip install --upgrade -r requirements.txt
fi

# Reload systemd if service files changed
SERVICE_UPDATED=false
if [ -f "birdfm.service" ]; then
    echo ""
    echo "Updating BirdFM systemd service (requires sudo)..."
    sudo cp birdfm.service /etc/systemd/system/birdfm.service
    SERVICE_UPDATED=true
fi

if [ -f "birdfm-web.service" ]; then
    echo ""
    echo "Updating web interface systemd service (requires sudo)..."
    sudo cp birdfm-web.service /etc/systemd/system/birdfm-web.service
    SERVICE_UPDATED=true
fi

if [ "$SERVICE_UPDATED" = true ]; then
    sudo systemctl daemon-reload
fi

# Start the services if they were running
if [ "$RESTART_BIRDFM" = true ]; then
    echo ""
    echo "Starting BirdFM service..."
    sudo systemctl start birdfm.service
fi

if [ "$RESTART_WEB" = true ]; then
    echo ""
    echo "Starting BirdFM web service..."
    sudo systemctl start birdfm-web.service
fi

echo ""
echo "✅ Update complete!"
echo ""

# Show status of running services
if [ "$RESTART_BIRDFM" = true ] || [ "$RESTART_WEB" = true ]; then
    echo "Service status:"
    [ "$RESTART_BIRDFM" = true ] && sudo systemctl status birdfm.service --no-pager
    [ "$RESTART_WEB" = true ] && sudo systemctl status birdfm-web.service --no-pager
else
    echo "To start the services:"
    echo "  sudo systemctl start birdfm"
    echo "  sudo systemctl start birdfm-web"
fi
echo ""
