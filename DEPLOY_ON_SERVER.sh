#!/bin/bash

# Remote Server Deployment Script
# This script will be uploaded to server and executed for deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║     ANNIEMUSIC Bot - Voice Chat Fix Deployment       ║${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${YELLOW}➜ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

cd /root/anniex || { print_error "Directory /root/anniex not found!"; exit 1; }

print_status "Pulling latest changes from GitHub..."
git pull origin main

print_success "Git pull completed!"

print_status "Checking current service status..."
if systemctl is-active --quiet anniex-ultrafast; then
    print_status "Service is currently running"
else
    print_status "Service is not currently running"
fi

print_status "Stopping existing service..."
systemctl stop anniex-ultrafast 2>/dev/null || true

sleep 2

print_status "Starting updated service..."
systemctl start anniex-ultrafast

sleep 3

print_status "Verifying service status..."
if systemctl is-active --quiet anniex-ultrafast; then
    print_success "Service restarted successfully!"
    echo ""
    print_status "Service details:"
    systemctl status anniex-ultrafast --no-pager -l
else
    print_error "Service failed to start!"
    echo ""
    print_status "Recent logs:"
    journalctl -u anniex-ultrafast --since "2 minutes ago" --no-pager | tail -20
    exit 1
fi

echo ""
print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "✅ Deployment completed successfully!"
print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Voice chat join fix has been deployed!"
echo "Changes:"
echo "  • Removed excessive logging"
echo "  • Improved error handling"
echo "  • Faster voice chat join times"
echo ""
print_status "To monitor bot logs, run:"
echo "  journalctl -u anniex-ultrafast -f"
echo ""
print_status "To check service status anytime:"
echo "  systemctl status anniex-ultrafast"
echo ""
