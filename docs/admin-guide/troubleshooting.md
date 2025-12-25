# 🔧 Troubleshooting

คู่มือการแก้ไขปัญหาสำหรับ Admin

---

## 🖥️ Admin Console

### Console ไม่เปิด

**อาการ:** คลิกแล้วไม่มีอะไรเกิดขึ้น

**แก้ไข:**
1. ตรวจสอบ Python version:
   ```bash
   python3 --version  # ต้องเป็น 3.11+
   ```

2. ติดตั้ง dependencies ใหม่:
   ```bash
   pip install --upgrade dlnk-admin-console
   ```

3. ตรวจสอบ Log:
   ```bash
   cat ~/.dlnk/admin/logs/admin.log
   ```

---

### Login ไม่ได้

**อาการ:** ใส่ Admin Key แล้วไม่ผ่าน

**แก้ไข:**
1. ตรวจสอบ Admin Key ถูกต้อง
2. ตรวจสอบ Database connection:
   ```bash
   dlnk-admin db-check
   ```

3. Reset Admin Key:
   ```bash
   dlnk-admin reset-admin-key --username "admin"
   ```

---

### 2FA ไม่ทำงาน

**อาการ:** รหัส 2FA ไม่ถูกต้อง

**แก้ไข:**
1. ตรวจสอบเวลาในเครื่องถูกต้อง:
   ```bash
   date
   timedatectl status
   ```

2. Sync เวลา:
   ```bash
   sudo timedatectl set-ntp true
   ```

3. Reset 2FA:
   ```bash
   dlnk-admin reset-2fa --username "admin"
   ```

---

## 🔑 License System

### สร้าง License ไม่ได้

**อาการ:** Error เมื่อสร้าง License

**แก้ไข:**
1. ตรวจสอบ Database:
   ```bash
   dlnk-admin db-check
   ```

2. ตรวจสอบ Disk Space:
   ```bash
   df -h
   ```

3. ดู Error Log:
   ```bash
   tail -100 ~/.dlnk/admin/logs/admin.log | grep -i error
   ```

---

### License Validation ล้มเหลว

**อาการ:** ผู้ใช้ Activate License ไม่ได้

**แก้ไข:**
1. ตรวจสอบ License มีอยู่:
   ```bash
   dlnk-admin license-info DLNK-XXXX-XXXX-XXXX-XXXX
   ```

2. ตรวจสอบ License ไม่หมดอายุ
3. ตรวจสอบ Hardware Binding:
   ```bash
   dlnk-admin reset-hardware DLNK-XXXX-XXXX-XXXX-XXXX
   ```

---

### Hardware Binding ผิดพลาด

**อาการ:** "License already in use on another device"

**แก้ไข:**
1. Reset Hardware Binding:
   ```bash
   dlnk-admin reset-hardware DLNK-XXXX-XXXX-XXXX-XXXX
   ```

2. หรือผ่าน Telegram:
   ```
   /reset_hardware DLNK-XXXX-XXXX-XXXX-XXXX
   ```

---

## 🗄️ Database

### Database Connection Error

**อาการ:** "Cannot connect to database"

**แก้ไข:**

**SQLite:**
```bash
# ตรวจสอบไฟล์
ls -la ~/.dlnk/admin/dlnk_admin.db

# ตรวจสอบ permission
chmod 644 ~/.dlnk/admin/dlnk_admin.db

# Repair database
sqlite3 ~/.dlnk/admin/dlnk_admin.db "PRAGMA integrity_check;"
```

**PostgreSQL:**
```bash
# ตรวจสอบ service
sudo systemctl status postgresql

# ตรวจสอบ connection
psql -h localhost -U dlnk_admin -d dlnk_admin -c "SELECT 1;"
```

---

### Database Corruption

**อาการ:** "Database is corrupted"

**แก้ไข:**
1. Backup ไฟล์เดิม:
   ```bash
   cp ~/.dlnk/admin/dlnk_admin.db ~/.dlnk/admin/dlnk_admin.db.backup
   ```

2. ลอง Repair:
   ```bash
   sqlite3 ~/.dlnk/admin/dlnk_admin.db ".recover" | sqlite3 ~/.dlnk/admin/dlnk_admin_recovered.db
   ```

3. หรือ Restore จาก Backup:
   ```bash
   cp ~/.dlnk/admin/backups/latest.db ~/.dlnk/admin/dlnk_admin.db
   ```

---

### Migration Error

**อาการ:** "Migration failed"

**แก้ไข:**
1. ดู Migration Status:
   ```bash
   dlnk-admin db-status
   ```

2. Rollback:
   ```bash
   dlnk-admin db-rollback
   ```

3. Migrate ใหม่:
   ```bash
   dlnk-admin db-migrate
   ```

---

## 🌐 API Server

### Server ไม่ Start

**อาการ:** "Address already in use"

**แก้ไข:**
1. หา Process ที่ใช้ Port:
   ```bash
   sudo lsof -i :8766
   ```

2. Kill Process:
   ```bash
   sudo kill -9 <PID>
   ```

3. หรือเปลี่ยน Port:
   ```yaml
   # config.yaml
   server:
     port: 8767
   ```

---

### SSL Certificate Error

**อาการ:** "SSL certificate verify failed"

**แก้ไข:**
1. ตรวจสอบ Certificate:
   ```bash
   openssl x509 -in /path/to/cert.pem -text -noout
   ```

2. ตรวจสอบวันหมดอายุ:
   ```bash
   openssl x509 -in /path/to/cert.pem -enddate -noout
   ```

3. Renew Certificate:
   ```bash
   sudo certbot renew
   ```

---

### API Timeout

**อาการ:** "Request timeout"

**แก้ไข:**
1. ตรวจสอบ Server Load:
   ```bash
   top
   htop
   ```

2. ตรวจสอบ Memory:
   ```bash
   free -h
   ```

3. เพิ่ม Timeout:
   ```yaml
   # config.yaml
   server:
     timeout: 60
   ```

---

## 📱 Telegram Bot

### Bot ไม่ตอบ

**อาการ:** ส่งคำสั่งแล้วไม่มีการตอบกลับ

**แก้ไข:**
1. ตรวจสอบ Bot Token:
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/getMe"
   ```

2. ตรวจสอบ Bot กำลังทำงาน:
   ```bash
   dlnk-admin telegram status
   ```

3. Restart Bot:
   ```bash
   dlnk-admin telegram restart
   ```

---

### ไม่ได้รับ Alert

**อาการ:** มี Event แต่ไม่ได้รับแจ้งเตือน

**แก้ไข:**
1. ตรวจสอบ Chat ID:
   ```bash
   dlnk-admin telegram test-alert
   ```

2. ตรวจสอบ Alert Settings:
   ```yaml
   # config.yaml
   telegram:
     alerts:
       enabled: true
   ```

3. ตรวจสอบว่าไม่ได้ Block Bot

---

### Webhook Error

**อาการ:** "Webhook failed"

**แก้ไข:**
1. ตรวจสอบ URL:
   ```bash
   curl -I https://admin.dlnk.io/telegram/webhook
   ```

2. ตรวจสอบ SSL:
   ```bash
   openssl s_client -connect admin.dlnk.io:443
   ```

3. Reset Webhook:
   ```bash
   dlnk-admin telegram set-webhook --url "https://admin.dlnk.io/telegram/webhook"
   ```

---

## 🔐 Security

### Prompt Filter False Positive

**อาการ:** Prompt ปกติถูก Block

**แก้ไข:**
1. ดู Blocked Prompt:
   ```bash
   dlnk-admin security-logs --type prompt_filter
   ```

2. เพิ่ม Whitelist:
   ```yaml
   # config.yaml
   security:
     prompt_filter:
       whitelist:
         - "pattern_to_allow"
   ```

3. ปรับ Sensitivity:
   ```yaml
   security:
     prompt_filter:
       sensitivity: "medium"  # low, medium, high
   ```

---

### Brute Force Detection

**อาการ:** Admin ถูก Lock

**แก้ไข:**
1. Unlock Account:
   ```bash
   dlnk-admin unlock-admin --username "admin"
   ```

2. ตรวจสอบ IP ที่พยายาม Login:
   ```bash
   dlnk-admin security-logs --type login_failed
   ```

3. Block IP:
   ```bash
   dlnk-admin block-ip 192.168.1.100
   ```

---

## 📊 Performance

### Server ช้า

**อาการ:** Response Time สูง

**แก้ไข:**
1. ตรวจสอบ Database:
   ```bash
   # SQLite
   sqlite3 ~/.dlnk/admin/dlnk_admin.db "ANALYZE;"
   
   # PostgreSQL
   psql -c "ANALYZE;"
   ```

2. เพิ่ม Index:
   ```bash
   dlnk-admin db-optimize
   ```

3. เพิ่ม Workers:
   ```yaml
   # config.yaml
   server:
     workers: 4
   ```

---

### Memory Leak

**อาการ:** Memory ใช้เพิ่มขึ้นเรื่อยๆ

**แก้ไข:**
1. ตรวจสอบ Memory:
   ```bash
   ps aux | grep dlnk-admin
   ```

2. Restart Service:
   ```bash
   dlnk-admin restart
   ```

3. ตั้ง Auto-restart:
   ```yaml
   # config.yaml
   server:
     auto_restart:
       enabled: true
       memory_threshold: "80%"
   ```

---

## 📝 Logs

### ดู Logs

```bash
# ดู Log ล่าสุด
tail -100 ~/.dlnk/admin/logs/admin.log

# ดู Error เท่านั้น
grep -i error ~/.dlnk/admin/logs/admin.log

# ดู Log แบบ Real-time
tail -f ~/.dlnk/admin/logs/admin.log
```

### Log Rotation

```yaml
# config.yaml
logging:
  rotation:
    max_size: "100MB"
    backup_count: 5
```

### ส่ง Log ไป External Service

```yaml
# config.yaml
logging:
  external:
    enabled: true
    service: "elasticsearch"
    url: "http://localhost:9200"
```

---

## 🆘 ติดต่อ Support

หากแก้ไขไม่ได้:

1. รวบรวมข้อมูล:
   ```bash
   dlnk-admin diagnostic > diagnostic.txt
   ```

2. ส่งไฟล์ diagnostic.txt พร้อมอธิบายปัญหาไปที่:
   - Email: admin@dlnk.io
   - Telegram: @dlnk_admin_support

---

**ก่อนหน้า:** [← ตั้งค่า Telegram Bot](telegram-setup.md)  
**กลับหน้าหลัก:** [Admin Guide](README.md)
