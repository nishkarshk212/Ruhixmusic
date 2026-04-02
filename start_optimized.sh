#!/bin/bash

# Music Bot Performance Startup Script
# This script starts the bot with performance monitoring

echo "======================================"
echo "  ANNIEMUSIC Bot - Optimized Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python version: $(python3 --version)"
echo ""

# Check if required packages are installed
echo "Checking dependencies..."
if ! python3 -c "import pyrogram" 2>/dev/null; then
    echo "❌ Required packages are missing. Installing..."
    pip3 install -r requirements.txt
fi
echo "✓ Dependencies OK"
echo ""

# Display current system resources
echo "System Resources:"
echo "----------------"
if command -v top &> /dev/null; then
    # macOS compatible
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Memory Usage:"
        vm_stat | perl -e 'while (<>) { print "/^(Page size of \d* bytes):\s+/" . ($n = $1) ? "" : $_ }' | perl -e 'while (<>) { if (/^free/) { ($f) = /\d+/; print "Free RAM: " . ($f * 4096 / 1024 / 1024) . " MB\n"; } elsif (/^active/) { ($a) = /\d+/; print "Active RAM: " . ($a * 4096 / 1024 / 1024) . " MB\n"; } }'
    else
        # Linux
        free -h | grep Mem
    fi
fi
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Please create a .env file with your API credentials."
    exit 1
fi
echo "✓ Configuration file found"
echo ""

# Start the bot with nice priority for better performance
echo "Starting ANNIEMUSIC Bot..."
echo "Press Ctrl+C to stop"
echo "======================================"
echo ""

# Use nice to give optimal CPU priority
nice -n 5 python3 -m ANNIEMUSIC

# If the bot crashes
echo ""
echo "======================================"
echo "Bot has stopped unexpectedly!"
echo "Check log.txt for errors."
echo "======================================"
