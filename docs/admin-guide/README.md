# 🔧 Admin Guide - คู่มือผู้ดูแลระบบ dLNk IDE

ยินดีต้อนรับสู่คู่มือผู้ดูแลระบบ dLNk IDE

---

## 📖 สารบัญ

1. [ติดตั้ง Admin Console](installation.md)
2. [จัดการ License](license-management.md)
3. [จัดการผู้ใช้](user-management.md)
4. [ตั้งค่า Telegram Bot](telegram-setup.md)
5. [แก้ไขปัญหา](troubleshooting.md)

---

## 🎯 ภาพรวมระบบ Admin

### สถาปัตยกรรม

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Console                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Dashboard  │  │   License   │  │   User Management   │  │
│  │   Stats     │  │  Management │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                           │                                  │
│                    ┌──────┴──────┐                          │
│                    │  Admin API  │                          │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
    │ License │       │  User   │       │ Telegram│
    │ Server  │       │   DB    │       │   Bot   │
    └─────────┘       └─────────┘       └─────────┘
```

### ส่วนประกอบหลัก

| ส่วนประกอบ | คำอธิบาย |
|------------|----------|
| **Admin Console** | แอพ Desktop สำหรับจัดการระบบ |
| **License Server** | เซิร์ฟเวอร์ตรวจสอบ License |
| **User Database** | ฐานข้อมูลผู้ใช้ |
| **Telegram Bot** | Bot สำหรับแจ้งเตือนและจัดการ |
| **Admin API** | REST API สำหรับการจัดการ |

---

## 👤 บทบาทของ Admin

### หน้าที่หลัก

1. **จัดการ License**
   - สร้าง License ใหม่
   - ต่ออายุ License
   - ยกเลิก License
   - Reset Hardware Binding

2. **จัดการผู้ใช้**
   - อนุมัติการลงทะเบียน
   - ระงับ/เปิดใช้งานบัญชี
   - ดูประวัติการใช้งาน

3. **ตรวจสอบระบบ**
   - ดู Dashboard สถิติ
   - ตรวจสอบ Logs
   - ตรวจจับความผิดปกติ

4. **รับแจ้งเตือน**
   - การโจมตีระบบ
   - License หมดอายุ
   - ปัญหาระบบ

---

## 🔐 ระดับสิทธิ์

| ระดับ | สิทธิ์ |
|-------|--------|
| **Super Admin** | ทุกอย่าง + จัดการ Admin อื่น |
| **Admin** | จัดการ License และ User |
| **Support** | ดูข้อมูลเท่านั้น |

---

## 🚀 เริ่มต้นอย่างรวดเร็ว

### 1. ติดตั้ง Admin Console

```bash
# ดาวน์โหลดและติดตั้ง
wget https://releases.dlnk.io/admin-console-setup.exe
# หรือใช้ Python
pip install dlnk-admin-console
```

### 2. เข้าสู่ระบบ

1. เปิด Admin Console
2. ใส่ Admin Key
3. ยืนยันตัวตนด้วย 2FA (ถ้าเปิดใช้)

### 3. ดู Dashboard

หลังเข้าสู่ระบบจะเห็น Dashboard แสดง:
- จำนวนผู้ใช้ทั้งหมด
- License ที่ใช้งานอยู่
- สถิติการใช้งาน AI

---

## 📊 Dashboard

### ข้อมูลที่แสดง

| หมวด | รายละเอียด |
|------|------------|
| **Users** | จำนวนผู้ใช้ทั้งหมด, Active, Inactive |
| **Licenses** | จำนวน License, ใช้งาน, หมดอายุ |
| **AI Usage** | จำนวน Requests, Top Users |
| **System** | Server Status, Uptime |

### กราฟและสถิติ

- กราฟการใช้งานรายวัน
- กราฟการลงทะเบียนใหม่
- Top 10 ผู้ใช้งานมากที่สุด
- License ที่ใกล้หมดอายุ

---

## ⚙️ การตั้งค่าพื้นฐาน

### ตั้งค่า Server

```python
# config.py
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8766
DATABASE_URL = "sqlite:///dlnk_admin.db"
SECRET_KEY = "your-secret-key"
```

### ตั้งค่า Telegram Bot

```python
# telegram_config.py
BOT_TOKEN = "your-bot-token"
ADMIN_CHAT_ID = "your-chat-id"
ALERT_ENABLED = True
```

---

## 📞 ต้องการความช่วยเหลือ?

- ดู [Troubleshooting](troubleshooting.md)
- ติดต่อ Super Admin
- Email: admin@dlnk.io

---

**ถัดไป:** [ติดตั้ง Admin Console →](installation.md)
