# 👥 User Management

คู่มือการจัดการผู้ใช้สำหรับ dLNk IDE

---

## 📋 ภาพรวม

ระบบจัดการผู้ใช้ช่วยให้ Admin สามารถ:
- ดูรายชื่อผู้ใช้ทั้งหมด
- อนุมัติการลงทะเบียน
- ระงับ/เปิดใช้งานบัญชี
- ดูประวัติการใช้งาน
- จัดการสิทธิ์

---

## 👤 สถานะผู้ใช้

| สถานะ | คำอธิบาย | สีแสดง |
|-------|----------|--------|
| **Pending** | รอการอนุมัติ | 🟡 เหลือง |
| **Active** | ใช้งานปกติ | 🟢 เขียว |
| **Suspended** | ถูกระงับชั่วคราว | 🟠 ส้ม |
| **Banned** | ถูกแบนถาวร | 🔴 แดง |
| **Expired** | License หมดอายุ | ⚪ เทา |

---

## 📋 การดูรายชื่อผู้ใช้

### Admin Console

1. เปิด Admin Console
2. ไปที่ **Users** tab
3. ดูรายชื่อผู้ใช้ทั้งหมด

### การกรอง

| Filter | คำอธิบาย |
|--------|----------|
| **Status** | กรองตามสถานะ |
| **License Type** | กรองตามประเภท License |
| **Registration Date** | กรองตามวันที่ลงทะเบียน |
| **Last Active** | กรองตามวันที่ใช้งานล่าสุด |

### การค้นหา

ค้นหาได้ด้วย:
- Email
- Username
- License Key

### API

```bash
curl -X GET "https://api.dlnk.io/admin/users?status=active&limit=50" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "email": "user@email.com",
      "username": "user1",
      "status": "active",
      "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
      "license_type": "pro",
      "registered_at": "2025-01-01T00:00:00Z",
      "last_active": "2025-12-25T10:30:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 50
}
```

---

## ✅ การอนุมัติผู้ใช้ใหม่

### Auto-Approve Mode

ตั้งค่าให้อนุมัติอัตโนมัติ:

```yaml
# config.yaml
registration:
  auto_approve: true
  default_license_type: "trial"
  default_duration_days: 7
```

### Manual Approve Mode

1. ไปที่ **Users** → **Pending**
2. ตรวจสอบข้อมูลผู้ใช้
3. คลิก **"Approve"** หรือ **"Reject"**

### Telegram Bot

```
# ดูรายการรอการอนุมัติ
/pending_users

# อนุมัติ
/approve user@email.com

# ปฏิเสธ
/reject user@email.com
```

### API

```bash
# อนุมัติ
curl -X POST https://api.dlnk.io/admin/users/1/approve \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "license_type": "trial",
    "duration_days": 7
  }'

# ปฏิเสธ
curl -X POST https://api.dlnk.io/admin/users/1/reject \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Invalid email"}'
```

---

## 🚫 การระงับผู้ใช้

### เหตุผลในการระงับ

- ละเมิดข้อตกลงการใช้งาน
- พฤติกรรมน่าสงสัย
- ร้องขอจากผู้ใช้เอง
- ปัญหาการชำระเงิน

### Admin Console

1. ค้นหาผู้ใช้
2. คลิก **"Suspend"**
3. ใส่เหตุผล
4. เลือกระยะเวลา (ถ้าต้องการ)
5. ยืนยัน

### Telegram Bot

```
/suspend user@email.com "Violation of terms"
```

### API

```bash
curl -X POST https://api.dlnk.io/admin/users/1/suspend \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Violation of terms",
    "duration_days": 30
  }'
```

---

## ✅ การเปิดใช้งานผู้ใช้

### Admin Console

1. ค้นหาผู้ใช้ที่ถูกระงับ
2. คลิก **"Unsuspend"**
3. ยืนยัน

### Telegram Bot

```
/unsuspend user@email.com
```

### API

```bash
curl -X POST https://api.dlnk.io/admin/users/1/unsuspend \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 🔴 การแบนผู้ใช้

### เหตุผลในการแบน

- การโจมตีระบบ
- การแชร์ License
- การใช้งานผิดกฎหมาย
- การละเมิดซ้ำหลายครั้ง

### Admin Console

1. ค้นหาผู้ใช้
2. คลิก **"Ban"**
3. ใส่เหตุผล
4. ยืนยัน (ต้องใส่รหัสยืนยัน)

### Telegram Bot

```
/ban user@email.com "Repeated violations"
```

### API

```bash
curl -X POST https://api.dlnk.io/admin/users/1/ban \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Repeated violations"}'
```

> ⚠️ **คำเตือน:** การแบนเป็นการถาวร ต้องมี Super Admin เท่านั้นที่สามารถ Unban ได้

---

## 📊 การดูประวัติการใช้งาน

### ข้อมูลที่แสดง

| ข้อมูล | คำอธิบาย |
|--------|----------|
| **Login History** | ประวัติการเข้าสู่ระบบ |
| **AI Requests** | จำนวน AI Requests |
| **Last Active** | เวลาใช้งานล่าสุด |
| **IP Addresses** | IP ที่ใช้เข้าถึง |
| **Devices** | อุปกรณ์ที่ใช้ |

### Admin Console

1. ค้นหาผู้ใช้
2. คลิก **"View Details"**
3. ดูแท็บ **"Activity"**

### API

```bash
curl -X GET https://api.dlnk.io/admin/users/1/activity \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Response:**
```json
{
  "user_id": 1,
  "activity": {
    "total_logins": 150,
    "total_ai_requests": 5000,
    "last_login": "2025-12-25T10:30:00Z",
    "last_ip": "192.168.1.100",
    "devices": [
      {
        "hardware_id": "ABC123...",
        "os": "Windows 11",
        "first_seen": "2025-01-01T00:00:00Z",
        "last_seen": "2025-12-25T10:30:00Z"
      }
    ],
    "daily_requests": [
      {"date": "2025-12-25", "count": 150},
      {"date": "2025-12-24", "count": 200}
    ]
  }
}
```

---

## 📧 การส่งข้อความถึงผู้ใช้

### ส่งถึงผู้ใช้คนเดียว

**Admin Console:**
1. ค้นหาผู้ใช้
2. คลิก **"Send Message"**
3. พิมพ์ข้อความ
4. เลือกช่องทาง (Email, In-App)
5. ส่ง

### ส่งถึงผู้ใช้หลายคน (Broadcast)

**Admin Console:**
1. ไปที่ **Users** → **Broadcast**
2. เลือกกลุ่มผู้รับ:
   - ทุกคน
   - ตาม License Type
   - ตาม Status
3. พิมพ์ข้อความ
4. ส่ง

### API

```bash
# ส่งถึงคนเดียว
curl -X POST https://api.dlnk.io/admin/users/1/message \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Important Notice",
    "body": "Your license will expire soon.",
    "channel": "email"
  }'

# Broadcast
curl -X POST https://api.dlnk.io/admin/broadcast \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "System Maintenance",
    "body": "Scheduled maintenance on...",
    "target": "all"
  }'
```

---

## 📈 User Statistics

### Dashboard Metrics

| Metric | คำอธิบาย |
|--------|----------|
| **Total Users** | จำนวนผู้ใช้ทั้งหมด |
| **Active Today** | ผู้ใช้ที่ใช้งานวันนี้ |
| **New This Week** | ผู้ใช้ใหม่สัปดาห์นี้ |
| **Pending Approval** | รอการอนุมัติ |
| **Suspended** | ถูกระงับ |

### API

```bash
curl -X GET https://api.dlnk.io/admin/users/stats \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Response:**
```json
{
  "total": 1000,
  "active": 850,
  "pending": 20,
  "suspended": 30,
  "banned": 10,
  "expired": 90,
  "new_today": 5,
  "new_this_week": 25,
  "active_today": 300
}
```

---

## 🔐 Security Monitoring

### Suspicious Activity Alerts

ระบบจะแจ้งเตือนเมื่อพบ:
- Login จาก IP ใหม่
- Login จากหลายประเทศในเวลาใกล้กัน
- AI Requests มากผิดปกติ
- พยายาม Bypass Prompt Filter

### ตั้งค่า Alert

```yaml
# config.yaml
security:
  alerts:
    new_ip_login: true
    multiple_country_login: true
    high_request_rate:
      enabled: true
      threshold: 100  # requests per minute
    prompt_filter_violation: true
```

### ดู Security Logs

**Admin Console:**
ไปที่ **Security** → **Logs**

**API:**
```bash
curl -X GET "https://api.dlnk.io/admin/security/logs?user_id=1" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 📤 Export User Data

### Export ทั้งหมด

**Admin Console:**
1. ไปที่ **Users** → **Export**
2. เลือก Format (CSV, JSON, Excel)
3. เลือก Fields ที่ต้องการ
4. Download

### Export เฉพาะผู้ใช้

**API:**
```bash
curl -X GET "https://api.dlnk.io/admin/users/export?format=csv" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -o users.csv
```

---

## 🔧 การแก้ไขปัญหา

### ผู้ใช้ Login ไม่ได้

1. ตรวจสอบสถานะ (Active?)
2. ตรวจสอบ License (Valid?)
3. ตรวจสอบ Hardware Binding
4. Reset Password ถ้าจำเป็น

### ผู้ใช้ไม่ได้รับ Email

1. ตรวจสอบ Email ถูกต้อง
2. ตรวจสอบ Spam Folder
3. ตรวจสอบ Email Server Logs

### ผู้ใช้ถูก Suspend โดยไม่ตั้งใจ

1. ตรวจสอบ Audit Log
2. Unsuspend ผู้ใช้
3. แจ้งผู้ใช้

---

**ก่อนหน้า:** [← จัดการ License](license-management.md)  
**ถัดไป:** [ตั้งค่า Telegram Bot →](telegram-setup.md)
