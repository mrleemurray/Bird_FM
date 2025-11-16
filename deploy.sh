#!/bin/bash
# Deploy BirdFM to Raspberry Pi
# Run this script from your local machine to deploy to the Pi
# Usage: ./deploy.sh [username] [hostname] [password]
# Example: ./deploy.sh pi raspberrypi.local mypassword

set -e

# Configuration - use arguments or environment variables, no defaults with personal info
PI_USER="${1:-${PI_USER}}"
PI_HOST="${2:-${PI_HOST}}"
PI_PASSWORD="${3:-${PI_PASSWORD}}"

if [ -z "$PI_USER" ] || [ -z "$PI_HOST" ]; then
    echo "Usage: $0 <username> <hostname> [password]"
    echo "Example: $0 pi raspberrypi.local mypassword"
    echo ""
    echo "Or set environment variables:"
    echo "  PI_USER=pi PI_HOST=raspberrypi.local PI_PASSWORD=secret $0"
    exit 1
fi

PI_PATH="${PI_PATH:-/home/$PI_USER/BirdFM}"

echo "======================================"
echo "BirdFM Deployment Script"
echo "======================================"
echo ""
echo "Deploying to: $PI_USER@$PI_HOST:$PI_PATH"
echo ""

# Setup sshpass if password provided
SSH_CMD="ssh"
RSYNC_CMD="rsync"
if [ -n "$PI_PASSWORD" ]; then
    if ! command -v sshpass &> /dev/null; then
        echo "⚠️  Password provided but 'sshpass' not installed."
        echo "Install with: brew install hudochenkov/sshpass/sshpass"
        echo "Or use SSH keys for passwordless authentication."
        echo ""
    else
        SSH_CMD="sshpass -p '$PI_PASSWORD' ssh"
        RSYNC_CMD="sshpass -p '$PI_PASSWORD' rsync"
        export SSHPASS="$PI_PASSWORD"
    fi
fi

# Check if we can reach the Pi
echo "Testing connection to Raspberry Pi..."
if [ -n "$PI_PASSWORD" ] && command -v sshpass &> /dev/null; then
    if ! sshpass -p "$PI_PASSWORD" ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "$PI_USER@$PI_HOST" "echo 'Connection successful'" 2>/dev/null; then
        echo "❌ Cannot connect to $PI_HOST"
        echo "Please check credentials and network connection"
        exit 1
    fi
else
    if ! ssh -o ConnectTimeout=5 "$PI_USER@$PI_HOST" "echo 'Connection successful'"; then
        echo "❌ Cannot connect to $PI_HOST"
        echo "Please check:"
        echo "  - The Pi is powered on and connected to network"
        echo "  - SSH is enabled on the Pi"
        echo "  - The hostname/IP is correct"
        exit 1
    fi
fi

echo "✅ Connection successful"
echo ""

# Create directory on Pi if it doesn't exist
echo "Creating directory on Pi..."
if [ -n "$PI_PASSWORD" ] && command -v sshpass &> /dev/null; then
    sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no "$PI_USER@$PI_HOST" "mkdir -p $PI_PATH"
else
    ssh "$PI_USER@$PI_HOST" "mkdir -p $PI_PATH"
fi

# Copy files to Pi (excluding venv, cache, logs, and git)
echo "Copying files to Pi..."
if [ -n "$PI_PASSWORD" ] && command -v sshpass &> /dev/null; then
    sshpass -p "$PI_PASSWORD" rsync -avz --progress \
        -e "ssh -o StrictHostKeyChecking=no" \
        --exclude 'venv/' \
        --exclude 'cache/' \
        --exclude 'logs/' \
        --exclude '.git/' \
        --exclude '*.pyc' \
        --exclude '__pycache__/' \
        --exclude '.DS_Store' \
        --exclude 'birdfm.log' \
        --exclude 'birdfm-error.log' \
        ./ "$PI_USER@$PI_HOST:$PI_PATH/"
else
    rsync -avz --progress \
        --exclude 'venv/' \
        --exclude 'cache/' \
        --exclude 'logs/' \
        --exclude '.git/' \
        --exclude '*.pyc' \
        --exclude '__pycache__/' \
        --exclude '.DS_Store' \
        --exclude 'birdfm.log' \
        --exclude 'birdfm-error.log' \
        ./ "$PI_USER@$PI_HOST:$PI_PATH/"
fi

echo ""
echo "✅ Files copied successfully"
echo ""

# Ask if user wants to run installation
read -p "Run installation script on Pi? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running installation on Pi..."
    if [ -n "$PI_PASSWORD" ] && command -v sshpass &> /dev/null; then
        sshpass -p "$PI_PASSWORD" ssh -o StrictHostKeyChecking=no -t "$PI_USER@$PI_HOST" "cd $PI_PATH && chmod +x install.sh && ./install.sh"
    else
        ssh -t "$PI_USER@$PI_HOST" "cd $PI_PATH && chmod +x install.sh && ./install.sh"
    fi
    
    echo ""
    echo "======================================"
    echo "Deployment Complete!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "1. SSH into your Pi:"
    echo "   ssh $PI_USER@$PI_HOST"
    echo ""
    echo "2. Add your API key to config.json:"
    echo "   cd $PI_PATH"
    echo "   nano config.json"
    echo ""
    echo "3. Start the service:"
    echo "   sudo systemctl start birdfm"
    echo ""
else
    echo ""
    echo "Skipping installation. To install manually:"
    echo "  ssh $PI_USER@$PI_HOST"
    echo "  cd $PI_PATH"
    echo "  ./install.sh"
    echo ""
fi
