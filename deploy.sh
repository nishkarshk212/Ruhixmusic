#!/bin/bash

# Automated Deployment Script for ANNIEMUSIC Bot
# Supports: Heroku, VPS, and Docker

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║     ANNIEMUSIC Bot - Automated Deployment Script      ║${NC}"
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

# Check if .env exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please create a .env file with your credentials first."
    exit 1
fi
print_success ".env file found"

# Deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI is not installed!"
        echo "Install it from: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Login to Heroku
    print_status "Logging in to Heroku..."
    heroku login
    
    # Create app or use existing
    echo ""
    read -p "Enter Heroku app name (or press Enter to create new): " APP_NAME
    
    if [ -z "$APP_NAME" ]; then
        print_status "Creating new Heroku app..."
        heroku create
        APP_NAME=$(heroku apps --json | jq -r '.[0].app.name')
    else
        print_status "Using existing app: $APP_NAME"
    fi
    
    # Set environment variables from .env
    print_status "Setting environment variables..."
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        # Remove leading/trailing whitespace
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs)
        print_status "Setting $key..."
        heroku config:set "$key=$value" --app "$APP_NAME"
    done < .env
    
    # Set buildpack
    print_status "Setting Python buildpack..."
    heroku buildpacks set heroku/python --app "$APP_NAME"
    
    # Deploy
    print_status "Deploying to Heroku..."
    git push heroku main
    
    # Scale worker
    print_status "Scaling worker..."
    heroku ps:scale worker=1 --app "$APP_NAME"
    
    # Show logs
    print_success "Deployment complete!"
    echo ""
    read -p "Do you want to view logs? (y/n): " SHOW_LOGS
    if [ "$SHOW_LOGS" = "y" ]; then
        heroku logs --tail --app "$APP_NAME"
    fi
    
    print_success "Your bot is now running on Heroku!"
    echo "App URL: https://$APP_NAME.herokuapp.com"
}

# Deploy to VPS
deploy_vps() {
    print_status "Preparing for VPS deployment..."
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    # Create systemd service
    echo ""
    read -p "Do you want to create a systemd service? (y/n): " CREATE_SERVICE
    
    if [ "$CREATE_SERVICE" = "y" ]; then
        print_status "Creating systemd service..."
        
        # Get absolute path
        WORK_DIR=$(pwd)
        PYTHON_PATH=$(which python3)
        
        # Create service file
        sudo bash -c "cat > /etc/systemd/system/anniex.service" << EOF
[Unit]
Description=ANNIEMUSIC Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$WORK_DIR
ExecStart=$PYTHON_PATH -m ANNIEMUSIC
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        # Enable and start service
        print_status "Enabling service..."
        sudo systemctl daemon-reload
        sudo systemctl enable anniex
        sudo systemctl start anniex
        
        # Show status
        print_success "Service created and started!"
        echo ""
        sudo systemctl status anniex
    else
        print_status "Starting bot manually..."
        ./start_optimized.sh
    fi
}

# Deploy using Docker
deploy_docker() {
    print_status "Deploying using Docker..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    # Build image
    print_status "Building Docker image..."
    docker build -t anniex-music .
    
    # Stop existing container if running
    print_status "Stopping existing container (if any)..."
    docker stop anniex 2>/dev/null || true
    docker rm anniex 2>/dev/null || true
    
    # Run container
    print_status "Starting container..."
    docker run -d \
        --name anniex \
        --env-file .env \
        --restart unless-stopped \
        anniex-music
    
    print_success "Container started!"
    echo ""
    echo "View logs with: docker logs -f anniex"
    echo "Stop with: docker stop anniex"
    echo "Start with: docker start anniex"
}

# Main menu
echo -e "${BLUE}Select deployment target:${NC}"
echo "1. Heroku (Cloud Platform)"
echo "2. VPS/Dedicated Server"
echo "3. Docker"
echo "4. Run Diagnostic Check"
echo "5. Exit"
echo ""

read -p "Choose an option (1-5): " OPTION

case $OPTION in
    1)
        deploy_heroku
        ;;
    2)
        deploy_vps
        ;;
    3)
        deploy_docker
        ;;
    4)
        print_status "Running diagnostic check..."
        ./check_performance.py
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid option!"
        exit 1
        ;;
esac

echo ""
print_success "Done!"
