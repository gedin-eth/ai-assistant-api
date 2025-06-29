# 🐳 Docker Deployment Guide for AI Personal Assistant API

This guide will help you dockerize and deploy your AI Personal Assistant API on a VPS server with Docker, Docker Compose, Nginx, and SSL certificates.

## 📋 **Prerequisites**

### **VPS Requirements**
- **OS**: Ubuntu 20.04+ or Debian 11+
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: Minimum 20GB
- **CPU**: 2 cores minimum
- **Domain**: A domain name pointing to your VPS IP

### **Domain Setup**
1. **DNS Configuration**: Point your domain to your VPS IP address
   ```bash
   # Example DNS records
   A     your-domain.com     -> YOUR_VPS_IP
   A     www.your-domain.com -> YOUR_VPS_IP
   ```

2. **Wait for DNS Propagation**: Allow 24-48 hours for DNS changes to propagate

## 🚀 **Quick Deployment**

### **Option 1: Automated Deployment (Recommended)**

1. **Upload files to your VPS**:
   ```bash
   # On your local machine
   scp -r . user@your-vps-ip:/home/user/ai-assistant-api
   
   # Or use git
   git clone your-repo-url
   ```

2. **Run the deployment script**:
   ```bash
   # SSH into your VPS
   ssh user@your-vps-ip
   
   # Navigate to the project directory
   cd ai-assistant-api
   
   # Make the script executable
   chmod +x scripts/deploy.sh
   
   # Run deployment (replace with your domain and email)
   ./scripts/deploy.sh your-domain.com admin@your-domain.com
   ```

### **Option 2: Manual Deployment**

Follow the step-by-step manual deployment process below.

## 🔧 **Manual Deployment Steps**

### **Step 1: Server Preparation**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
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
```

### **Step 2: Install Docker**

```bash
# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
exit
# SSH back in
```

### **Step 3: Install Docker Compose**

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### **Step 4: Set Up Application Directory**

```bash
# Create application directory
sudo mkdir -p /opt/ai-assistant-api
sudo chown $USER:$USER /opt/ai-assistant-api

# Copy application files
cp -r . /opt/ai-assistant-api/
cd /opt/ai-assistant-api

# Create credentials directory
mkdir -p credentials
```

### **Step 5: Configure Environment**

```bash
# Create environment file
cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google API Configuration
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_CALENDAR_ID=primary

# Email Configuration
DEFAULT_EMAIL=admin@your-domain.com

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Domain Configuration
DOMAIN=your-domain.com
EOF

# Edit with your actual values
nano .env
```

### **Step 6: Set Up Google Credentials**

1. **Download Google Service Account credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to APIs & Services > Credentials
   - Download your service account JSON file
   - Rename to `google_credentials.json`

2. **Download Gmail OAuth2 credentials**:
   - Download your OAuth2 credentials JSON file
   - Rename to `gmail_oauth_credentials.json`

3. **Upload to VPS**:
   ```bash
   # On your local machine
   scp google_credentials.json user@your-vps-ip:/opt/ai-assistant-api/credentials/
   scp gmail_oauth_credentials.json user@your-vps-ip:/opt/ai-assistant-api/credentials/
   ```

### **Step 7: Configure Nginx**

```bash
# Update Nginx configuration with your domain
sed -i "s/your-domain.com/YOUR_ACTUAL_DOMAIN/g" nginx/ai-assistant.conf

# Install Nginx
sudo apt install -y nginx

# Enable and start Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### **Step 8: Set Up SSL Certificate**

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Create SSL directory
mkdir -p ssl

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com --non-interactive --agree-tos --email admin@your-domain.com

# Copy certificates to our directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/cert.pem ssl/key.pem
```

### **Step 9: Build and Deploy**

```bash
# Build Docker images
docker-compose build

# Start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### **Step 10: Test Deployment**

```bash
# Test health endpoint
curl -f https://your-domain.com/health

# Test API documentation
curl -f https://your-domain.com/docs

# Test root endpoint
curl -f https://your-domain.com/
```

## 🔄 **Management Commands**

### **Container Management**

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f ai-assistant-api

# Update and restart
docker-compose pull
docker-compose up -d --build
```

### **System Service Management**

```bash
# Enable auto-start
sudo systemctl enable ai-assistant.service

# Start service
sudo systemctl start ai-assistant.service

# Stop service
sudo systemctl stop ai-assistant.service

# Check status
sudo systemctl status ai-assistant.service

# View logs
sudo journalctl -u ai-assistant.service -f
```

### **SSL Certificate Renewal**

```bash
# Test renewal
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew

# Set up automatic renewal (add to crontab)
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Container Won't Start**
```bash
# Check logs
docker-compose logs ai-assistant-api

# Check environment variables
docker-compose config

# Verify credentials
ls -la credentials/
```

#### **2. SSL Certificate Issues**
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check Nginx configuration
sudo nginx -t
```

#### **3. Database Issues**
```bash
# Check database file permissions
ls -la assistant.db

# Reset database (if needed)
docker-compose down
rm assistant.db
docker-compose up -d
```

#### **4. Port Conflicts**
```bash
# Check what's using port 8000
sudo netstat -tlnp | grep :8000

# Check what's using port 80/443
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### **Log Locations**

```bash
# Application logs
docker-compose logs ai-assistant-api

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u ai-assistant.service -f
```

## 🔒 **Security Considerations**

### **Firewall Setup**

```bash
# Install UFW
sudo apt install ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Check status
sudo ufw status
```

### **Regular Updates**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d

# Update SSL certificates
sudo certbot renew
```

## 📊 **Monitoring**

### **Health Checks**

```bash
# Manual health check
curl -f https://your-domain.com/health

# Automated monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
if ! curl -f https://your-domain.com/health > /dev/null 2>&1; then
    echo "API is down! Restarting..."
    docker-compose restart
    # Send notification email
    echo "API restarted at $(date)" | mail -s "API Restart" admin@your-domain.com
fi
EOF

chmod +x monitor.sh

# Add to crontab for monitoring
crontab -e
# Add: */5 * * * * /opt/ai-assistant-api/monitor.sh
```

### **Resource Monitoring**

```bash
# Check container resource usage
docker stats

# Check disk usage
df -h

# Check memory usage
free -h

# Check system load
uptime
```

## 🚀 **Scaling Considerations**

### **For Higher Traffic**

1. **Increase Resources**:
   - Upgrade VPS to more RAM/CPU
   - Add load balancer
   - Use multiple instances

2. **Database Optimization**:
   - Migrate to PostgreSQL
   - Add database clustering
   - Implement caching (Redis)

3. **Performance Tuning**:
   - Optimize Nginx configuration
   - Add CDN for static assets
   - Implement rate limiting

## 📚 **Additional Resources**

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

## 🎉 **Deployment Complete!**

Your AI Personal Assistant API is now running on your VPS with:
- ✅ **Docker containerization**
- ✅ **Nginx reverse proxy**
- ✅ **SSL encryption**
- ✅ **Automatic startup**
- ✅ **Health monitoring**
- ✅ **Log management**

**Access your API at**: `https://your-domain.com`
**API Documentation**: `https://your-domain.com/docs`
**Health Check**: `https://your-domain.com/health` 