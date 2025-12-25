# dLNk IDE - Production Deployment Checklist

**Date:** December 25, 2025  
**Prepared By:** AI-12 (Continuation from AI-02)  
**Project Status:** ✅ **Ready for Production Deployment**

---

## 📋 Pre-Deployment Checklist

### 1. Infrastructure Requirements

| Item | Status | Notes |
|------|--------|-------|
| Docker Engine | ⬜ Required | Version 20.10+ recommended |
| Docker Compose | ⬜ Required | Version 2.0+ or docker-compose v1.29+ |
| Server (VPS/Cloud) | ⬜ Required | Minimum 2GB RAM, 2 vCPU |
| Domain Name | ⬜ Optional | For HTTPS/SSL setup |
| SSL Certificate | ⬜ Optional | Let's Encrypt or commercial cert |

### 2. Environment Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTIGRAVITY_ENDPOINT` | ✅ Yes | Primary AI provider endpoint |
| `OPENAI_API_KEY` | ⚠️ Optional | Fallback provider |
| `GEMINI_API_KEY` | ⚠️ Optional | Fallback provider |
| `GROQ_API_KEY` | ⚠️ Optional | Fallback provider |
| `TELEGRAM_BOT_TOKEN` | ⚠️ Optional | For alerts |
| `TELEGRAM_ADMIN_CHAT_ID` | ⚠️ Optional | For alerts |
| `MASTER_SECRET` | ✅ Yes | **MUST CHANGE** - Generate new key |
| `ENCRYPTION_SALT` | ✅ Yes | **MUST CHANGE** - Generate new salt |
| `JWT_SECRET` | ✅ Yes | **MUST CHANGE** - Generate new secret |

### 3. Security Secrets Generation

```bash
# Generate MASTER_SECRET (32 bytes hex)
python3 -c "import secrets; print(secrets.token_hex(32))"

# Generate ENCRYPTION_SALT (16 bytes hex)
python3 -c "import secrets; print(secrets.token_hex(16))"

# Generate JWT_SECRET (32 bytes hex)
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 Deployment Steps

### Step 1: Clone/Download Project

```bash
# Option A: Clone from repository
git clone <repository-url> dlnk-ide
cd dlnk-ide

# Option B: Download from Google Drive
rclone copy manus_google_drive:dLNk-IDE-Project/ ./dlnk-ide --config ~/.gdrive-rclone.ini
cd dlnk-ide
```

### Step 2: Configure Environment

```bash
cd deploy

# Copy template
cp .env.template .env

# Edit with your values
nano .env
```

**Important:** Replace all placeholder values with actual secrets!

### Step 3: Build Docker Images

```bash
./deploy.sh build
```

### Step 4: Start Services

```bash
./deploy.sh start
```

### Step 5: Verify Deployment

```bash
# Check service status
./deploy.sh status

# View logs
./deploy.sh logs
```

### Step 6: Run Integration Tests

```bash
./deploy.sh test
```

---

## 🔍 Service Endpoints

| Service | Port | Endpoint | Health Check |
|---------|------|----------|--------------|
| License API | 8088 | `http://localhost:8088` | `/health` |
| AI Bridge REST | 8766 | `http://localhost:8766` | `/health` |
| AI Bridge WebSocket | 8765 | `ws://localhost:8765` | N/A |
| Security API | 8089 | `http://localhost:8089` | `/health` |
| Nginx Proxy | 80/443 | `http://localhost` | N/A |

---

## 🔒 Security Recommendations

### Production Security Checklist

- [ ] **Change all default secrets** - MASTER_SECRET, ENCRYPTION_SALT, JWT_SECRET
- [ ] **Enable HTTPS** - Use SSL/TLS certificates
- [ ] **Configure firewall** - Only expose necessary ports (80, 443)
- [ ] **Set up rate limiting** - Already configured in .env
- [ ] **Enable Telegram alerts** - For security notifications
- [ ] **Regular backups** - Backup `/data` volumes
- [ ] **Monitor logs** - Check `/logs` volumes regularly

### SSL/TLS Setup (Optional but Recommended)

```bash
# Using Let's Encrypt with certbot
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem deploy/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem deploy/nginx/ssl/key.pem

# Enable SSL in .env
ENABLE_SSL=true
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check all services
curl http://localhost:8088/health  # License
curl http://localhost:8766/health  # AI Bridge
curl http://localhost:8089/health  # Security
```

### Log Locations

| Service | Log Path |
|---------|----------|
| License Server | `license-logs:/logs` |
| AI Bridge | `ai-bridge-logs:/logs` |
| Security | `security-logs:/logs` |
| Nginx | `nginx-logs:/var/log/nginx` |

### Backup Commands

```bash
# Backup all volumes
docker run --rm -v license-data:/data -v $(pwd):/backup alpine tar cvf /backup/license-data.tar /data
docker run --rm -v ai-bridge-tokens:/tokens -v $(pwd):/backup alpine tar cvf /backup/tokens.tar /tokens
```

---

## 🔄 Update Procedure

```bash
# 1. Pull latest changes
git pull origin main

# 2. Rebuild images
./deploy.sh build

# 3. Restart services
./deploy.sh restart

# 4. Verify
./deploy.sh status
```

---

## ⚠️ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | `sudo lsof -i :PORT` then kill process |
| Docker permission denied | `sudo usermod -aG docker $USER` then logout/login |
| Container won't start | Check logs: `docker logs dlnk-<service>` |
| Database locked | Restart license-server container |

### Emergency Commands

```bash
# Stop all services
./deploy.sh stop

# Remove all containers and volumes (CAUTION: Data loss!)
docker-compose down -v

# Full reset
./deploy.sh stop
docker system prune -a
./deploy.sh setup
```

---

## ✅ Post-Deployment Verification

- [ ] All services running (`./deploy.sh status`)
- [ ] Health checks passing
- [ ] License API responding
- [ ] AI Bridge WebSocket connecting
- [ ] Security service active
- [ ] Telegram alerts working (if configured)
- [ ] SSL/HTTPS working (if configured)

---

**Document Version:** 1.0  
**Last Updated:** December 25, 2025  
**Prepared By:** AI-12 (dLNk IDE Project)
