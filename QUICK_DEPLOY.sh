#!/bin/bash

# Quick Server Deployment Script
# Run this on your server to deploy the voice chat fix

set -e

echo "╔══════════════════════════════════════════════════╗"
echo "║                                                  ║"
echo "║     Deploying Voice Chat Fix to Server          ║"
echo "║                                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Navigate to bot directory
cd /root/anniex || { echo "Error: /root/anniex not found!"; exit 1; }

# Pull latest changes
echo "➜ Pulling latest changes from GitHub..."
git pull origin main

# Restart service
echo "➜ Restarting anniex-ultrafast service..."
sudo systemctl restart anniex-ultrafast

# Check status
echo "➜ Checking service status..."
if sudo systemctl is-active --quiet anniex-ultrafast; then
    echo "✅ Service is running successfully!"
    echo ""
    echo "Service Details:"
    sudo systemctl status anniex-ultrafast --no-pager -l
else
    echo "❌ Service failed to start!"
    echo "Check logs with: sudo journalctl -u anniex-ultrafast -f"
    exit 1
fi

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "To monitor logs, run:"
echo "  sudo journalctl -u anniex-ultrafast -f"
