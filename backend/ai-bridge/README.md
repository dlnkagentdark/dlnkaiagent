# dLNk AI Bridge

> AI Bridge สำหรับ dLNk IDE - เชื่อมต่อ Antigravity/Jetski gRPC API พร้อม Fallback System

## 🎯 Features

- **gRPC Client** - เชื่อมต่อ Antigravity gRPC endpoint
- **Token Manager** - จัดการ OAuth token พร้อม auto-refresh
- **WebSocket Server** - สำหรับ Extension เชื่อมต่อ real-time (port 8765)
- **REST API Server** - สำหรับ Extension เรียกใช้ (port 8766)
- **Fallback System** - Antigravity → Gemini → OpenAI → Groq → Ollama

## 📁 โครงสร้างโปรเจค

```
ai-bridge/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt
├── README.md
├── grpc_client/
│   ├── __init__.py
│   ├── antigravity_client.py  # gRPC Client
│   ├── jetski_client.py       # Jetski API Client
│   └── proto_encoder.py       # Protocol Buffers encoder
├── token_manager/
│   ├── __init__.py
│   ├── token_store.py         # Token storage
│   ├── token_refresh.py       # Auto-refresh logic
│   └── encryption.py          # Fernet encryption
├── servers/
│   ├── __init__.py
│   ├── websocket_server.py    # WebSocket server (8765)
│   └── rest_server.py         # REST API server (8766)
├── fallback/
│   ├── __init__.py
│   ├── provider_manager.py    # Manage multiple providers
│   ├── gemini_client.py
│   ├── openai_client.py
│   ├── groq_client.py
│   └── ollama_client.py
└── utils/
    ├── __init__.py
    ├── logger.py
    └── helpers.py
```

## 🚀 Installation

```bash
# Clone or download the project
cd ai-bridge

# Install dependencies
pip install -r requirements.txt

# Run the bridge
python main.py
```

## ⚙️ Configuration

### Environment Variables

```bash
# Token Settings
export DLNK_ENCRYPTION_KEY="your-fernet-key"

# Fallback Providers (optional)
export GEMINI_API_KEY="your-gemini-key"
export OPENAI_API_KEY="your-openai-key"
export GROQ_API_KEY="your-groq-key"

# Server Settings (optional)
export DLNK_WS_HOST="127.0.0.1"
export DLNK_WS_PORT="8765"
export DLNK_REST_HOST="127.0.0.1"
export DLNK_REST_PORT="8766"

# Logging
export DLNK_LOG_LEVEL="INFO"
```

### Token Import

นำเข้า token จากไฟล์ JSON:

```python
from token_manager import TokenManager

manager = TokenManager()
manager.import_from_file("path/to/tokens.json")
```

รูปแบบไฟล์ token:
```json
{
  "access_token": "ya29.xxx...",
  "refresh_token": "1//xxx...",
  "client_secret": "GOCSPX-xxx..."
}
```

## 📡 API Reference

### WebSocket API (ws://localhost:8765)

#### Chat Message
```json
{
  "type": "chat",
  "id": "unique-id",
  "data": {
    "message": "Hello!",
    "system_prompt": "Optional system prompt",
    "conversation_id": "optional-conversation-id"
  }
}
```

#### Streaming Chat
```json
{
  "type": "chat_stream",
  "id": "unique-id",
  "data": {
    "message": "Hello!"
  }
}
```

#### Status Request
```json
{
  "type": "status",
  "id": "unique-id"
}
```

### REST API (http://localhost:8766)

#### POST /api/chat
```bash
curl -X POST http://localhost:8766/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "system_prompt": "You are helpful"}'
```

#### GET /api/status
```bash
curl http://localhost:8766/api/status
```

#### GET /api/providers
```bash
curl http://localhost:8766/api/providers
```

#### POST /api/token
```bash
curl -X POST http://localhost:8766/api/token \
  -H "Content-Type: application/json" \
  -d '{"access_token": "ya29.xxx", "refresh_token": "1//xxx"}'
```

## 🔄 Fallback Priority

1. **Antigravity** - Primary (ฟรี 100% ถ้ามี token)
2. **Gemini** - Secondary (ฟรี มี rate limit)
3. **OpenAI** - Tertiary (Paid)
4. **Groq** - Quaternary (ฟรี มี rate limit)
5. **Ollama** - Local (Offline capable)

## 🔐 Security

- Token เข้ารหัสด้วย Fernet symmetric encryption
- Token auto-refresh ทุก 55 นาที (ก่อน expire 5 นาที)
- รองรับ CORS สำหรับ Extension

## 📊 Monitoring

### Get Status
```python
bridge = AIBridge()
status = bridge.get_status()
print(status)
```

### Provider Stats
```python
stats = provider_manager.get_stats()
print(stats)
```

## 🧪 Testing

```bash
# Test WebSocket
python -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8765') as ws:
        await ws.send(json.dumps({
            'type': 'chat',
            'id': 'test-1',
            'data': {'message': 'Hello!'}
        }))
        response = await ws.recv()
        print(response)

asyncio.run(test())
"

# Test REST API
curl http://localhost:8766/api/status
```

## 📝 Dependencies

- Python 3.11+
- grpcio, grpcio-tools
- httpx[http2]
- websockets
- fastapi, uvicorn
- cryptography
- aiohttp, aiofiles

## 🤝 Integration

### VS Code Extension
```typescript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8765');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Send chat message
ws.send(JSON.stringify({
  type: 'chat',
  id: 'msg-1',
  data: { message: 'Hello AI!' }
}));
```

## 📄 License

MIT License - dLNk Team

---

**Developed by AI-05 AI Bridge Developer**
