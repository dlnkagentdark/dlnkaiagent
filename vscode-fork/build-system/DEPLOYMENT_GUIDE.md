# dLNk IDE - Deployment Guide
**Version:** 1.0.0  
**Date:** 2025-12-24  
**Target:** Production Deployment

---

## 📋 Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM:** 4GB minimum, 8GB recommended
- **CPU:** 2 cores minimum, 4 cores recommended
- **Disk:** 20GB free space
- **Docker:** 20.10+ with Docker Compose v2

### Required Services
- Docker Engine
- Docker Compose
- Nginx (optional, included in compose)
- SSL Certificate (for HTTPS)

---

## 🚀 Quick Deployment

### Step 1: Clone Repository
```bash
git clone https://github.com/dlnk/dlnk-ide-project.git
cd dlnk-ide-project
```

### Step 2: Configure Environment
```bash
cd deploy
cp .env.template .env
nano .env
```

**Required Environment Variables:**
```bash
# Antigravity Configuration
ANTIGRAVITY_ENDPOINT=grpc.antigravity.ai:443

# API Keys (Optional - for fallback)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=...

# Telegram Bot
TELEGRAM_BOT_TOKEN=8209736694:AAGdDD_ko9zq27C-gvCIDqCHAH3UnYY9RJc
TELEGRAM_ADMIN_CHAT_ID=7420166612

# Security
DLNK_ENCRYPTION_KEY=<generate-with-fernet>
DLNK_ADMIN_KEY=<generate-random-key>

# Database
DLNK_DATABASE_PATH=/data/dlnk_license.db
```

### Step 3: Generate Encryption Keys
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Step 4: Deploy Services
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🔧 Manual Deployment

### Backend Services

#### 1. License Server
```bash
cd backend/license
docker build -t dlnk-license:1.0.0 .
docker run -d \
  --name dlnk-license \
  -p 8088:8088 \
  -v license-data:/data \
  -e DLNK_API_HOST=0.0.0.0 \
  -e DLNK_API_PORT=8088 \
  dlnk-license:1.0.0
```

#### 2. AI Bridge
```bash
cd backend/ai-bridge
docker build -t dlnk-ai-bridge:1.0.0 .
docker run -d \
  --name dlnk-ai-bridge \
  -p 8765:8765 \
  -p 8766:8766 \
  -v ai-bridge-tokens:/tokens \
  -e DLNK_WS_PORT=8765 \
  -e DLNK_REST_PORT=8766 \
  -e ANTIGRAVITY_ENDPOINT=${ANTIGRAVITY_ENDPOINT} \
  dlnk-ai-bridge:1.0.0
```

#### 3. Security Service
```bash
cd security
docker build -t dlnk-security:1.0.0 .
docker run -d \
  --name dlnk-security \
  -p 8089:8089 \
  -v security-data:/data \
  -e TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN} \
  -e TELEGRAM_ADMIN_CHAT_ID=${TELEGRAM_ADMIN_CHAT_ID} \
  dlnk-security:1.0.0
```

---

## 🔐 SSL Configuration

### Using Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Manual Certificate
```bash
# Place certificates in deploy/nginx/ssl/
cp your-cert.crt deploy/nginx/ssl/
cp your-key.key deploy/nginx/ssl/

# Update nginx.conf
nano deploy/nginx/nginx.conf
```

---

## 📊 Health Checks

### Check Service Status
```bash
# All services
docker-compose ps

# Individual service
docker logs dlnk-license
docker logs dlnk-ai-bridge
docker logs dlnk-security
```

### API Health Endpoints
```bash
# License Server
curl http://localhost:8088/health

# AI Bridge
curl http://localhost:8766/health

# Security Service
curl http://localhost:8089/health
```

---

## 🔄 Updates and Maintenance

### Update Services
```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose down
docker-compose up -d
```

### Backup Database
```bash
# Backup license database
docker exec dlnk-license \
  sqlite3 /data/dlnk_license.db ".backup '/data/backup.db'"

# Copy to host
docker cp dlnk-license:/data/backup.db ./backup-$(date +%Y%m%d).db
```

### View Logs
```bash
# Real-time logs
docker-compose logs -f

# Specific service
docker-compose logs -f ai-bridge

# Last 100 lines
docker-compose logs --tail=100
```

---

## 🛡️ Security Best Practices

1. **Change Default Keys:** Generate new encryption keys
2. **Use HTTPS:** Always use SSL in production
3. **Firewall Rules:** Restrict access to backend ports
4. **Regular Backups:** Automate database backups
5. **Monitor Logs:** Set up log monitoring and alerts
6. **Update Regularly:** Keep Docker images updated

---

## 📱 Admin Console

### Desktop Installation
```bash
cd admin-console
pip3 install -r requirements.txt
python3 main.py
```

### Configuration
```bash
# Edit config
nano admin-console/config.py

# Set API endpoints
DLNK_LICENSE_API=http://localhost:8088
DLNK_AI_BRIDGE_API=http://localhost:8766
DLNK_SECURITY_API=http://localhost:8089
```

---

## 🤖 Telegram Bot

### Setup
```bash
cd telegram-bot
pip3 install -r requirements.txt

# Configure
export TELEGRAM_BOT_TOKEN="your-token"
export TELEGRAM_ADMIN_CHAT_ID="your-chat-id"

# Run
python3 main.py
```

---

## 🐛 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Check port conflicts
sudo netstat -tulpn | grep <port>

# Restart service
docker-compose restart <service-name>
```

### Database Issues
```bash
# Check database
docker exec dlnk-license sqlite3 /data/dlnk_license.db ".tables"

# Reset database (CAUTION: Deletes all data)
docker-compose down -v
docker-compose up -d
```

### Connection Issues
```bash
# Test connectivity
curl -v http://localhost:8088/health
curl -v http://localhost:8766/health

# Check firewall
sudo ufw status
sudo ufw allow 8088/tcp
sudo ufw allow 8765/tcp
sudo ufw allow 8766/tcp
```

---

## 📞 Support

- **Documentation:** https://docs.dlnk.dev
- **Issues:** https://github.com/dlnk/dlnk-ide/issues
- **Telegram:** @dlnk_support

---

*Last Updated: 2025-12-24*
