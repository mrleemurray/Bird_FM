#!/bin/bash
# BirdFM Installation Script for Raspberry Pi
# Run this script on your Raspberry Pi to install and configure BirdFM

set -e  # Exit on error

echo "======================================"
echo "BirdFM Installation Script"
echo "======================================"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null && ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Installing in: $SCRIPT_DIR"
echo ""

# Update system packages
echo "Updating system packages..."
sudo apt-get update

# Install required system packages
echo ""
echo "Installing system dependencies..."
sudo apt-get install -y python3 python3-pip python3-venv mpg123 ffmpeg git

# Install audio dependencies
echo ""
echo "Installing audio dependencies..."
sudo apt-get install -y alsa-utils pulseaudio

# Create Python virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
fi

# Activate virtual environment and install Python packages
echo ""
echo "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Check if config.json exists
echo ""
if [ ! -f "config.json" ]; then
    echo "Config file not found. Creating from example..."
    if [ -f "config.json.example" ]; then
        cp config.json.example config.json
        echo "Created config.json from example"
        echo "⚠️  IMPORTANT: Edit config.json and add your Xeno-Canto API key!"
    else
        echo "Creating minimal config.json..."
        echo '{"api_key": "YOUR_API_KEY_HERE"}' > config.json
        echo "⚠️  IMPORTANT: Edit config.json and add your Xeno-Canto API key!"
    fi
else
    echo "config.json already exists"
fi

# Check if countries.json exists
if [ ! -f "countries.json" ]; then
    echo "Creating default countries.json..."
    cat > countries.json << 'EOF'
{
    "countries": [
        "United Kingdom",
        "United States",
        "Australia"
    ]
}
EOF
    echo "Created countries.json with default countries"
fi

# Create cache directory
echo ""
echo "Creating cache directory..."
mkdir -p cache

# Create log directory
mkdir -p logs

# Install systemd service
echo ""
echo "Installing systemd service..."

# Create systemd service file
sudo tee /etc/systemd/system/birdfm.service > /dev/null << EOF
[Unit]
Description=BirdFM - Xeno-Canto Bird Sound Player
After=network-online.target sound.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/venv/bin/python $SCRIPT_DIR/BirdFM.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/logs/birdfm.log
StandardError=append:$SCRIPT_DIR/logs/birdfm-error.log

# Environment variables
Environment="PYTHONUNBUFFERED=1"

# Restart policy
StartLimitInterval=200
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF

echo "Systemd service created at /etc/systemd/system/birdfm.service"

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
echo ""
echo "Enabling BirdFM service to start on boot..."
sudo systemctl enable birdfm.service

# Test audio output
echo ""
echo "Testing audio configuration..."
if command -v speaker-test &> /dev/null; then
    echo "Audio test available. You can test speakers with: speaker-test -t wav -c 2"
fi

# Set audio output to headphone jack (for Raspberry Pi)
if command -v amixer &> /dev/null; then
    echo "Setting audio output to headphone jack..."
    amixer cset numid=3 1 2>/dev/null || echo "Could not set audio output (this is normal on some systems)"
fi

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Edit config.json and add your Xeno-Canto API key"
echo "   nano config.json"
echo ""
echo "2. (Optional) Edit countries.json to customize bird locations"
echo "   nano countries.json"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl start birdfm"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status birdfm"
echo ""
echo "5. View logs:"
echo "   tail -f logs/birdfm.log"
echo "   tail -f birdfm.log"
echo ""
echo "Useful commands:"
echo "  sudo systemctl stop birdfm     # Stop the service"
echo "  sudo systemctl restart birdfm  # Restart the service"
echo "  sudo systemctl disable birdfm  # Disable auto-start"
echo ""
echo "The service will automatically:"
echo "  - Start on system boot"
echo "  - Restart on crash (with 10 second delay)"
echo "  - Recover from errors"
echo ""
