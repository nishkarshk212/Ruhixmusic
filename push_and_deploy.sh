#!/bin/bash

# Git Push and Server Update Script for ANNIEMUSIC Bot

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║     ANNIEMUSIC Bot - Git Push & Server Update         ║${NC}"
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

# Step 1: Check if changes are committed
print_status "Checking git status..."
cd /Users/nishkarshkr/Desktop/Music\ bot/anniex

if git diff-index --quiet HEAD --; then
    print_success "All changes committed"
else
    print_status "Committing staged changes..."
    git add -A
    git commit -m "Auto-commit: Latest changes"
    print_success "Changes committed!"
fi

# Step 2: Push to Git
print_status "Pushing to GitHub..."
git push origin main
print_success "Successfully pushed to GitHub!"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Step 3: Deploy to server via SSH
SERVER_HOST="161.118.250.195"
SERVER_USER="root"
SERVER_PASS="Akshay343402355468"
REMOTE_DIR="/root/Ruhixmusic"

print_status "Connecting to server ($SERVER_HOST)..."
print_status "Pulling latest changes on server..."

# SSH into server and deploy using sshpass
export SSHPASS="$SERVER_PASS"
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'ENDSSH'
cd /root/Ruhixmusic || exit 1

echo "Pulling latest changes from Git..."
git pull origin main

echo "Installing dependencies (if any changed)..."
pip3 install -r requirements.txt --quiet

echo "Restarting bot service..."
if systemctl is-active --quiet anniex-ultrafast; then
    systemctl restart anniex-ultrafast
    echo "Service restarted successfully!"
    echo ""
    echo "Service status:"
    systemctl status anniex-ultrafast --no-pager -l
else
    echo "Bot service not running as systemd service."
    echo "Checking for running process..."
    if pgrep -f "python.*ANNIEMUSIC" > /dev/null; then
        echo "Found running bot process, restarting..."
        pkill -f "python.*ANNIEMUSIC"
        sleep 2
        cd /root/anniex
        nohup python3 -m ANNIEMUSIC > bot.log 2>&1 &
        echo "Bot restarted!"
    else
        echo "Bot is not currently running. Starting it now..."
        cd /root/anniex
        nohup python3 -m ANNIEMUSIC > bot.log 2>&1 &
        echo "Bot started!"
    fi
fi

echo ""
echo "Deployment completed successfully!"
ENDSSH

# Check SSH exit status
if [ $? -eq 0 ]; then
    print_success "Server update completed successfully!"
else
    print_error "Failed to connect to server or deploy changes"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Your bot has been updated with the latest changes!${NC}"
echo -e "${YELLOW}Support Channel: @Tele_212_bots${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
print_success "New feature added: /vcusers command to see voice chat participants"
