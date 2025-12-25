# 🔍 dLNk & Antigravity System Analysis

## 📋 Executive Summary

โปรเจ็คนี้ประกอบด้วยระบบหลัก 3 ส่วนที่ต้องผสานเข้าด้วยกัน:

1. **Antigravity** - VS Code-based IDE ที่มี AI integration ผ่าน gRPC
2. **dLNk Core** - ระบบจัดการ License, Admin, และ AI Bridge
3. **VS Code Fork** - ต้องสร้างใหม่ภายใต้แบรนด์ AI DLNK

---

## 🏗️ System Architecture

### 1. Antigravity gRPC Integration

**Endpoint หลัก:**
```
https://antigravity-worker.google.com/exa.language_server_pb.LanguageServerService/SendUserCascadeMessage
```

**Protocol:**
- gRPC over HTTP/2
- Binary Protobuf encoding
- Bearer Token authentication

**Key Components:**
- `ProtoEncoder` - สร้าง Protobuf binary payload
- `build_cascade_request()` - สร้าง request สำหรับ AI chat
- `TokenManager` - จัดการ Access/Refresh Token

### 2. OAuth Configuration

```python
OAUTH_CLIENT_ID = "1090535352638-q5m3558i87588pnd64fjm614un18k0id.apps.googleusercontent.com"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
```

**Token Storage:** `~/.dlnk/tokens/unified_tokens.json`

### 3. AI Provider Priority

| Priority | Provider | Type | Cost |
|----------|----------|------|------|
| 1 | Antigravity | gRPC | Free (with token) |
| 2 | Gemini | REST API | Free tier |
| 3 | OpenAI | REST API | Paid |
| 4 | Groq | REST API | Free tier |
| 5 | Ollama | Local | Free |
| 6 | Offline | N/A | N/A |

---

## 🔑 Key Files Analysis

### Core System Files

| File | Purpose | Key Classes |
|------|---------|-------------|
| `dlnk_unified_launcher.py` | Main launcher (GUI + CLI) | UnifiedTokenManager, AntigravityClient, UnifiedAIBridge |
| `dlnk_antigravity_bridge.py` | gRPC connection | ProtoEncoder, TokenManager, AntigravityClient |
| `ai_gateway_server.py` | REST API server | AIProviderManager, RateLimiter |
| `dlnk_license_system.py` | License management | DLNKLicenseSystem, License, User |
| `dlnk_admin_auth.py` | Admin authentication | AdminAuthDB, Session management |
| `dlnk_telegram_bot.py` | Telegram bot | DLNKTelegramBot |

### Proxy & Security Files

| File | Purpose |
|------|---------|
| `mitm_https_proxy.py` | HTTPS MITM proxy for token harvesting |
| `exfil_client.py` | Data exfiltration client |
| `trace_jetski.py` | Jetski protocol analyzer |

---

## 🔧 Integration Points

### 1. Token Flow
```
User → Import Token → TokenManager → Auto-Refresh → Antigravity gRPC
                                   ↓
                            Fallback to Gemini/OpenAI
```

### 2. API Server Flow
```
Client → REST API (/v1/chat/completions) → AIProviderManager → Provider Selection → Response
```

### 3. VS Code Integration
```
VS Code → Extension → Proxy (8081) → Antigravity gRPC
                   ↓
            Token Injection
```

---

## 📝 Required Changes for AI DLNK Fork

### 1. Branding Changes
- ชื่อแอพ: "AI DLNK"
- Logo และ UI ใหม่
- ตัด AI ค่ายอื่นออก (ใช้เฉพาะ Jetski ผ่าน Antigravity)

### 2. UI Login System
- ใช้ระบบ Login แบบเดิมจาก `dlnk_admin_auth.py`
- รองรับ 2FA (TOTP)
- Session-based authentication

### 3. Bot Integration
- Telegram Bot สำหรับ License management
- Admin Console ผ่าน Web

### 4. API Endpoints
```
/v1/chat/completions - AI Chat (OpenAI-compatible)
/admin/token/import - Import token
/admin/token/status - Check token status
/verify - License verification
```

---

## 🚀 Recommended Architecture for AI DLNK

```
┌─────────────────────────────────────────────────────────────┐
│                        AI DLNK IDE                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   UI Login  │  │  AI Chat    │  │   Code Editor       │  │
│  │   (dLNk)    │  │  Interface  │  │   (VS Code Fork)    │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │            │
│  ┌──────┴────────────────┴─────────────────────┴──────┐     │
│  │              Unified AI Bridge                      │     │
│  │  (Antigravity gRPC → Jetski API)                   │     │
│  └──────────────────────┬─────────────────────────────┘     │
│                         │                                   │
│  ┌──────────────────────┴─────────────────────────────┐     │
│  │              Token Manager                          │     │
│  │  (Auto-refresh, Storage, Validation)               │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   License   │  │  Telegram   │  │   Admin Console     │  │
│  │   Server    │  │    Bot      │  │   (Flask/FastAPI)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Dependencies

### Python Packages
```
httpx[http2]
requests
customtkinter
pillow
cryptography
fastapi
uvicorn
python-telegram-bot
flask
pyotp
```

### System Requirements
- Python 3.11+
- VS Code (for fork base)
- SSL certificates for MITM proxy

---

## 🔐 Security Considerations

1. **Token Storage** - ใช้ Fernet encryption
2. **Admin Auth** - Session-based with 2FA support
3. **API Rate Limiting** - 60 RPM, 1000 RPD default
4. **License Validation** - SHA256 hash verification

---

## 📅 Next Steps

1. สร้าง VS Code Fork พร้อม branding AI DLNK
2. รวม UI Login จาก dLNk
3. เชื่อมต่อ Antigravity gRPC ผ่าน Jetski API
4. ตั้งค่า License Server และ Telegram Bot
5. ทดสอบระบบทั้งหมด
