# 📅 AI-09 Scheduled Tasks

**วันที่สร้าง:** 2025-12-25
**อัพเดทล่าสุด:** 2025-12-25
**สถานะ:** ✅ Active

---

## 🔄 Scheduled Task หลัก

### AI-09 Workflow Check (ทุก 5 นาที)

| รายละเอียด | ค่า |
|-----------|-----|
| **ชื่อ** | AI-09 Workflow Check |
| **ความถี่** | ทุก 5 นาที (300 วินาที) |
| **หน้าที่** | ตรวจสอบงานใหม่, รับคำสั่ง, Integrate กับ AI อื่น |

**โฟลเดอร์ที่ตรวจสอบ:**
- `/dLNk-IDE-Project/tasks/AI-09/` - งานที่มอบหมายให้ AI-09
- `/dLNk-IDE-Project/security/` - จาก AI-08 Security
- `/dLNk-IDE-Project/backend/` - จาก AI-05, 06, 07
- `/dLNk-IDE-Project/commands/` - คำสั่งเพิ่มเติม

---

## 📊 Timeline (ทุก 5 นาที)

```
Min 0    Min 5    Min 10   Min 15   Min 20   Min 25   Min 30
  |        |        |        |        |        |        |
  🔄       🔄       🔄       🔄       🔄       🔄       🔄
  
🔄 = ตรวจสอบงาน + รับคำสั่ง + Integrate + ทบทวน
```

---

## 🔗 Dependencies Map

```
AI-08 (Security)
    └── Alert System ──────────────────┐
                                       │
AI-05 (AI Bridge)                      │
    └── AI API endpoints ──────────────┤
                                       ├──> AI-09 Telegram Bot
AI-06 (License Server)                 │    (ตรวจสอบทุก 5 นาที)
    └── License API endpoints ─────────┤
                                       │
AI-07 (Admin Console)                  │
    └── Admin API endpoints ───────────┘
```

---

## 📝 สิ่งที่ทำในแต่ละรอบ

1. **ตรวจสอบงานใหม่** - ดูไฟล์ใหม่ใน Google Drive
2. **รับคำสั่งเพิ่มเติม** - ดูโฟลเดอร์ commands/
3. **Integrate กับ AI อื่น** - Security, Backend API
4. **ทบทวนงาน** - ตรวจสอบความถูกต้อง
5. **รายงานสถานะ** - แจ้งผู้ใช้ถ้ามีอัพเดท

---

## 📁 โฟลเดอร์ใน Google Drive

| โฟลเดอร์ | ใช้สำหรับ |
|---------|----------|
| `/dLNk-IDE-Project/telegram-bot/` | Output ของ AI-09 |
| `/dLNk-IDE-Project/tasks/AI-09/` | งานที่มอบหมายให้ AI-09 |
| `/dLNk-IDE-Project/commands/` | คำสั่งเพิ่มเติม |
| `/dLNk-IDE-Project/status/` | รายงานสถานะ |
| `/dLNk-IDE-Project/security/` | จาก AI-08 |
| `/dLNk-IDE-Project/backend/` | จาก AI-05, 06, 07 |

---

**AI-09 Telegram Bot Developer**
**Workflow: ทุก 5 นาที ✅**
