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

# Check if service is running
if systemctl is-active --quiet birdfm.service 2>/dev/null; then
    echo "Stopping BirdFM service (requires sudo)..."
    sudo systemctl stop birdfm.service
    RESTART_SERVICE=true
else
    echo "Service not running"
    RESTART_SERVICE=false
fi

# Update Python packages if requirements changed
if [ -f "requirements.txt" ]; then
    echo ""
    echo "Updating Python packages..."
    source venv/bin/activate
    pip install --upgrade -r requirements.txt
fi

# Reload systemd if service file changed
if [ -f "birdfm.service" ]; then
    echo ""
    echo "Updating systemd service (requires sudo)..."
    sudo cp birdfm.service /etc/systemd/system/birdfm.service
    sudo systemctl daemon-reload
fi

# Start the service if it was running
if [ "$RESTART_SERVICE" = true ]; then
    echo ""
    echo "Starting BirdFM service..."
    sudo systemctl start birdfm.service
    
    echo ""
    echo "✅ Update complete!"
    echo ""
    echo "Service status:"
    sudo systemctl status birdfm.service --no-pager
else
    echo ""
    echo "✅ Update complete!"
    echo ""
    echo "To start the service:"
    echo "  sudo systemctl start birdfm"
fi
echo ""
