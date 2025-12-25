# 🔑 dLNk License & Authentication System

ระบบจัดการ License และ Authentication สำหรับ dLNk IDE

## 📁 โครงสร้างโปรเจค

```
license/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt
├── README.md
├── license/
│   ├── __init__.py
│   ├── generator.py           # License key generation
│   ├── validator.py           # License validation
│   ├── hardware.py            # Hardware ID binding
│   └── storage.py             # License storage (SQLite)
├── auth/
│   ├── __init__.py
│   ├── login.py               # Login logic (supports offline)
│   ├── register.py            # Registration logic
│   ├── totp.py                # 2FA TOTP
│   └── session.py             # Session management
├── api/
│   ├── __init__.py
│   ├── server.py              # FastAPI server
│   └── routes/
│       ├── license.py         # License endpoints
│       └── auth.py            # Auth endpoints
└── utils/
    ├── __init__.py
    ├── encryption.py          # Fernet encryption
    └── helpers.py             # Utility functions
```

## 🚀 การติดตั้ง

```bash
# ติดตั้ง dependencies
pip install -r requirements.txt

# หรือติดตั้งทีละตัว
pip install fastapi uvicorn cryptography aiohttp pyotp qrcode pydantic
```

## 💻 การใช้งาน

### เริ่ม API Server

```bash
python main.py server
# หรือ
python main.py server --host 0.0.0.0 --port 8088
```

### สร้าง License

```bash
# สร้าง License แบบ formatted (DLNK-XXXX-XXXX-XXXX-XXXX)
python main.py generate --type pro --days 365 --owner "John Doe" --email "john@example.com"

# สร้าง License แบบ encrypted (compatible กับระบบเดิม)
python main.py generate --encrypted --days 30 --owner "John Doe"
```

### ตรวจสอบ License

```bash
python main.py validate DLNK-XXXX-XXXX-XXXX-XXXX
```

### สร้าง User

```bash
python main.py create-user --username john --password "SecurePass123!" --email john@example.com
```

### ดู Hardware ID

```bash
python main.py hwid
```

### ดูสถิติ

```bash
python main.py stats
```

## 📡 API Endpoints

### License API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/license/generate` | สร้าง License ใหม่ |
| POST | `/api/license/validate` | ตรวจสอบ License |
| POST | `/api/license/extend` | ขยายอายุ License |
| POST | `/api/license/revoke` | เพิกถอน License |
| GET | `/api/license/info/{key}` | ดูข้อมูล License |
| GET | `/api/license/list` | ดูรายการ License |
| GET | `/api/license/stats` | ดูสถิติ |

### Auth API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/register` | ลงทะเบียน |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | ดูข้อมูล user ปัจจุบัน |
| POST | `/api/auth/change-password` | เปลี่ยนรหัสผ่าน |
| GET | `/api/auth/sessions` | ดูรายการ sessions |

## 📄 License Key Format

```
DLNK-XXXX-XXXX-XXXX-XXXX

โครงสร้าง:
- DLNK: Prefix
- XXXX: 4 กลุ่ม ตัวอักษร/ตัวเลข (Hex)
```

## 🔐 License Types

| Type | Features | Duration |
|------|----------|----------|
| Trial | ai_chat, basic_code_assist | 14 days |
| Pro | ai_chat, code_complete, history, dark_mode, priority_support | 365 days |
| Enterprise | All features + unlimited, api_access, custom_branding, admin_panel | 365 days |

## 🖥️ Hardware ID

Hardware ID สร้างจาก:
- MAC Address
- CPU ID
- Disk Serial
- Machine ID

รองรับทั้ง Windows และ Linux

## 🔒 Offline Mode

ระบบรองรับ Offline Mode:
- บันทึก credentials แบบเข้ารหัส
- ใช้งานได้ 7 วันโดยไม่ต้องเชื่อมต่อ internet
- ต้อง login online อีกครั้งเมื่อหมดอายุ

## 🔐 2FA (Two-Factor Authentication)

รองรับ TOTP (Time-based One-Time Password):
- ใช้ได้กับ Google Authenticator, Authy, etc.
- สร้าง QR Code สำหรับ setup

## ⚙️ Environment Variables

```bash
DLNK_MASTER_SECRET=<encryption-key>
DLNK_SESSION_SECRET=<session-key>
DLNK_API_HOST=0.0.0.0
DLNK_API_PORT=8088
DLNK_ADMIN_API=http://localhost:8089
DLNK_ENV=development  # or production
```

## 📝 Example Usage

### Python

```python
from license import generate_license, validate_license

# Generate
key, encrypted = generate_license(
    user_id="user123",
    license_type="pro",
    duration_days=365
)
print(f"License: {key}")

# Validate
result = validate_license(key)
if result.valid:
    print(f"Features: {result.features}")
    print(f"Days remaining: {result.days_remaining}")
```

### API (cURL)

```bash
# Generate License
curl -X POST http://localhost:8088/api/license/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "license_type": "pro", "duration_days": 365}'

# Validate License
curl -X POST http://localhost:8088/api/license/validate \
  -H "Content-Type: application/json" \
  -d '{"license_key": "DLNK-XXXX-XXXX-XXXX-XXXX"}'

# Login
curl -X POST http://localhost:8088/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "SecurePass123!"}'
```

## 🔗 Dependencies

- **AI-04 (UI)**: ต้องการ Login/Register API
- **AI-05 (AI Bridge)**: อาจต้องการ Token validation
- **AI-07 (Admin)**: ต้องการ License Management API

## 📄 License

Copyright © 2025 dLNk IDE Project
