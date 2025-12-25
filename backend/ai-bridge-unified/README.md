# dLNk AI Bridge - Antigravity Only Edition

> **No Limits • No Fallbacks • Free Forever**

ระบบเชื่อมต่อ dLNk IDE กับ Antigravity AI โดยตรง ไม่มี fallback providers อื่น (ไม่มี Gemini, OpenAI, Groq, Ollama)

## ✨ Features

- **Antigravity Only** - ใช้ Antigravity AI เท่านั้น ฟรี ไม่จำกัด
- **Auto Token Refresh** - รีเฟรช token อัตโนมัติทุก 55 นาที
- **WebSocket Server** - สำหรับ IDE Extension เชื่อมต่อ (port 8765)
- **REST API Server** - สำหรับ HTTP requests (port 8766)
- **Single File** - โค้ดทั้งหมดอยู่ในไฟล์เดียว รันจบในครั้งเดียว
- **Secure Token Storage** - เก็บ token แบบเข้ารหัส

## 📦 Installation

```bash
# 1. Clone หรือดาวน์โหลดโฟลเดอร์นี้

# 2. ติดตั้ง dependencies
pip3 install -r requirements.txt

# 3. รันโปรแกรม
python3 dlnk_antigravity_only.py
# หรือ
chmod +x run.sh && ./run.sh
```

## 🔑 Token Setup

### วิธีที่ 1: นำเข้าจากไฟล์ JSON

1. เปิด Antigravity และ login ด้วย Google Account
2. หา token file ที่:
   - Linux: `~/.config/antigravity/...`
   - Windows: `%APPDATA%/antigravity/...`
   - macOS: `~/Library/Application Support/antigravity/...`
3. คัดลอก `tokens.json` หรือ `oauth_credentials.json`
4. POST ไปที่ API:

```bash
curl -X POST http://127.0.0.1:8766/api/import-token \
  -H "Content-Type: application/json" \
  -d @tokens.json
```

### วิธีที่ 2: ใส่ token โดยตรง

```bash
curl -X POST http://127.0.0.1:8766/api/import-token \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "ya29.xxx...",
    "refresh_token": "1//xxx...",
    "client_secret": "GOCSPX-xxx..."
  }'
```

## 📡 API Endpoints

### REST API (http://127.0.0.1:8766)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | ข้อมูลเซิร์ฟเวอร์ |
| `/api/status` | GET | สถานะการเชื่อมต่อ |
| `/api/chat` | POST | ส่งข้อความไปยัง AI |
| `/api/import-token` | POST | นำเข้า tokens |

### WebSocket (ws://127.0.0.1:8765)

```javascript
// Connect
const ws = new WebSocket('ws://127.0.0.1:8765');

// Send chat message
ws.send(JSON.stringify({
  type: 'chat',
  message: 'สวัสดี',
  conversation_id: 'optional-id'
}));

// Receive response
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.content);
};
```

## 🔧 Configuration

ตั้งค่าผ่าน Environment Variables:

```bash
# Ports
export DLNK_WS_PORT=8765
export DLNK_REST_PORT=8766

# Host (default: 127.0.0.1)
export DLNK_WS_HOST=0.0.0.0
export DLNK_REST_HOST=0.0.0.0
```

## 📁 File Structure

```
dlnk_unified/
├── dlnk_antigravity_only.py  # Main application (single file)
├── requirements.txt          # Dependencies
├── run.sh                    # Run script
└── README.md                 # This file
```

## 🔒 Token Storage

Tokens จะถูกเก็บแบบเข้ารหัสที่:
```
~/.dlnk/tokens/
├── .encryption_key   # Encryption key (auto-generated)
└── tokens.enc        # Encrypted tokens
```

## 🚀 Usage Examples

### Python

```python
import requests

# Send chat message
response = requests.post('http://127.0.0.1:8766/api/chat', json={
    'message': 'เขียนโค้ด Python สำหรับ web scraping'
})
print(response.json()['content'])
```

### cURL

```bash
curl -X POST http://127.0.0.1:8766/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "สวัสดี"}'
```

### JavaScript

```javascript
fetch('http://127.0.0.1:8766/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'สวัสดี' })
})
.then(res => res.json())
.then(data => console.log(data.content));
```

## ⚠️ Troubleshooting

### "No valid access token available"
- ยังไม่ได้นำเข้า token
- Token หมดอายุ และไม่มี refresh_token
- กรุณานำเข้า token ใหม่

### "Token refresh failed"
- refresh_token หมดอายุ
- ไม่มี client_secret
- กรุณา login Antigravity ใหม่และนำเข้า token

### "Connection refused"
- ตรวจสอบว่า server กำลังรันอยู่
- ตรวจสอบ port ว่าถูกต้อง (8765, 8766)

## 📝 License

MIT License - Free to use and modify

## 🙏 Credits

- **Antigravity** by Google
- **dLNk Team** - Development

---

**dLNk IDE - No Limits AI**
