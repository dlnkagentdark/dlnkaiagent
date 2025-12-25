# dLNk IDE - Quick Start Production Guide

**Version:** 1.0.0  
**Date:** December 25, 2025

---

## 🚀 5-Minute Production Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- Internet connection

### Step 1: Get the Project

```bash
# Clone or download from Google Drive
cd /path/to/your/server
# Assuming project is already available
cd dLNk-IDE-Project
```

### Step 2: Generate Security Keys

```bash
# Run these commands and save the output
echo "MASTER_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
echo "ENCRYPTION_SALT=$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
echo "JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
```

### Step 3: Configure Environment

```bash
cd deploy
cp .env.template .env
nano .env  # Edit with your values
```

**Minimum required changes in .env:**
```
MASTER_SECRET=<your-generated-secret>
ENCRYPTION_SALT=<your-generated-salt>
JWT_SECRET=<your-generated-jwt-secret>
```

### Step 4: Deploy

```bash
./deploy.sh setup
```

### Step 5: Verify

```bash
./deploy.sh status
```

Expected output:
```
Service status:
  - dlnk-license-server: Up
  - dlnk-ai-bridge: Up
  - dlnk-security: Up
  - dlnk-nginx: Up
```

---

## 🔗 Access Points

| Service | URL |
|---------|-----|
| License API | http://your-server:8088 |
| AI Bridge REST | http://your-server:8766 |
| AI Bridge WebSocket | ws://your-server:8765 |
| Security API | http://your-server:8089 |
| Main Proxy | http://your-server |

---

## 📱 Connect dLNk IDE Client

1. Open dLNk IDE application
2. Go to Settings → Server Configuration
3. Enter your server URL
4. Login or register
5. Activate license
6. Start coding!

---

## 🛠️ Common Commands

```bash
# Start services
./deploy.sh start

# Stop services
./deploy.sh stop

# View logs
./deploy.sh logs

# Check status
./deploy.sh status

# Run tests
./deploy.sh test

# Restart services
./deploy.sh restart
```

---

## ⚠️ Troubleshooting

**Services won't start:**
```bash
docker logs dlnk-license-server
docker logs dlnk-ai-bridge
```

**Port conflict:**
```bash
sudo lsof -i :8088
sudo lsof -i :8765
```

**Reset everything:**
```bash
./deploy.sh stop
docker system prune -a
./deploy.sh setup
```

---

## 📞 Support

For issues or questions, check:
- `docs/` folder for detailed documentation
- `PRODUCTION_DEPLOYMENT_CHECKLIST.md` for full checklist
- Project logs in Docker volumes

---

**Happy Coding with dLNk IDE! 🎄**
