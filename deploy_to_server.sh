#!/bin/bash

# Server Deployment Script for ANNIEMUSIC Bot
# This script updates the bot from Git repository

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║     ANNIEMUSIC Bot - Server Update Script             ║${NC}"
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

cd /root/anniex || exit 1

print_status "Pulling latest changes from Git..."
git pull origin main

print_success "Git pull completed!"

print_status "Checking if systemd service exists..."
if systemctl is-active --quiet anniex-ultrafast; then
    print_status "Restarting anniex-ultrafast service..."
    sudo systemctl restart anniex-ultrafast
    print_success "Service restarted successfully!"
    
    print_status "Service status:"
    sudo systemctl status anniex-ultrafast --no-pager
else
    print_status "Bot is not running as a service. Checking for running process..."
    if pgrep -f "python.*ANNIEMUSIC" > /dev/null; then
        print_status "Found running bot process, restarting..."
        pkill -f "python.*ANNIEMUSIC"
        sleep 2
        cd /root/anniex
        nohup python3 -m ANNIEMUSIC > bot.log 2>&1 &
        print_success "Bot restarted!"
    else
        print_status "Bot is not currently running. You can start it manually."
    fi
fi

echo ""
print_success "Server update completed!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Your bot has been updated with the latest changes!"
echo "Support Channel: @Tele_212_bots"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
