# 🖥️ dLNk Admin Console

Desktop Application สำหรับจัดการ dLNk IDE พัฒนาด้วย Python CustomTkinter

## 📋 Features

### Dashboard
- แสดงสถิติการใช้งานแบบ Real-time
- Total Licenses, Active Users, Requests Today
- Top Users Today
- Recent Activity Log

### License Management
- ดูรายการ License ทั้งหมด
- สร้าง License ใหม่ (Trial, Basic, Pro, Enterprise, Admin)
- ต่ออายุ License (+30 วัน)
- ยกเลิก/Revoke License
- ค้นหาและกรอง License

### User Management
- ดูรายการผู้ใช้ทั้งหมด
- ดู Activity Log ของผู้ใช้
- Ban/Unban ผู้ใช้
- กรองตาม Status และ Role

### Log Viewer
- ดู C2 Logs (Prompt Requests)
- ดู Security Alerts
- กรองตาม Status และ Severity
- Export Logs

### Token Management
- ดู Antigravity Tokens
- Refresh Token
- Revoke Token
- ดูสถิติการใช้งาน Token

### Settings
- ตั้งค่า Telegram Bot
- ตั้งค่า Alert Thresholds
- ตั้งค่า API Endpoints
- ตั้งค่า Security (Session, Login Attempts, 2FA)

## 🚀 Installation

### Requirements
- Python 3.8+
- pip

### Install Dependencies

```bash
cd admin-console
pip install -r requirements.txt
```

### Run Application

```bash
python main.py
```

## 🔑 Login

ใช้ Admin Key เพื่อเข้าสู่ระบบ:

| Key Format | Role |
|------------|------|
| `DLNK-ADMIN-XXXX-XXXX-XXXX` | Admin |
| `DLNK-SUPER-XXXX-XXXX-XXXX` | Super Admin |
| `DLNK-DEV-XXXX-XXXX-XXXX` | Developer |

### Test Keys (Development)
- `DLNK-ADMIN-TEST-1234-5678` - Admin access
- `DLNK-SUPER-TEST-1234-5678` - Super Admin access

## 📁 Project Structure

```
admin-console/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── app/
│   ├── __init__.py
│   ├── app.py                 # Main application
│   ├── auth.py                # Admin authentication
│   └── api_client.py          # Backend API client
├── views/
│   ├── __init__.py
│   ├── login_view.py          # Login window
│   ├── dashboard_view.py      # Dashboard
│   ├── licenses_view.py       # License management
│   ├── users_view.py          # User management
│   ├── logs_view.py           # Log viewer
│   ├── tokens_view.py         # Token management
│   └── settings_view.py       # Settings
├── components/
│   ├── __init__.py
│   ├── sidebar.py             # Navigation sidebar
│   ├── header.py              # Top header
│   ├── table.py               # Data table
│   ├── chart.py               # Charts & stat cards
│   └── dialog.py              # Modal dialogs
├── utils/
│   ├── __init__.py
│   ├── theme.py               # Theme colors
│   └── helpers.py             # Helper functions
└── assets/
    ├── icons/
    └── fonts/
```

## 🎨 Theme

ใช้ Color Theme เดียวกับ dLNk IDE:

```python
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_tertiary': '#0f3460',
    'accent': '#e94560',
    'accent_secondary': '#533483',
    'success': '#00d9ff',
    'warning': '#ffc107',
    'error': '#ff4757',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'border': '#2d2d44'
}
```

## 🔗 API Integration

Admin Console เชื่อมต่อกับ Backend API:

| Endpoint | Description |
|----------|-------------|
| `/api/stats` | Dashboard statistics |
| `/api/licenses` | License management |
| `/api/users` | User management |
| `/api/logs` | C2 Logs |
| `/api/alerts` | Security alerts |
| `/api/tokens` | Token management |

### Environment Variables

```bash
DLNK_API_URL=http://localhost:5001
DLNK_TELEGRAM_BOT_TOKEN=your_bot_token
DLNK_TELEGRAM_ADMIN_ID=your_chat_id
```

## 📝 Dependencies

- **customtkinter** - Modern UI framework
- **pillow** - Image processing
- **requests** - HTTP client
- **matplotlib** - Charts (optional)
- **cryptography** - License encryption
- **pyotp** - 2FA support

## 🔒 Security

- Session-based authentication
- Admin Key validation
- Optional 2FA (TOTP)
- Session expiry (24 hours default)
- Rate limiting support

## 📄 License

Part of dLNk IDE Project

## 👨‍💻 Developer

AI-07 Admin Console Developer
