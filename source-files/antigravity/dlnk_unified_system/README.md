# 🚀 dLNk Unified System v3.0

**All-in-One AI IDE Solution** - รวม Antigravity + dLNk เป็นแอพเดียว

## ✨ Features

- **🔑 Token Management**: นำเข้า, จัดเก็บ, และ Auto-refresh token อัตโนมัติ
- **🤖 Multi-Provider AI**: Antigravity → Gemini → OpenAI → Ollama → Offline
- **💬 AI Chat Interface**: GUI และ CLI สำหรับสนทนากับ AI
- **🔧 VS Code Integration**: เปิด VS Code พร้อม Proxy อัตโนมัติ
- **📱 Telegram Bot**: จัดการ License ผ่าน Telegram
- **🌐 API Server**: OpenAI-compatible REST API

## 📦 Installation

```bash
# 1. Clone หรือ Download โปรเจ็ค

# 2. ติดตั้ง Dependencies
python setup.py install

# 3. ตั้งค่าระบบ
python setup.py configure

# 4. (Optional) สร้าง Shortcuts
python setup.py shortcuts

# หรือทำทั้งหมดในครั้งเดียว
python setup.py all
```

## 🚀 Quick Start

### GUI Mode (แนะนำ)

```bash
python dlnk_unified_launcher.py
```

### CLI Mode

```bash
python dlnk_unified_launcher.py --cli
```

### API Server

```bash
python -m uvicorn ai_gateway_server:app --host 0.0.0.0 --port 8000
```

## 🔑 Token Setup

### วิธีที่ 1: Import จากไฟล์

1. เปิด Launcher
2. ไปที่ Tab "🔑 Tokens"
3. คลิก "📥 Import Token from File"
4. เลือกไฟล์ `stolen_data_*.json`

### วิธีที่ 2: CLI

```bash
python dlnk_unified_launcher.py --cli
# พิมพ์: /import /path/to/stolen_data.json
```

### วิธีที่ 3: Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-key"
export OPENAI_API_KEY="your-openai-key"
export GROQ_API_KEY="your-groq-key"
```

## 📁 File Structure

```
dlnk_unified_system/
├── dlnk_unified_launcher.py   # Main launcher (GUI + CLI)
├── setup.py                   # Installation script
├── README.md                  # This file
└── requirements.txt           # Python dependencies

~/.dlnk/                       # User data directory
├── tokens/                    # Token storage
├── sessions/                  # Chat sessions
├── logs/                      # Log files
└── config.json               # Configuration
```

## 🔧 Configuration

ไฟล์ `~/.dlnk/config.json`:

```json
{
  "proxy_port": 8081,
  "license_server": "http://127.0.0.1:5000",
  "telegram_link": "https://t.me/dlnkai",
  "auto_refresh": true,
  "default_provider": "antigravity"
}
```

## 🤖 AI Providers Priority

1. **Antigravity** (ฟรี 100% - ต้องมี Token)
2. **Gemini** (ฟรี - มี Rate Limit)
3. **OpenAI** (ตามการตั้งค่า)
4. **Groq** (ฟรี - มี Rate Limit)
5. **Ollama** (ฟรี 100% - Local)
6. **Offline** (Fallback)

## 📱 Telegram Bot Commands

- `/start` - เริ่มต้นใช้งาน
- `สร้างคีย์` - สร้าง License Key
- `เขียนโค้ด` - ให้ AI เขียนโค้ด

## 🔒 Security Notes

- Token ถูกเก็บใน `~/.dlnk/tokens/` แบบ encrypted
- Auto-refresh ทำงานทุก 55 นาที (ก่อน token หมดอายุ)
- ไม่มีการส่งข้อมูลไปยัง server ภายนอก (ยกเว้น AI providers)

## 🆘 Troubleshooting

### Token ไม่ทำงาน

1. ตรวจสอบว่าไฟล์ `stolen_data.json` มี `access_token` และ `refresh_token`
2. ลอง Import ใหม่
3. ตรวจสอบ Internet connection

### VS Code ไม่เปิด

1. ตรวจสอบว่าติดตั้ง VS Code แล้ว
2. ลองเปิด VS Code ด้วยตนเองก่อน
3. ตรวจสอบ Path ใน Settings

### AI ไม่ตอบ

1. ตรวจสอบ Available Providers ใน Status
2. ตั้งค่า API Key สำหรับ Gemini/OpenAI
3. รัน Ollama local

## 📞 Support

- **Telegram**: [@dlnkai](https://t.me/dlnkai)
- **Issues**: GitHub Issues

## 📄 License

MIT License - Free for personal and commercial use.

---

**Made with ❤️ by dLNk Team**
