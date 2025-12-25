# 📥 ติดตั้ง Admin Console

คู่มือการติดตั้งและตั้งค่า Admin Console สำหรับ dLNk IDE

---

## 💻 ความต้องการของระบบ

### Server Requirements

| รายการ | ความต้องการ |
|--------|-------------|
| **OS** | Ubuntu 20.04+, Windows Server 2019+, macOS 11+ |
| **RAM** | 2 GB ขึ้นไป |
| **Disk** | 1 GB ขึ้นไป |
| **Python** | 3.11+ |
| **Network** | Port 8766 (API), Port 443 (HTTPS) |

### Dependencies

```
fastapi>=0.100.0
uvicorn>=0.23.0
sqlalchemy>=2.0.0
python-telegram-bot>=20.0
customtkinter>=5.0.0
cryptography>=41.0.0
pyotp>=2.9.0
```

---

## 🐍 วิธีที่ 1: ติดตั้งด้วย Python (แนะนำ)

### 1. ติดตั้ง Python 3.11+

**Ubuntu:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows:**
ดาวน์โหลดจาก https://python.org

**macOS:**
```bash
brew install python@3.11
```

### 2. สร้าง Virtual Environment

```bash
# สร้าง venv
python3.11 -m venv dlnk-admin-env

# Activate
# Linux/macOS:
source dlnk-admin-env/bin/activate

# Windows:
dlnk-admin-env\Scripts\activate
```

### 3. ติดตั้ง Admin Console

```bash
pip install dlnk-admin-console
```

หรือติดตั้งจาก source:

```bash
git clone https://github.com/dlnk/admin-console.git
cd admin-console
pip install -r requirements.txt
pip install -e .
```

### 4. ตั้งค่าเริ่มต้น

```bash
# สร้าง config file
dlnk-admin init

# แก้ไข config
nano ~/.dlnk/admin/config.yaml
```

### 5. รัน Admin Console

```bash
# รัน GUI
dlnk-admin gui

# หรือรัน API Server
dlnk-admin server
```

---

## 🖥️ วิธีที่ 2: ติดตั้งด้วย Executable

### Windows

1. ดาวน์โหลด `dLNk-Admin-Setup.exe`
2. รันไฟล์ติดตั้ง
3. ทำตามขั้นตอน Installation Wizard
4. เปิดจาก Start Menu

### Linux

```bash
# ดาวน์โหลด AppImage
wget https://releases.dlnk.io/dLNk-Admin.AppImage
chmod +x dLNk-Admin.AppImage
./dLNk-Admin.AppImage
```

### macOS

1. ดาวน์โหลด `dLNk-Admin.dmg`
2. เปิดและลากไปยัง Applications
3. เปิดจาก Applications

---

## 🐳 วิธีที่ 3: ติดตั้งด้วย Docker

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  admin-api:
    image: dlnk/admin-console:latest
    ports:
      - "8766:8766"
    environment:
      - DATABASE_URL=sqlite:///data/dlnk_admin.db
      - SECRET_KEY=${SECRET_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  admin-web:
    image: dlnk/admin-web:latest
    ports:
      - "3000:3000"
    depends_on:
      - admin-api
    environment:
      - API_URL=http://admin-api:8766
    restart: unless-stopped
```

### รัน Docker

```bash
# สร้าง .env file
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
echo "TELEGRAM_BOT_TOKEN=your-bot-token" >> .env

# รัน
docker-compose up -d
```

---

## ⚙️ การตั้งค่า

### Config File

```yaml
# ~/.dlnk/admin/config.yaml

server:
  host: "0.0.0.0"
  port: 8766
  debug: false

database:
  url: "sqlite:///~/.dlnk/admin/dlnk_admin.db"
  # หรือใช้ PostgreSQL:
  # url: "postgresql://user:pass@localhost/dlnk_admin"

security:
  secret_key: "your-secret-key-here"
  token_expire_hours: 24
  enable_2fa: true

telegram:
  bot_token: "your-bot-token"
  admin_chat_id: "your-chat-id"
  enable_alerts: true

logging:
  level: "INFO"
  file: "~/.dlnk/admin/logs/admin.log"
```

### Environment Variables

```bash
# .env
DLNK_SECRET_KEY=your-secret-key
DLNK_DATABASE_URL=sqlite:///dlnk_admin.db
DLNK_TELEGRAM_BOT_TOKEN=your-bot-token
DLNK_ADMIN_CHAT_ID=your-chat-id
```

---

## 🔐 การตั้งค่า Admin แรก

### 1. สร้าง Super Admin

```bash
dlnk-admin create-admin \
  --username "superadmin" \
  --email "admin@dlnk.io" \
  --role "super_admin"
```

หรือผ่าน Python:

```python
from dlnk_admin import AdminManager

manager = AdminManager()
admin_key = manager.create_admin(
    username="superadmin",
    email="admin@dlnk.io",
    role="super_admin"
)
print(f"Admin Key: {admin_key}")
```

### 2. ตั้งค่า 2FA (แนะนำ)

```bash
dlnk-admin setup-2fa --username "superadmin"
```

จะได้ QR Code สำหรับ scan ด้วย Google Authenticator

### 3. ทดสอบการเข้าสู่ระบบ

```bash
dlnk-admin login
```

---

## 🌐 การตั้งค่า HTTPS

### ใช้ Let's Encrypt

```bash
# ติดตั้ง certbot
sudo apt install certbot

# ขอ certificate
sudo certbot certonly --standalone -d admin.dlnk.io

# ตั้งค่าใน config.yaml
```

```yaml
# config.yaml
server:
  ssl:
    enabled: true
    cert_file: "/etc/letsencrypt/live/admin.dlnk.io/fullchain.pem"
    key_file: "/etc/letsencrypt/live/admin.dlnk.io/privkey.pem"
```

### ใช้ Self-signed Certificate

```bash
# สร้าง certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ~/.dlnk/admin/ssl/key.pem \
  -out ~/.dlnk/admin/ssl/cert.pem
```

---

## 🔥 การตั้งค่า Firewall

### UFW (Ubuntu)

```bash
# เปิด port ที่จำเป็น
sudo ufw allow 8766/tcp  # Admin API
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### iptables

```bash
sudo iptables -A INPUT -p tcp --dport 8766 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

---

## 🔄 การอัพเดท

### Python Package

```bash
pip install --upgrade dlnk-admin-console
```

### Docker

```bash
docker-compose pull
docker-compose up -d
```

### Executable

ดาวน์โหลดเวอร์ชันใหม่และติดตั้งทับ

---

## ✅ ตรวจสอบการติดตั้ง

### ตรวจสอบ API

```bash
curl http://localhost:8766/health
```

ผลลัพธ์ที่ถูกต้อง:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### ตรวจสอบ Database

```bash
dlnk-admin db-check
```

### ตรวจสอบ Telegram Bot

```bash
dlnk-admin telegram-test
```

---

## 🔧 การแก้ไขปัญหา

### Port ถูกใช้งานอยู่

```bash
# หา process ที่ใช้ port
sudo lsof -i :8766

# Kill process
sudo kill -9 <PID>
```

### Database Error

```bash
# Reset database
dlnk-admin db-reset

# Migrate
dlnk-admin db-migrate
```

### Permission Denied

```bash
# แก้ไข permission
chmod 755 ~/.dlnk/admin
chmod 600 ~/.dlnk/admin/config.yaml
```

---

## 📞 ต้องการความช่วยเหลือ?

- ดู [Troubleshooting](troubleshooting.md)
- ติดต่อ: admin@dlnk.io

---

**ก่อนหน้า:** [← Admin Guide](README.md)  
**ถัดไป:** [จัดการ License →](license-management.md)
