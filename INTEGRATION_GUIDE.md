# dLNk IDE - Integration Guide

## 📋 Overview

คู่มือนี้อธิบายวิธีการรวมระบบ (Integration) ของ dLNk IDE ทุก component

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        dLNk IDE                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │  VS Code    │────▶│  AI Bridge  │────▶│ Antigravity │       │
│  │  Extension  │     │  (Backend)  │     │   /Jetski   │       │
│  └─────────────┘     └──────┬──────┘     └─────────────┘       │
│         │                   │                                    │
│         │            ┌──────┴──────┐                            │
│         │            │             │                            │
│         │     ┌──────▼──────┐ ┌────▼─────┐                     │
│         │     │  Security   │ │ Fallback │                     │
│         │     │   Module    │ │ Providers│                     │
│         │     └─────────────┘ └──────────┘                     │
│         │                                                       │
│  ┌──────▼──────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   License   │────▶│    Admin    │────▶│  Telegram   │       │
│  │   System    │     │   Console   │     │    Bot      │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🔗 Integration Points

### 1. VS Code Extension → AI Bridge

**Protocol:** WebSocket (ws://localhost:8765) + REST API (http://localhost:8766)

```typescript
// Extension side
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'chat',
    id: 'msg-001',
    data: {
      message: 'Hello AI',
      system_prompt: 'You are a helpful assistant'
    }
  }));
};
```

### 2. AI Bridge → Security Module

**Location:** `/backend/ai-bridge/security_middleware.py`

```python
from security_middleware import get_security_middleware, filter_prompt

# Initialize
security = get_security_middleware()

# Filter prompt before processing
allowed, response, metadata = security.filter_prompt(
    prompt=user_message,
    user_id=user_id,
    ip_address=client_ip
)

if not allowed:
    return {"error": response, "blocked": True}
```

### 3. Extension → License System

**Protocol:** REST API (http://localhost:8088)

```typescript
// Validate license
const response = await fetch('http://localhost:8088/api/license/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    license_key: 'DLNK-XXXX-XXXX-XXXX',
    hardware_id: getHardwareId()
  })
});
```

### 4. Admin Console → License API

**Protocol:** REST API with Authentication

```python
import requests

# Admin login
response = requests.post('http://localhost:8088/api/auth/login', json={
    'username': 'admin',
    'password': 'password',
    'totp_code': '123456'  # 2FA
})

token = response.json()['token']

# Manage licenses
headers = {'Authorization': f'Bearer {token}'}
licenses = requests.get('http://localhost:8088/api/licenses', headers=headers)
```

### 5. Telegram Bot → All Services

```python
# Monitor AI Bridge
bridge_status = requests.get('http://localhost:8766/status')

# Monitor License System
license_status = requests.get('http://localhost:8088/api/health')

# Get Security Alerts
from security.alerts import AlertManager
alert_manager = AlertManager(bot_token=BOT_TOKEN, chat_id=CHAT_ID)
```

## 🚀 Startup Sequence

### 1. Start License System
```bash
cd backend/license
python main.py
# Runs on port 8088
```

### 2. Start AI Bridge
```bash
cd backend/ai-bridge
python main.py
# WebSocket: 8765, REST: 8766
```

### 3. Start Admin Console
```bash
cd admin-console
python main.py
# Runs on port 5000
```

### 4. Start Telegram Bot
```bash
cd telegram-bot
python main.py
```

### 5. Launch VS Code Extension
```bash
cd vscode-fork
# Build and launch
npm run build
```

## 📁 File Locations

| Component | Location | Main File |
|-----------|----------|-----------|
| VS Code Fork | `/vscode-fork/` | `product.json` |
| Extension | `/extension/` | `extension.ts` |
| AI Bridge | `/backend/ai-bridge/` | `main.py` |
| License System | `/backend/license/` | `main.py` |
| Admin Console | `/admin-console/` | `main.py` |
| Security Module | `/security/` | `main.py` |
| Telegram Bot | `/telegram-bot/` | `main.py` |
| UI Design | `/ui-design/` | Assets |
| Documentation | `/docs/` | All docs |

## ⚙️ Configuration

### Environment Variables

```bash
# AI Bridge
export ANTIGRAVITY_ENDPOINT="grpc://api.antigravity.ai:443"
export ANTIGRAVITY_TOKEN="your-token"
export WS_PORT=8765
export REST_PORT=8766

# License System
export LICENSE_DB_PATH="./data/licenses.db"
export LICENSE_API_PORT=8088
export JWT_SECRET="your-secret"

# Security
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="your-chat-id"

# Admin Console
export ADMIN_PORT=5000
export LICENSE_API_URL="http://localhost:8088"
```

### Config Files

- `/backend/ai-bridge/config.py` - AI Bridge configuration
- `/backend/license/config.py` - License system configuration
- `/security/config.py` - Security module configuration
- `/admin-console/config.py` - Admin console configuration

## 🧪 Testing Integration

### Test AI Bridge + Security
```bash
cd backend/ai-bridge
python -c "
from security_middleware import filter_prompt
allowed, response, meta = filter_prompt('hack dlnk', 'test-user')
print(f'Allowed: {allowed}, Response: {response}')
"
```

### Test License API
```bash
curl -X POST http://localhost:8088/api/license/validate \
  -H 'Content-Type: application/json' \
  -d '{"license_key": "TEST-KEY", "hardware_id": "test-hw"}'
```

### Test WebSocket
```bash
python -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8765') as ws:
        await ws.send(json.dumps({
            'type': 'status',
            'id': 'test-001',
            'data': {}
        }))
        response = await ws.recv()
        print(response)

asyncio.run(test())
"
```

## 📊 Health Checks

| Service | Endpoint | Expected |
|---------|----------|----------|
| AI Bridge WS | `ws://localhost:8765` | Connected |
| AI Bridge REST | `http://localhost:8766/health` | `{"status": "ok"}` |
| License API | `http://localhost:8088/api/health` | `{"status": "ok"}` |
| Admin Console | `http://localhost:5000/health` | `{"status": "ok"}` |

## 🔒 Security Considerations

1. **All internal communication** should use localhost only
2. **External access** requires proper firewall configuration
3. **API tokens** must be stored securely (encrypted)
4. **2FA** is required for admin access
5. **Rate limiting** is enabled by default

## 📝 Troubleshooting

### Connection Refused
- Check if service is running
- Verify port is not in use
- Check firewall settings

### Authentication Failed
- Verify token is valid
- Check token expiration
- Ensure 2FA code is correct

### Security Module Not Working
- Verify security module is installed
- Check import paths
- Review logs for errors

---

**dLNk IDE - No Limits AI**  
**Integration Guide v1.0**
