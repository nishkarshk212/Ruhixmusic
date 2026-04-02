#!/bin/bash

# Ultra-Fast Startup Script for ANNIEMUSIC Bot
# Optimized for 1-2 second response times

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║     🚀 ANNIEMUSIC Bot - ULTRA FAST START             ║"
echo "║         Optimized for 1-2s Response Time             ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Function to print colored output
print_green() {
    echo -e "\033[0;32m✓ $1\033[0m"
}

print_yellow() {
    echo -e "\033[1;33m➜ $1\033[0m"
}

print_red() {
    echo -e "\033[0;31m✗ $1\033[0m"
}

# Check Python version
print_yellow "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_green "Python version: $python_version"

# Check if dependencies are installed
print_yellow "Verifying dependencies..."
if python3 -c "import pyrogram, pytgcalls, motor" 2>/dev/null; then
    print_green "All core dependencies loaded"
else
    print_red "Missing dependencies! Installing..."
    pip3 install -r requirements.txt --quiet
    print_green "Dependencies installed"
fi

# Check .env file
if [ ! -f ".env" ]; then
    print_red "ERROR: .env file not found!"
    exit 1
fi
print_green "Configuration loaded from .env"

# Display optimization settings
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚡ PERFORMANCE OPTIMIZATIONS APPLIED:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • Bot Workers: 32 threads (was 8)"
echo "  • Assistant Workers: 16 threads each (was 4)"
echo "  • Sleep Threshold: 1 second (was 5)"
echo "  • PyTgCalls Cache: 500ms (was 300ms)"
echo "  • MongoDB Pool: 100 connections (was 50)"
echo "  • API Timeout: 15 seconds (was 30)"
echo "  • DB Timeouts: Reduced by 50%"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Set environment variable for performance mode
export ANNIEMUSIC_FAST_MODE=1

# Start the bot with optimized settings
print_yellow "Starting ANNIEMUSIC Bot in ULTRA FAST mode..."
echo ""

# Use nice and ionice for better resource allocation (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # High priority process on Linux
    nice -n -10 ionice -c 2 -n 1 python3 -m ANNIEMUSIC
else
    # macOS or other systems
    python3 -m ANNIEMUSIC
fi

# If we reach here, bot has stopped
echo ""
print_red "Bot has stopped unexpectedly!"
print_yellow "Check log.txt for error details"
print_yellow "Restarting in 5 seconds..."
sleep 5
exec "$0"  # Restart script
