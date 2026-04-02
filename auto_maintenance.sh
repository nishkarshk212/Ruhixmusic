#!/bin/bash

# ANNIEMUSIC Bot - Auto Maintenance Script
# Runs every 24 hours to: update, clean cache, restart bot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║     ANNIEMUSIC Bot - Auto Maintenance Script          ║${NC}"
echo -e "${BLUE}║           Daily Update & Cleanup                      ║${NC}"
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

WORK_DIR="/root/Ruhixmusic"
LOG_FILE="/root/Ruhixmusic/maintenance.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

cd "$WORK_DIR" || exit 1

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Starting Auto Maintenance..."

# Step 1: Stop the bot
print_status "Stopping bot service..."
systemctl stop ruhixmusic.service
log "Bot service stopped"

# Step 2: Git pull for auto-update
print_status "Checking for updates..."
cd "$WORK_DIR"
git fetch origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    log "Updates found! Pulling latest changes..."
    git pull origin main
    print_success "Bot updated successfully!"
    log "Update completed"
else
    log "Already up to date"
    print_success "No updates needed"
fi

# Step 3: Clear cache and unnecessary files
print_status "Cleaning cache and unnecessary files..."

# Clear Python cache
find "$WORK_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
log "Cleared Python __pycache__"

# Clear .pyc files
find "$WORK_DIR" -name "*.pyc" -delete 2>/dev/null || true
log "Cleared .pyc files"

# Clear downloads folder (old files)
if [ -d "$WORK_DIR/downloads" ]; then
    find "$WORK_DIR/downloads" -type f -mtime +1 -delete 2>/dev/null || true
    log "Cleared old downloads (>1 day)"
fi

# Clear cache folder
if [ -d "$WORK_DIR/cache" ]; then
    find "$WORK_DIR/cache" -type f -mtime +1 -delete 2>/dev/null || true
    log "Cleared old cache files (>1 day)"
fi

# Clear system temp files
rm -rf /tmp/anniex_* 2>/dev/null || true
log "Cleared temp files"

# Clear pip cache
pip cache purge 2>/dev/null || true
log "Cleared pip cache"

print_success "Cache cleaned successfully!"
log "Cache cleaning completed"

# Step 4: Check disk space
print_status "Disk usage after cleanup:"
df -h / | tail -1
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
log "Disk usage: ${DISK_USAGE}%"

# Step 5: Restart the bot
print_status "Starting bot service..."
systemctl start ruhixmusic.service
sleep 5

# Check if bot is running
if systemctl is-active --quiet ruhixmusic.service; then
    print_success "Bot restarted successfully!"
    log "Bot restarted successfully ✅"
else
    print_error "Bot failed to start! Check logs."
    log "Bot restart FAILED ❌"
    systemctl status ruhixmusic.service --no-pager
    exit 1
fi

# Final status
echo ""
print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_success "Auto Maintenance Completed Successfully!"
print_success "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "Auto Maintenance Completed Successfully!"

# Send notification to logger (optional)
echo ""
echo "Next scheduled maintenance: $(date -d '+24 hours' '+%Y-%m-%d %H:%M:%S')"
