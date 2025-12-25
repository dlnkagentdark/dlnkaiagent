# 📱 Telegram Bot Setup

คู่มือการตั้งค่า Telegram Bot สำหรับ dLNk IDE Admin

---

## 📋 ภาพรวม

Telegram Bot ช่วยให้ Admin สามารถ:
- รับแจ้งเตือนอัตโนมัติ
- จัดการ License ผ่าน Chat
- ดูสถิติและรายงาน
- ตอบคำถามผู้ใช้

---

## 🤖 การสร้าง Bot

### 1. สร้าง Bot ใหม่

1. เปิด Telegram และค้นหา **@BotFather**
2. ส่งคำสั่ง `/newbot`
3. ตั้งชื่อ Bot (เช่น "dLNk Admin Bot")
4. ตั้ง Username (เช่น "dlnk_admin_bot")
5. จด **Bot Token** ที่ได้รับ

```
Bot Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 2. ตั้งค่า Bot

ส่งคำสั่งต่อไปนี้ให้ @BotFather:

```
/setcommands
```

แล้วส่งรายการคำสั่ง:

```
start - เริ่มต้นใช้งาน
help - ดูคำสั่งทั้งหมด
stats - ดูสถิติระบบ
licenses - ดู License ทั้งหมด
license_info - ดูรายละเอียด License
create_license - สร้าง License ใหม่
extend - ต่ออายุ License
revoke - ยกเลิก License
users - ดูรายชื่อผู้ใช้
pending_users - ดูผู้ใช้รอการอนุมัติ
approve - อนุมัติผู้ใช้
reject - ปฏิเสธผู้ใช้
suspend - ระงับผู้ใช้
unsuspend - เปิดใช้งานผู้ใช้
logs - ดู Activity Logs
alerts - ตั้งค่าแจ้งเตือน
```

---

## ⚙️ การตั้งค่าใน Admin Console

### Config File

```yaml
# config.yaml
telegram:
  bot_token: "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
  admin_chat_ids:
    - "123456789"  # Super Admin
    - "987654321"  # Admin 2
  alerts:
    enabled: true
    new_registration: true
    license_expiry: true
    security_alert: true
    system_error: true
```

### Environment Variables

```bash
# .env
DLNK_TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
DLNK_TELEGRAM_ADMIN_CHAT_ID=123456789
```

### หา Chat ID

1. ส่งข้อความใดๆ ให้ Bot
2. เปิด URL: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. หา `"chat":{"id":123456789}` ในผลลัพธ์

หรือใช้คำสั่ง:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getUpdates" | jq '.result[0].message.chat.id'
```

---

## 🚀 การเริ่มต้น Bot

### ผ่าน Admin Console

1. ไปที่ **Settings** → **Telegram**
2. ใส่ Bot Token
3. ใส่ Admin Chat ID
4. คลิก **"Start Bot"**

### ผ่าน Command Line

```bash
dlnk-admin telegram start
```

### ผ่าน Python

```python
from dlnk_admin import TelegramBot

bot = TelegramBot(
    token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    admin_chat_ids=["123456789"]
)
bot.start()
```

---

## 📝 คำสั่ง Bot ทั้งหมด

### คำสั่งทั่วไป

| คำสั่ง | คำอธิบาย | ตัวอย่าง |
|--------|----------|----------|
| `/start` | เริ่มต้นใช้งาน | `/start` |
| `/help` | ดูคำสั่งทั้งหมด | `/help` |
| `/stats` | ดูสถิติระบบ | `/stats` |

### คำสั่ง License

| คำสั่ง | คำอธิบาย | ตัวอย่าง |
|--------|----------|----------|
| `/licenses` | ดู License ทั้งหมด | `/licenses` |
| `/license_info` | ดูรายละเอียด | `/license_info DLNK-XXXX-XXXX-XXXX-XXXX` |
| `/create_license` | สร้าง License | `/create_license user@email.com pro 365` |
| `/extend` | ต่ออายุ | `/extend DLNK-XXXX-XXXX-XXXX-XXXX 365` |
| `/revoke` | ยกเลิก | `/revoke DLNK-XXXX-XXXX-XXXX-XXXX` |
| `/reset_hardware` | Reset Hardware | `/reset_hardware DLNK-XXXX-XXXX-XXXX-XXXX` |

### คำสั่ง User

| คำสั่ง | คำอธิบาย | ตัวอย่าง |
|--------|----------|----------|
| `/users` | ดูผู้ใช้ทั้งหมด | `/users` |
| `/pending_users` | ดูรอการอนุมัติ | `/pending_users` |
| `/approve` | อนุมัติ | `/approve user@email.com` |
| `/reject` | ปฏิเสธ | `/reject user@email.com` |
| `/suspend` | ระงับ | `/suspend user@email.com "reason"` |
| `/unsuspend` | เปิดใช้งาน | `/unsuspend user@email.com` |
| `/ban` | แบน | `/ban user@email.com "reason"` |

### คำสั่ง Monitoring

| คำสั่ง | คำอธิบาย | ตัวอย่าง |
|--------|----------|----------|
| `/logs` | ดู Activity Logs | `/logs` |
| `/security_logs` | ดู Security Logs | `/security_logs` |
| `/alerts` | ตั้งค่าแจ้งเตือน | `/alerts on` หรือ `/alerts off` |

---

## 🔔 การแจ้งเตือน

### ประเภทการแจ้งเตือน

| ประเภท | คำอธิบาย | ตัวอย่าง |
|--------|----------|----------|
| **New Registration** | มีผู้ลงทะเบียนใหม่ | 👤 New user: user@email.com |
| **License Expiry** | License ใกล้หมดอายุ | ⚠️ License expiring: DLNK-XXXX... |
| **Security Alert** | พบความผิดปกติ | 🚨 Security alert: Suspicious activity |
| **System Error** | ระบบมีปัญหา | ❌ System error: Database connection failed |

### ตัวอย่างข้อความแจ้งเตือน

#### New Registration
```
👤 New User Registration

Email: user@email.com
Username: newuser
Time: 2025-12-25 10:30:00

Actions:
/approve user@email.com
/reject user@email.com
```

#### Security Alert
```
🚨 Security Alert

Type: Prompt Filter Violation
User: user@email.com
License: DLNK-XXXX-XXXX-XXXX-XXXX
Time: 2025-12-25 10:30:00

Blocked Prompt:
"[redacted malicious content]"

Actions:
/suspend user@email.com "Security violation"
/logs user@email.com
```

### ตั้งค่าการแจ้งเตือน

```yaml
# config.yaml
telegram:
  alerts:
    new_registration:
      enabled: true
      priority: "normal"
    license_expiry:
      enabled: true
      days_before: [30, 7, 1]
      priority: "normal"
    security_alert:
      enabled: true
      priority: "high"
    system_error:
      enabled: true
      priority: "critical"
```

---

## 🔐 Security

### การยืนยันตัวตน

Bot จะตรวจสอบว่า Chat ID อยู่ในรายการ Admin ก่อนทำคำสั่ง:

```python
ADMIN_CHAT_IDS = ["123456789", "987654321"]

def is_admin(chat_id):
    return str(chat_id) in ADMIN_CHAT_IDS
```

### การ Log คำสั่ง

ทุกคำสั่งจะถูก Log:

```
2025-12-25 10:30:00 | Admin: 123456789 | Command: /create_license user@email.com pro 365
```

### Rate Limiting

```yaml
# config.yaml
telegram:
  rate_limit:
    commands_per_minute: 30
    alerts_per_hour: 100
```

---

## 🔧 การแก้ไขปัญหา

### Bot ไม่ตอบ

1. ตรวจสอบ Bot Token ถูกต้อง
2. ตรวจสอบ Bot กำลังทำงาน
3. ตรวจสอบ Chat ID ถูกต้อง

```bash
# ทดสอบ Bot
curl "https://api.telegram.org/bot<TOKEN>/getMe"
```

### ไม่ได้รับแจ้งเตือน

1. ตรวจสอบ Alert Settings
2. ตรวจสอบ Chat ID
3. ตรวจสอบ Log

```bash
dlnk-admin telegram test-alert
```

### คำสั่งไม่ทำงาน

1. ตรวจสอบ Syntax
2. ตรวจสอบสิทธิ์
3. ดู Error Log

---

## 📊 Inline Keyboards

### ตัวอย่าง License Info

```
📋 License Information

Key: DLNK-XXXX-XXXX-XXXX-XXXX
User: user@email.com
Type: Pro
Status: Active
Expires: 2026-12-25

[Extend 30 days] [Extend 365 days]
[Reset Hardware] [Revoke]
```

### ตัวอย่าง User Approval

```
👤 New User Registration

Email: user@email.com
Username: newuser
Time: 2025-12-25 10:30:00

[✅ Approve (Trial)] [✅ Approve (Pro)]
[❌ Reject]
```

---

## 🔄 Webhook vs Polling

### Polling (Default)

Bot ดึงข้อมูลจาก Telegram Server เป็นระยะ:

```python
bot.start_polling()
```

**ข้อดี:**
- ตั้งค่าง่าย
- ไม่ต้องมี Public URL

**ข้อเสีย:**
- ช้ากว่า Webhook
- ใช้ทรัพยากรมากกว่า

### Webhook

Telegram ส่งข้อมูลมาที่ Server:

```python
bot.set_webhook(url="https://admin.dlnk.io/telegram/webhook")
```

**ข้อดี:**
- เร็วกว่า
- ใช้ทรัพยากรน้อยกว่า

**ข้อเสีย:**
- ต้องมี Public URL
- ต้องมี SSL Certificate

### ตั้งค่า Webhook

```yaml
# config.yaml
telegram:
  mode: "webhook"  # หรือ "polling"
  webhook_url: "https://admin.dlnk.io/telegram/webhook"
  webhook_port: 8443
```

---

## 📝 Custom Commands

### เพิ่มคำสั่งใหม่

```python
from dlnk_admin.telegram import TelegramBot

bot = TelegramBot(token="...", admin_chat_ids=["..."])

@bot.command("custom")
async def custom_command(update, context):
    await update.message.reply_text("Custom response!")

bot.start()
```

### เพิ่ม Inline Handler

```python
@bot.callback_query_handler
async def handle_callback(update, context):
    query = update.callback_query
    if query.data == "approve_user":
        # Handle approval
        await query.answer("User approved!")
```

---

## 📞 Support

หากพบปัญหา:
- ดู [Troubleshooting](troubleshooting.md)
- ติดต่อ: admin@dlnk.io

---

**ก่อนหน้า:** [← จัดการผู้ใช้](user-management.md)  
**ถัดไป:** [แก้ไขปัญหา →](troubleshooting.md)
