#!/bin/bash

# AI Personal Assistant API Deployment Script
# This script sets up and deploys the API on a VPS server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}

echo -e "${BLUE}🚀 AI Personal Assistant API Deployment Script${NC}"
echo -e "${BLUE}==============================================${NC}"
echo ""

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Update system packages
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System packages updated"

# Install required packages
print_info "Installing required packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release
print_status "Required packages installed"

# Install Docker
print_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo usermod -aG docker $USER
    print_status "Docker installed"
else
    print_status "Docker already installed"
fi

# Install Docker Compose
print_info "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
else
    print_status "Docker Compose already installed"
fi

# Install Nginx
print_info "Installing Nginx..."
sudo apt install -y nginx
sudo systemctl enable nginx
sudo systemctl start nginx
print_status "Nginx installed and started"

# Install Certbot for SSL certificates
print_info "Installing Certbot..."
sudo apt install -y certbot python3-certbot-nginx
print_status "Certbot installed"

# Create application directory
print_info "Setting up application directory..."
APP_DIR="/opt/ai-assistant-api"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR
print_status "Application directory created: $APP_DIR"

# Clone or copy application files
if [ -d ".git" ]; then
    print_info "Copying application files..."
    cp -r . $APP_DIR/
else
    print_warning "Not a git repository. Please ensure all application files are in the current directory."
    cp -r . $APP_DIR/
fi

cd $APP_DIR

# Create credentials directory
print_info "Setting up credentials directory..."
mkdir -p credentials
print_status "Credentials directory created"

# Create environment file
print_info "Creating environment file..."
if [ ! -f .env ]; then
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google API Configuration
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_CALENDAR_ID=primary

# Email Configuration
DEFAULT_EMAIL=$EMAIL

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Domain Configuration
DOMAIN=$DOMAIN
EOF
    print_status "Environment file created"
    print_warning "Please edit .env file with your actual API keys and configuration"
else
    print_status "Environment file already exists"
fi

# Update Nginx configuration with domain
print_info "Updating Nginx configuration..."
sed -i "s/your-domain.com/$DOMAIN/g" nginx/ai-assistant.conf
print_status "Nginx configuration updated"

# Create SSL directory
print_info "Setting up SSL directory..."
mkdir -p ssl
print_status "SSL directory created"

# Get SSL certificate
print_info "Obtaining SSL certificate..."
if sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL; then
    print_status "SSL certificate obtained"
    
    # Copy SSL certificates to our directory
    sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/cert.pem
    sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/key.pem
    sudo chown $USER:$USER ssl/cert.pem ssl/key.pem
    print_status "SSL certificates copied"
else
    print_warning "Could not obtain SSL certificate. You may need to configure DNS first."
    print_info "Creating self-signed certificate for testing..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    print_status "Self-signed certificate created"
fi

# Build and start containers
print_info "Building and starting Docker containers..."
docker-compose build
docker-compose up -d
print_status "Containers started"

# Wait for application to be ready
print_info "Waiting for application to be ready..."
sleep 30

# Test the application
print_info "Testing application..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_status "Application is running successfully!"
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}📋 Deployment Summary:${NC}"
    echo -e "  • Application URL: https://$DOMAIN"
    echo -e "  • API Documentation: https://$DOMAIN/docs"
    echo -e "  • Health Check: https://$DOMAIN/health"
    echo -e "  • Application Directory: $APP_DIR"
    echo ""
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo -e "  1. Edit .env file with your actual API keys"
    echo -e "  2. Place your Google credentials in the credentials/ directory"
    echo -e "  3. Restart containers: docker-compose restart"
    echo -e "  4. Set up automatic SSL renewal: sudo crontab -e"
    echo -e "     Add: 0 12 * * * /usr/bin/certbot renew --quiet"
    echo ""
else
    print_error "Application failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Set up log rotation
print_info "Setting up log rotation..."
sudo tee /etc/logrotate.d/ai-assistant > /dev/null << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF
print_status "Log rotation configured"

# Create systemd service for auto-start
print_info "Creating systemd service..."
sudo tee /etc/systemd/system/ai-assistant.service > /dev/null << EOF
[Unit]
Description=AI Personal Assistant API
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable ai-assistant.service
print_status "Systemd service created and enabled"

print_info "Deployment completed! The API will automatically start on system boot." 