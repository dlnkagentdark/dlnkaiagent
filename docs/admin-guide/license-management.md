# 🔑 License Management

คู่มือการจัดการ License สำหรับ dLNk IDE

---

## 📋 ภาพรวม

ระบบ License ของ dLNk IDE ใช้สำหรับ:
- ควบคุมการเข้าถึง AI Features
- จำกัดจำนวนอุปกรณ์
- กำหนดระยะเวลาการใช้งาน
- ติดตามการใช้งาน

---

## 🏷️ ประเภท License

| ประเภท | ระยะเวลา | อุปกรณ์ | AI Requests/วัน | ราคา |
|--------|----------|---------|-----------------|------|
| **Trial** | 7 วัน | 1 | 100 | ฟรี |
| **Standard** | 1 ปี | 1 | 500 | $XX |
| **Pro** | 1 ปี | 3 | 1,000 | $XX |
| **Enterprise** | Custom | ไม่จำกัด | ไม่จำกัด | ติดต่อ |

---

## 🔤 รูปแบบ License Key

```
DLNK-XXXX-XXXX-XXXX-XXXX
```

- **Prefix:** `DLNK`
- **Format:** 4 กลุ่ม × 4 ตัวอักษร
- **Characters:** A-Z, 0-9
- **Case:** ไม่สนใจตัวพิมพ์ใหญ่/เล็ก

---

## ➕ การสร้าง License

### ผ่าน Admin Console GUI

1. เปิด Admin Console
2. ไปที่ **Licenses** tab
3. คลิก **"Create License"**
4. กรอกข้อมูล:
   - **Email:** อีเมลผู้ใช้
   - **Type:** ประเภท License
   - **Duration:** ระยะเวลา (วัน)
   - **Hardware Binding:** เปิด/ปิด
5. คลิก **"Generate"**
6. ส่ง License Key ให้ผู้ใช้

### ผ่าน Telegram Bot

```
/create_license user@email.com pro 365
```

**Parameters:**
- `user@email.com` - อีเมลผู้ใช้
- `pro` - ประเภท (trial, standard, pro, enterprise)
- `365` - จำนวนวัน

### ผ่าน API

```bash
curl -X POST https://api.dlnk.io/admin/licenses \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@email.com",
    "type": "pro",
    "duration_days": 365,
    "hardware_binding": true
  }'
```

**Response:**
```json
{
  "success": true,
  "license_key": "DLNK-ABCD-EFGH-IJKL-MNOP",
  "expires_at": "2026-12-25T00:00:00Z"
}
```

### ผ่าน Python

```python
from dlnk_admin import LicenseManager

manager = LicenseManager()
license_key = manager.create_license(
    email="user@email.com",
    license_type="pro",
    duration_days=365,
    hardware_binding=True
)
print(f"License Key: {license_key}")
```

---

## 📋 การดู License

### ดูทั้งหมด

**Admin Console:**
ไปที่ **Licenses** tab

**Telegram Bot:**
```
/licenses
```

**API:**
```bash
curl -X GET https://api.dlnk.io/admin/licenses \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### ดูรายละเอียด License

**Telegram Bot:**
```
/license_info DLNK-XXXX-XXXX-XXXX-XXXX
```

**API:**
```bash
curl -X GET https://api.dlnk.io/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Response:**
```json
{
  "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
  "email": "user@email.com",
  "type": "pro",
  "status": "active",
  "created_at": "2025-12-25T00:00:00Z",
  "expires_at": "2026-12-25T00:00:00Z",
  "hardware_id": "ABC123...",
  "last_used": "2025-12-25T10:30:00Z",
  "usage": {
    "requests_today": 150,
    "requests_total": 5000
  }
}
```

---

## 🔄 การต่ออายุ License

### Admin Console

1. ค้นหา License
2. คลิก **"Extend"**
3. ใส่จำนวนวันที่ต้องการเพิ่ม
4. คลิก **"Confirm"**

### Telegram Bot

```
/extend DLNK-XXXX-XXXX-XXXX-XXXX 365
```

### API

```bash
curl -X POST https://api.dlnk.io/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX/extend \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 365}'
```

---

## ❌ การยกเลิก License

### Admin Console

1. ค้นหา License
2. คลิก **"Revoke"**
3. ยืนยันการยกเลิก

### Telegram Bot

```
/revoke DLNK-XXXX-XXXX-XXXX-XXXX
```

### API

```bash
curl -X POST https://api.dlnk.io/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX/revoke \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 🔗 Hardware Binding

### วิธีการทำงาน

1. ผู้ใช้ Activate License บนอุปกรณ์
2. ระบบเก็บ Hardware ID ของอุปกรณ์
3. License ใช้ได้เฉพาะอุปกรณ์นั้น
4. ถ้าต้องการเปลี่ยนอุปกรณ์ ต้อง Reset

### Reset Hardware Binding

**Admin Console:**
1. ค้นหา License
2. คลิก **"Reset Hardware"**
3. ยืนยัน

**Telegram Bot:**
```
/reset_hardware DLNK-XXXX-XXXX-XXXX-XXXX
```

**API:**
```bash
curl -X POST https://api.dlnk.io/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX/reset-hardware \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## 📦 Bulk Operations

### Import Licenses

1. เตรียมไฟล์ CSV:
```csv
email,type,duration_days
user1@email.com,pro,365
user2@email.com,standard,365
user3@email.com,trial,7
```

2. **Admin Console:**
   - ไปที่ **Licenses** → **Import**
   - อัพโหลดไฟล์ CSV
   - ตรวจสอบและยืนยัน

3. **API:**
```bash
curl -X POST https://api.dlnk.io/admin/licenses/import \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -F "file=@licenses.csv"
```

### Export Licenses

**Admin Console:**
1. ไปที่ **Licenses** → **Export**
2. เลือก Format (CSV, JSON, Excel)
3. เลือก Filter (ทั้งหมด, Active, Expired)
4. คลิก **Download**

**API:**
```bash
curl -X GET "https://api.dlnk.io/admin/licenses/export?format=csv&status=active" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -o licenses.csv
```

---

## 📊 License Statistics

### Dashboard Metrics

| Metric | คำอธิบาย |
|--------|----------|
| **Total Licenses** | จำนวน License ทั้งหมด |
| **Active** | License ที่ใช้งานอยู่ |
| **Expired** | License ที่หมดอายุ |
| **Revoked** | License ที่ถูกยกเลิก |
| **Expiring Soon** | License ที่จะหมดอายุใน 30 วัน |

### API Statistics

```bash
curl -X GET https://api.dlnk.io/admin/licenses/stats \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Response:**
```json
{
  "total": 1000,
  "active": 850,
  "expired": 100,
  "revoked": 50,
  "expiring_soon": 75,
  "by_type": {
    "trial": 200,
    "standard": 500,
    "pro": 250,
    "enterprise": 50
  }
}
```

---

## 🔔 การแจ้งเตือน

### ตั้งค่าแจ้งเตือน License หมดอายุ

```yaml
# config.yaml
notifications:
  license_expiry:
    enabled: true
    days_before: [30, 7, 1]  # แจ้งเตือนก่อนหมดอายุ
    channels:
      - telegram
      - email
```

### ตัวอย่างข้อความแจ้งเตือน

```
⚠️ License Expiry Warning

License: DLNK-XXXX-XXXX-XXXX-XXXX
User: user@email.com
Expires: 2026-01-01 (7 days remaining)

Action: /extend DLNK-XXXX-XXXX-XXXX-XXXX 365
```

---

## 🔧 การแก้ไขปัญหา

### "License already in use"

**สาเหตุ:** License ถูก bind กับอุปกรณ์อื่นแล้ว

**แก้ไข:**
1. Reset Hardware Binding
2. ให้ผู้ใช้ Activate ใหม่

### "License expired"

**สาเหตุ:** License หมดอายุแล้ว

**แก้ไข:**
1. ต่ออายุ License
2. หรือสร้าง License ใหม่

### "Invalid license key"

**สาเหตุ:** License Key ไม่ถูกต้อง

**แก้ไข:**
1. ตรวจสอบการพิมพ์
2. ตรวจสอบว่า License มีอยู่ในระบบ

### "License revoked"

**สาเหตุ:** License ถูกยกเลิกแล้ว

**แก้ไข:**
1. ติดต่อ Admin เพื่อขอ License ใหม่

---

## 🔐 Security Best Practices

1. **ใช้ Hardware Binding** สำหรับ License ที่สำคัญ
2. **ตรวจสอบ Usage** เป็นประจำ
3. **Revoke License** ที่น่าสงสัยทันที
4. **ตั้ง Alert** สำหรับ Unusual Activity
5. **Backup Database** เป็นประจำ

---

**ก่อนหน้า:** [← ติดตั้ง Admin Console](installation.md)  
**ถัดไป:** [จัดการผู้ใช้ →](user-management.md)
