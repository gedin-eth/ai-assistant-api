# 🚀 VPS Deployment Guide

This guide shows you how to deploy your AI Assistant API to a VPS server using GitHub and Docker.

## 📋 Prerequisites

- VPS server with Ubuntu 20.04+ or Debian 11+
- Root access to your VPS
- Domain name (optional but recommended)

## 🚀 Quick Deployment

### Step 1: SSH into your VPS

```bash
ssh root@your-vps-ip
```

### Step 2: Clone and Deploy

```bash
# Clone the repository
git clone https://github.com/gedin-eth/ai-assistant-api.git
cd ai-assistant-api

# Make the deployment script executable
chmod +x scripts/deploy_vps.sh

# Run the deployment script
./scripts/deploy_vps.sh your-domain.com
```

### Step 3: Configure Your Environment

```bash
# Edit the environment file with your API keys
nano .env
```

Update these values in the `.env` file:
- `OPENAI_API_KEY=your_actual_openai_api_key`
- `GOOGLE_SHEET_ID=your_actual_google_sheet_id`
- `DOMAIN=your_actual_domain.com`

### Step 4: Upload Your Credentials

From your local machine, upload your Google credentials:

```bash
# Upload Google credentials
scp credentials/google_credentials.json root@your-vps-ip:/opt/ai-assistant-api/credentials/
scp credentials/gmail_oauth_credentials.json root@your-vps-ip:/opt/ai-assistant-api/credentials/
```

### Step 5: Restart the Application

```bash
# On your VPS, restart the containers
cd /opt/ai-assistant-api
docker-compose restart
```

### Step 6: Test Your Deployment

```bash
# Test the health endpoint
curl http://localhost:8000/health

# Test the API documentation
curl http://localhost:8000/docs
```

## 🔧 Manual Deployment (Alternative)

If you prefer to deploy manually:

```bash
# 1. Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io

# 2. Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 3. Clone repository
git clone https://github.com/gedin-eth/ai-assistant-api.git
cd ai-assistant-api

# 4. Create .env file
nano .env

# 5. Build and start
docker-compose build
docker-compose up -d
```

## 📊 Monitoring and Management

### Check Application Status

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f

# Check resource usage
docker stats
```

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Restart Application

```bash
# Restart all containers
docker-compose restart

# Or restart specific service
docker-compose restart api
```

## 🔒 Security Considerations

1. **Firewall Setup**: Configure your VPS firewall
   ```bash
   ufw allow 22    # SSH
   ufw allow 80    # HTTP
   ufw allow 443   # HTTPS
   ufw enable
   ```

2. **SSL Certificate**: Set up SSL for production
   ```bash
   apt install -y certbot python3-certbot-nginx
   certbot --nginx -d your-domain.com
   ```

3. **Environment Variables**: Never commit sensitive data to Git

## 🐛 Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   netstat -tlnp | grep :8000
   docker-compose down
   docker-compose up -d
   ```

2. **Container won't start**
   ```bash
   docker-compose logs
   docker-compose logs api
   ```

3. **Permission issues**
   ```bash
   chown -R root:root /opt/ai-assistant-api
   chmod -R 755 /opt/ai-assistant-api
   ```

### Getting Help

- Check logs: `docker-compose logs -f`
- Check container status: `docker-compose ps`
- Check system resources: `htop` or `docker stats`

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify your API keys are correct
3. Ensure all credentials are in the right place
4. Check that ports are not blocked by firewall

Your application should now be running at `http://your-vps-ip:8000` or `https://your-domain.com` if you set up SSL. 