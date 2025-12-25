# dLNk IDE

**Intelligent Development Environment** - VS Code Fork with AI Integration

![dLNk Logo](dlnk_logo.png)

## Overview

dLNk IDE is a customized development environment based on VS Code, featuring:

- 🤖 **AI DLNK** - Integrated AI assistant powered by Jetski
- 🔐 **License Management** - Secure license key system
- 🌙 **Dark Mode UI** - Professional dark theme
- 👥 **Admin Console** - Web and Desktop management interface
- 🤖 **Telegram Bot** - Remote license management

## Components

### Core Files

| File | Description |
|------|-------------|
| `dlnk_launcher_v2.py` | Main launcher with login UI |
| `dlnk_ai_bridge.py` | AI Bridge service connecting to Jetski |
| `dlnk_license_system.py` | License management system |
| `dlnk_admin_web.py` | Web-based admin console |
| `dlnk_telegram_bot.py` | Telegram bot for remote management |

### Quick Start

1. **Install Dependencies**
```bash
pip install customtkinter pillow flask flask-cors websockets aiohttp cryptography python-telegram-bot
```

2. **Run the Launcher**
```bash
python dlnk_launcher_v2.py
```

3. **Start Admin Console (Web)**
```bash
python dlnk_admin_web.py --port 5001
```

4. **Start Telegram Bot**
```bash
python dlnk_telegram_bot.py --token YOUR_BOT_TOKEN
```

## License System

### Create a License

```bash
# Create a basic license for 30 days
python dlnk_license_system.py create-license --type basic --days 30 --owner "User Name"

# Create an encrypted license
python dlnk_license_system.py generate-encrypted --days 30 --owner "User Name"
```

### License Types

| Type | Features | Duration |
|------|----------|----------|
| Trial | Basic AI chat | 7 days |
| Basic | AI chat, Code assist, Dark mode | 30 days |
| Pro | All Basic + Advanced AI, Priority support | 90 days |
| Enterprise | All Pro + Custom branding, API access | 365 days |
| Admin | All features + Admin panel | Custom |

### Verify a License

```bash
python dlnk_license_system.py verify --key "DLNK-XXXX-XXXX-XXXX-XXXX"
```

## Admin Console

### Web Interface

Access the admin console at `http://localhost:5001`

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### Features

- 📊 Dashboard with statistics
- 🔑 License management (create, extend, revoke)
- 👥 User management
- 📝 Activity logs

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/stats` | View license statistics |
| `/licenses` | List all licenses |
| `/create [owner] [type] [days]` | Create new license |
| `/verify <key>` | Verify a license |
| `/revoke <key>` | Revoke a license |
| `/extend <key> [days]` | Extend license |
| `/quick` | Quick create with buttons |
| `/myid` | Get your Telegram ID |
| `/addadmin <id>` | Add admin by Telegram ID |

## AI Bridge

The AI Bridge connects dLNk IDE to the Jetski AI service.

### Endpoints

- **WebSocket**: `ws://localhost:8765` - Real-time chat
- **REST API**: `http://localhost:8766` - HTTP interface

### API Usage

```python
import requests

# Chat with AI
response = requests.post('http://localhost:8766/chat', json={
    'message': 'Hello AI',
    'context': []
})
print(response.json())
```

## Configuration

Configuration files are stored in `~/.dlnk-ide/`:

- `config.json` - User preferences
- `licenses.db` - SQLite database
- `telegram_bot_token.txt` - Telegram bot token
- `admin_telegram_ids.txt` - Admin Telegram IDs

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  dLNk Launcher  │────▶│  License System │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   dLNk IDE      │────▶│   AI Bridge     │
│  (VS Code Fork) │     │  (WebSocket)    │
└─────────────────┘     └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Jetski API    │
                        └─────────────────┘
```

## Security

- All license keys are encrypted using Fernet (AES-128)
- Hardware ID binding prevents license sharing
- Activity logging for audit trails
- Admin authentication required for management

## Support

- Telegram: [@dlnkai](https://t.me/dlnkai)
- Email: support@dlnk.dev

## Version

Current Version: **2.0.0**

---

© 2025 dLNk Team. All rights reserved.
