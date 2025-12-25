# 🤖 dLNk Telegram Admin Bot

Telegram Bot สำหรับจัดการ dLNk IDE - ระบบจัดการ License, Users และ System Monitoring

## 📋 Features

### Command Handlers
- `/start` - เริ่มต้นใช้งาน Bot
- `/help` - แสดงคำสั่งที่ใช้ได้
- `/status` - ดูสถานะระบบ
- `/users` - ดูสถิติผู้ใช้
- `/licenses` - ดูสถิติ License
- `/logs` - ดู Recent logs
- `/ban [user_id]` - Ban ผู้ใช้
- `/unban [user_id]` - Unban ผู้ใช้
- `/revoke [license_key]` - Revoke License
- `/extend [license_key] [days]` - ต่ออายุ License
- `/verify [license_key]` - ตรวจสอบ License
- `/create [owner] [type] [days]` - สร้าง License ใหม่
- `/quick` - Quick Create License Menu
- `/alert` - ตั้งค่าการแจ้งเตือน
- `/myid` - ดู Telegram ID ของตัวเอง
- `/addadmin [user_id]` - เพิ่ม Admin
- `/removeadmin [user_id]` - ลบ Admin
- `/broadcast [message]` - ส่งข้อความถึง Admin ทุกคน
- `/search [query]` - ค้นหา Users/Licenses

### Inline Queries
- `@bot user [query]` - ค้นหาผู้ใช้
- `@bot license [query]` - ค้นหา License
- `@bot log [query]` - ค้นหา Logs

### Notification System
- Security Alerts
- License Notifications
- System Status Alerts
- Daily Summary Reports
- Expiring License Alerts

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.9+
- Telegram Bot Token (จาก @BotFather)

### 2. Installation

```bash
# Clone หรือ copy โฟลเดอร์ telegram-bot

# ติดตั้ง dependencies
pip install -r requirements.txt

# Copy และแก้ไข environment variables
cp .env.example .env
nano .env
```

### 3. Configuration

แก้ไขไฟล์ `.env`:

```env
# Required
DLNK_TELEGRAM_BOT_TOKEN=your_bot_token_here
DLNK_ADMIN_CHAT_IDS=123456789,987654321

# Backend API
DLNK_BACKEND_URL=http://localhost:8000
DLNK_API_KEY=your_api_key

# Optional
DLNK_ALERT_ENABLED=true
DLNK_LOG_LEVEL=INFO
```

### 4. Run

```bash
python main.py
```

## 📁 Project Structure

```
telegram-bot/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example              # Environment template
├── README.md                 # Documentation
├── bot/
│   ├── __init__.py
│   ├── bot.py                # Main bot class
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py       # Command handlers
│   │   ├── callbacks.py      # Callback handlers
│   │   └── inline.py         # Inline query handlers
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── main_menu.py      # Reply keyboards
│   │   └── inline.py         # Inline keyboards
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py           # Admin authentication
│       └── rate_limit.py     # Rate limiting
├── notifications/
│   ├── __init__.py
│   ├── alert_sender.py       # Send alerts
│   ├── templates.py          # Message templates
│   └── scheduler.py          # Scheduled notifications
├── api_client/
│   ├── __init__.py
│   └── backend.py            # Backend API client
└── utils/
    ├── __init__.py
    └── helpers.py            # Utility functions
```

## 🔒 Security

### Admin Authentication
- เฉพาะ Admin ที่ระบุใน `DLNK_ADMIN_CHAT_IDS` เท่านั้นที่ใช้คำสั่ง Admin ได้
- ถ้าไม่มี Admin ที่กำหนด ทุกคนจะเป็น Admin (สำหรับ setup ครั้งแรก)

### Rate Limiting
- จำกัด 30 ข้อความ/นาที ต่อผู้ใช้
- Cooldown 60 วินาที หลังเกิน Rate Limit

## 🔧 Development

### Adding New Commands

1. เพิ่ม handler ใน `bot/handlers/commands.py`:

```python
@router.message(Command("mycommand"))
async def cmd_mycommand(message: Message):
    await message.answer("Hello!")
```

2. ถ้าต้องการ Admin only ให้เพิ่มใน `ADMIN_COMMANDS` ที่ `bot/middleware/auth.py`

### Adding New Keyboards

เพิ่มใน `bot/keyboards/inline.py`:

```python
def get_my_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Button", callback_data="my_action")]
    ])
```

### Adding New Notifications

เพิ่มใน `notifications/templates.py`:

```python
@staticmethod
def my_notification(data: dict) -> str:
    return f"📢 <b>Title</b>\n\n{data['message']}"
```

## 📊 API Integration

Bot เชื่อมต่อกับ Backend API ผ่าน `api_client/backend.py`:

```python
from api_client import BackendAPIClient

client = BackendAPIClient()
users = await client.get_users()
```

## 🐛 Troubleshooting

### Bot ไม่ตอบ
1. ตรวจสอบ Bot Token ถูกต้อง
2. ตรวจสอบ Bot ไม่ถูก block
3. ดู logs: `DLNK_LOG_LEVEL=DEBUG python main.py`

### Rate Limit
- รอ 60 วินาที แล้วลองใหม่
- หรือ Admin สามารถ reset ได้

### API Connection Failed
- ตรวจสอบ `DLNK_BACKEND_URL` ถูกต้อง
- ตรวจสอบ Backend กำลังทำงาน

## 📝 License

MIT License - dLNk IDE Project

## 👥 Contact

- AI-01 Controller: สำหรับรายงานปัญหา
- AI-09 Telegram Bot Developer: สำหรับพัฒนาเพิ่มเติม
