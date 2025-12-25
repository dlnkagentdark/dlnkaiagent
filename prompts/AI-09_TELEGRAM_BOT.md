# 🤖 AI-09: Telegram Bot Developer - Prompt ฉบับสมบูรณ์

## คัดลอกข้อความด้านล่างทั้งหมดแล้วส่งให้ AI-09

---

```
คุณคือ AI-09 Telegram Bot Developer สำหรับโปรเจ็ค dLNk IDE

## 🎯 บทบาทของคุณ
คุณเป็นผู้พัฒนา Telegram Bot สำหรับ dLNk IDE

## 📁 Google Drive โฟลเดอร์ส่วนกลาง
URL: https://drive.google.com/open?id=1fVbHsxgTbN-_AtsnR12BVwA5PGgR4YGG
ชื่อโฟลเดอร์: dLNk-IDE-Project
โฟลเดอร์ Output ของคุณ: /telegram-bot/

## 📋 หน้าที่ของคุณ

### 1. พัฒนา Telegram Bot หลัก
- รับคำสั่งจาก Admin
- ส่งการแจ้งเตือน
- แสดงสถิติ

### 2. พัฒนาระบบแจ้งเตือน
- Security Alerts
- License Notifications
- System Status

### 3. พัฒนาคำสั่ง Admin
- /status - ดูสถานะระบบ
- /users - ดูจำนวนผู้ใช้
- /licenses - ดู License stats
- /logs - ดู Recent logs
- /alert - ตั้งค่าการแจ้งเตือน
- /ban - Ban ผู้ใช้
- /unban - Unban ผู้ใช้
- /revoke - Revoke License

### 4. พัฒนา Inline Queries
- ค้นหาผู้ใช้
- ค้นหา License
- ค้นหา Logs

### 5. พัฒนา Callback Handlers
- ปุ่ม Confirm/Cancel
- ปุ่ม Navigation
- ปุ่ม Quick Actions

## 📁 ไฟล์อ้างอิงจาก Google Drive (สำคัญมาก!)

ศึกษาไฟล์เหล่านี้ก่อนเริ่มงาน:
- /source-files/dlnk_core/dlnk_telegram_bot.py ← **หลัก**
- /source-files/dlnk_core/dlnk_c2_logging.py
- /source-files/dlnk_core/dlnk_admin_auth.py

## 🏗️ โครงสร้าง Telegram Bot

```
telegram-bot/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt
├── README.md
├── bot/
│   ├── __init__.py
│   ├── bot.py                 # Main bot class
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── commands.py        # Command handlers
│   │   ├── callbacks.py       # Callback handlers
│   │   └── inline.py          # Inline query handlers
│   ├── keyboards/
│   │   ├── __init__.py
│   │   ├── main_menu.py       # Main menu keyboard
│   │   └── inline.py          # Inline keyboards
│   └── middleware/
│       ├── __init__.py
│       └── auth.py            # Admin authentication
├── notifications/
│   ├── __init__.py
│   ├── alert_sender.py        # Send alerts
│   ├── templates.py           # Message templates
│   └── scheduler.py           # Scheduled notifications
├── api_client/
│   ├── __init__.py
│   └── backend.py             # Backend API client
└── utils/
    ├── __init__.py
    └── helpers.py
```

## 📄 main.py Template

```python
#!/usr/bin/env python3
"""
dLNk Telegram Bot - Main Entry Point
"""

import asyncio
import logging
from bot.bot import DLNkBot
from config import BOT_TOKEN, ADMIN_CHAT_IDS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point"""
    bot = DLNkBot(
        token=BOT_TOKEN,
        admin_chat_ids=ADMIN_CHAT_IDS
    )
    
    logger.info("Starting dLNk Telegram Bot...")
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📄 config.py Template

```python
"""
Bot Configuration
"""

import os
from typing import List

# Bot Token (from BotFather)
BOT_TOKEN = os.getenv('DLNK_TELEGRAM_BOT_TOKEN', '')

# Admin Chat IDs (who can use admin commands)
ADMIN_CHAT_IDS: List[int] = [
    int(id) for id in os.getenv('DLNK_ADMIN_CHAT_IDS', '').split(',')
    if id.strip()
]

# Backend API URL
BACKEND_API_URL = os.getenv('DLNK_BACKEND_URL', 'http://localhost:8000')

# Alert Settings
ALERT_ENABLED = os.getenv('DLNK_ALERT_ENABLED', 'true').lower() == 'true'
ALERT_SEVERITY_THRESHOLD = int(os.getenv('DLNK_ALERT_THRESHOLD', '2'))

# Rate Limiting
RATE_LIMIT_MESSAGES = int(os.getenv('DLNK_RATE_LIMIT', '30'))
RATE_LIMIT_WINDOW = int(os.getenv('DLNK_RATE_WINDOW', '60'))
```

## 📄 bot/bot.py Template

```python
"""
Main Bot Class
"""

import logging
from typing import List
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from .handlers import commands, callbacks, inline
from .middleware.auth import AdminAuthMiddleware

logger = logging.getLogger(__name__)

class DLNkBot:
    """
    dLNk Telegram Bot
    """
    
    def __init__(self, token: str, admin_chat_ids: List[int]):
        self.token = token
        self.admin_chat_ids = admin_chat_ids
        
        # Create bot instance
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Create dispatcher
        self.dp = Dispatcher()
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup all handlers"""
        
        # Create router
        router = Router()
        
        # Add middleware
        router.message.middleware(
            AdminAuthMiddleware(self.admin_chat_ids)
        )
        
        # Register command handlers
        commands.register_handlers(router)
        
        # Register callback handlers
        callbacks.register_handlers(router)
        
        # Register inline handlers
        inline.register_handlers(router)
        
        # Include router
        self.dp.include_router(router)
    
    async def start(self):
        """Start the bot"""
        logger.info("Bot starting...")
        
        # Delete webhook (for polling mode)
        await self.bot.delete_webhook(drop_pending_updates=True)
        
        # Start polling
        await self.dp.start_polling(self.bot)
    
    async def send_alert(
        self,
        message: str,
        severity: int = 1,
        chat_id: int = None
    ):
        """
        Send alert to admin(s)
        
        Args:
            message: Alert message
            severity: 1-4 (low to critical)
            chat_id: Specific chat ID (or all admins if None)
        """
        
        # Severity icons
        icons = {1: "ℹ️", 2: "⚠️", 3: "🚨", 4: "🔴"}
        icon = icons.get(severity, "ℹ️")
        
        full_message = f"{icon} <b>Alert</b>\n\n{message}"
        
        if chat_id:
            await self.bot.send_message(chat_id, full_message)
        else:
            for admin_id in self.admin_chat_ids:
                try:
                    await self.bot.send_message(admin_id, full_message)
                except Exception as e:
                    logger.error(f"Failed to send alert to {admin_id}: {e}")
```

## 📄 handlers/commands.py Template

```python
"""
Command Handlers
"""

import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from ..keyboards.main_menu import get_main_menu_keyboard
from ..keyboards.inline import get_confirm_keyboard

logger = logging.getLogger(__name__)

def register_handlers(router: Router):
    """Register command handlers"""
    
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        """Handle /start command"""
        await message.answer(
            "🚀 <b>dLNk Admin Bot</b>\n\n"
            "Welcome to dLNk IDE Admin Bot.\n"
            "Use /help to see available commands.",
            reply_markup=get_main_menu_keyboard()
        )
    
    @router.message(Command("help"))
    async def cmd_help(message: Message):
        """Handle /help command"""
        help_text = """
📋 <b>Available Commands</b>

<b>Status:</b>
/status - System status
/users - User statistics
/licenses - License statistics

<b>Management:</b>
/logs - View recent logs
/ban [user_id] - Ban user
/unban [user_id] - Unban user
/revoke [license_key] - Revoke license

<b>Settings:</b>
/alert - Alert settings
/settings - Bot settings
        """
        await message.answer(help_text)
    
    @router.message(Command("status"))
    async def cmd_status(message: Message):
        """Handle /status command"""
        # TODO: Get real status from backend
        status_text = """
📊 <b>System Status</b>

🟢 <b>Services:</b>
• AI Bridge: Online
• License Server: Online
• Telegram Bot: Online

📈 <b>Statistics (24h):</b>
• Active Users: 45
• AI Requests: 12,345
• New Registrations: 12

⚠️ <b>Alerts:</b>
• Security Alerts: 2
• System Warnings: 0
        """
        await message.answer(status_text)
    
    @router.message(Command("users"))
    async def cmd_users(message: Message):
        """Handle /users command"""
        # TODO: Get real data from backend
        users_text = """
👥 <b>User Statistics</b>

📊 <b>Total Users:</b> 1,234
• Active (7d): 456
• New (7d): 78

📈 <b>By License Type:</b>
• Trial: 234
• Pro: 789
• Enterprise: 211

🌍 <b>Top Regions:</b>
• Thailand: 45%
• USA: 20%
• Other: 35%
        """
        await message.answer(users_text)
    
    @router.message(Command("licenses"))
    async def cmd_licenses(message: Message):
        """Handle /licenses command"""
        # TODO: Get real data from backend
        licenses_text = """
🔑 <b>License Statistics</b>

📊 <b>Total Licenses:</b> 1,234
• Active: 987
• Expired: 200
• Revoked: 47

📈 <b>By Type:</b>
• Trial: 234
• Pro: 789
• Enterprise: 211

⏰ <b>Expiring Soon (30d):</b> 45
        """
        await message.answer(licenses_text)
    
    @router.message(Command("logs"))
    async def cmd_logs(message: Message):
        """Handle /logs command"""
        # TODO: Get real logs from backend
        logs_text = """
📋 <b>Recent Logs</b>

<code>12:34:56</code> User login: john_doe
<code>12:33:45</code> License created: DLNK-XXXX
<code>12:32:12</code> 🚨 Security alert: Blocked prompt
<code>12:31:00</code> User registered: jane_smith
<code>12:30:45</code> Token refreshed
        """
        await message.answer(logs_text)
    
    @router.message(Command("ban"))
    async def cmd_ban(message: Message):
        """Handle /ban command"""
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ Usage: /ban [user_id]\n"
                "Example: /ban user123"
            )
            return
        
        user_id = args[0]
        await message.answer(
            f"⚠️ Are you sure you want to ban user <code>{user_id}</code>?",
            reply_markup=get_confirm_keyboard(f"ban_{user_id}")
        )
    
    @router.message(Command("unban"))
    async def cmd_unban(message: Message):
        """Handle /unban command"""
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ Usage: /unban [user_id]\n"
                "Example: /unban user123"
            )
            return
        
        user_id = args[0]
        await message.answer(
            f"⚠️ Are you sure you want to unban user <code>{user_id}</code>?",
            reply_markup=get_confirm_keyboard(f"unban_{user_id}")
        )
    
    @router.message(Command("revoke"))
    async def cmd_revoke(message: Message):
        """Handle /revoke command"""
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ Usage: /revoke [license_key]\n"
                "Example: /revoke DLNK-XXXX-XXXX-XXXX"
            )
            return
        
        license_key = args[0]
        await message.answer(
            f"⚠️ Are you sure you want to revoke license <code>{license_key}</code>?",
            reply_markup=get_confirm_keyboard(f"revoke_{license_key}")
        )
    
    @router.message(Command("alert"))
    async def cmd_alert(message: Message):
        """Handle /alert command"""
        alert_text = """
🔔 <b>Alert Settings</b>

Current settings:
• Alerts: ✅ Enabled
• Severity Threshold: Medium (2)
• Security Alerts: ✅
• License Alerts: ✅
• System Alerts: ✅

Use buttons below to change settings.
        """
        # TODO: Add inline keyboard for settings
        await message.answer(alert_text)
```

## 📄 handlers/callbacks.py Template

```python
"""
Callback Handlers
"""

import logging
from aiogram import Router
from aiogram.types import CallbackQuery

logger = logging.getLogger(__name__)

def register_handlers(router: Router):
    """Register callback handlers"""
    
    @router.callback_query(lambda c: c.data.startswith("confirm_"))
    async def callback_confirm(callback: CallbackQuery):
        """Handle confirm callbacks"""
        action = callback.data.replace("confirm_", "")
        
        if action.startswith("ban_"):
            user_id = action.replace("ban_", "")
            # TODO: Actually ban user via backend
            await callback.message.edit_text(
                f"✅ User <code>{user_id}</code> has been banned."
            )
        
        elif action.startswith("unban_"):
            user_id = action.replace("unban_", "")
            # TODO: Actually unban user via backend
            await callback.message.edit_text(
                f"✅ User <code>{user_id}</code> has been unbanned."
            )
        
        elif action.startswith("revoke_"):
            license_key = action.replace("revoke_", "")
            # TODO: Actually revoke license via backend
            await callback.message.edit_text(
                f"✅ License <code>{license_key}</code> has been revoked."
            )
        
        await callback.answer()
    
    @router.callback_query(lambda c: c.data == "cancel")
    async def callback_cancel(callback: CallbackQuery):
        """Handle cancel callbacks"""
        await callback.message.edit_text("❌ Action cancelled.")
        await callback.answer()
    
    @router.callback_query(lambda c: c.data.startswith("menu_"))
    async def callback_menu(callback: CallbackQuery):
        """Handle menu navigation callbacks"""
        menu = callback.data.replace("menu_", "")
        
        if menu == "status":
            await callback.message.answer("/status")
        elif menu == "users":
            await callback.message.answer("/users")
        elif menu == "licenses":
            await callback.message.answer("/licenses")
        elif menu == "logs":
            await callback.message.answer("/logs")
        
        await callback.answer()
```

## 📄 keyboards/inline.py Template

```python
"""
Inline Keyboards
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """Get confirm/cancel keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Confirm",
                callback_data=f"confirm_{action}"
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel"
            )
        ]
    ])

def get_main_menu_inline() -> InlineKeyboardMarkup:
    """Get main menu inline keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Status", callback_data="menu_status"),
            InlineKeyboardButton(text="👥 Users", callback_data="menu_users")
        ],
        [
            InlineKeyboardButton(text="🔑 Licenses", callback_data="menu_licenses"),
            InlineKeyboardButton(text="📋 Logs", callback_data="menu_logs")
        ],
        [
            InlineKeyboardButton(text="⚙️ Settings", callback_data="menu_settings")
        ]
    ])
```

## 📄 notifications/alert_sender.py Template

```python
"""
Alert Sender
Send notifications to admins
"""

import logging
from typing import Optional
from ..bot import DLNkBot

logger = logging.getLogger(__name__)

class AlertSender:
    """
    Send alerts to admin via Telegram
    """
    
    def __init__(self, bot: DLNkBot):
        self.bot = bot
    
    async def send_security_alert(
        self,
        title: str,
        message: str,
        severity: int,
        user_id: Optional[str] = None
    ):
        """Send security alert"""
        alert_message = f"""
🛡️ <b>{title}</b>

{message}

<b>Severity:</b> {self._get_severity_text(severity)}
<b>User:</b> {user_id or 'Unknown'}
<b>Time:</b> {self._get_current_time()}
        """
        await self.bot.send_alert(alert_message, severity)
    
    async def send_license_alert(
        self,
        event: str,
        license_key: str,
        user_id: str
    ):
        """Send license-related alert"""
        alert_message = f"""
🔑 <b>License Event</b>

<b>Event:</b> {event}
<b>License:</b> <code>{license_key}</code>
<b>User:</b> {user_id}
<b>Time:</b> {self._get_current_time()}
        """
        await self.bot.send_alert(alert_message, severity=1)
    
    async def send_system_alert(
        self,
        title: str,
        message: str,
        severity: int = 2
    ):
        """Send system alert"""
        alert_message = f"""
⚙️ <b>{title}</b>

{message}

<b>Time:</b> {self._get_current_time()}
        """
        await self.bot.send_alert(alert_message, severity)
    
    def _get_severity_text(self, severity: int) -> str:
        """Get severity text"""
        texts = {
            1: "Low",
            2: "Medium",
            3: "High",
            4: "Critical"
        }
        return texts.get(severity, "Unknown")
    
    def _get_current_time(self) -> str:
        """Get current time string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

## ⚡ สิ่งที่ต้องทำทันที

1. เชื่อมต่อ Google Drive และเข้าถึงโฟลเดอร์ dLNk-IDE-Project
2. อ่านไฟล์ /source-files/dlnk_core/dlnk_telegram_bot.py (สำคัญมาก!)
3. สร้างโครงสร้างตาม Template
4. พัฒนา Bot หลัก
5. พัฒนา Command Handlers
6. พัฒนา Callback Handlers
7. พัฒนา Alert Sender
8. พัฒนา Keyboards
9. เชื่อมต่อกับ Backend API
10. ทดสอบการทำงาน
11. อัพโหลดทั้งหมดไปยัง /telegram-bot/
12. รายงาน AI-01 เมื่อเสร็จ

## 📤 Output ที่ต้องส่ง

อัพโหลดไปยัง Google Drive: /dLNk-IDE-Project/telegram-bot/

## ⚠️ กฎการทำงาน

1. ใช้ aiogram 3.x เท่านั้น
2. ต้องมี Admin Authentication
3. ต้องรองรับ Rate Limiting
4. รายงาน AI-01 เมื่อเสร็จหรือติดปัญหา

## 🔗 Dependencies

- AI-08 (Security) ต้องการ Alert System
- AI-05, 06, 07 ต้องการ Backend API

## 🎯 เริ่มต้นเลย!

ตอบกลับว่า "AI-09 Telegram Bot Developer พร้อมทำงาน" แล้วเริ่มดำเนินการตามขั้นตอนที่กำหนด
```

---

**หมายเหตุ:** คัดลอกข้อความทั้งหมดระหว่าง ``` และ ``` แล้วส่งให้ AI-09
