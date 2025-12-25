# 🚀 เริ่มต้นใช้งาน dLNk IDE

คู่มือการใช้งานเบื้องต้นสำหรับผู้ใช้ใหม่

---

## 📋 ก่อนเริ่มต้น

ตรวจสอบว่าคุณได้:

- [x] ติดตั้ง dLNk IDE เรียบร้อยแล้ว
- [x] มี License Key และ Activate แล้ว
- [x] เชื่อมต่ออินเทอร์เน็ต

---

## 🖥️ ทำความรู้จักกับหน้าจอหลัก

### โครงสร้างหน้าจอ

```
┌─────────────────────────────────────────────────────────────┐
│  Menu Bar                                                   │
├─────┬───────────────────────────────────────────────┬───────┤
│     │                                               │       │
│  A  │                                               │   D   │
│  c  │              Editor Area                      │   A   │
│  t  │              (พื้นที่เขียนโค้ด)                │   I   │
│  i  │                                               │       │
│  v  │                                               │   C   │
│  i  │                                               │   h   │
│  t  │                                               │   a   │
│  y  │                                               │   t   │
│     │                                               │       │
│  B  │                                               │   P   │
│  a  │                                               │   a   │
│  r  │                                               │   n   │
│     │                                               │   e   │
│     │                                               │   l   │
├─────┴───────────────────────────────────────────────┴───────┤
│  Status Bar                                                 │
└─────────────────────────────────────────────────────────────┘
```

### ส่วนประกอบหลัก

| ส่วน | คำอธิบาย |
|------|----------|
| **Menu Bar** | เมนูหลักของแอพ (File, Edit, View, etc.) |
| **Activity Bar** | ไอคอนสำหรับเปลี่ยน View (Explorer, Search, AI Chat) |
| **Editor Area** | พื้นที่สำหรับเขียนและแก้ไขโค้ด |
| **AI Chat Panel** | หน้าต่างสนทนากับ AI |
| **Status Bar** | แสดงสถานะต่างๆ (License, Connection, etc.) |

---

## 📁 การเปิดโปรเจ็ค

### วิธีที่ 1: เปิดโฟลเดอร์

1. คลิก **File** → **Open Folder**
2. เลือกโฟลเดอร์โปรเจ็ค
3. คลิก **Select Folder**

### วิธีที่ 2: ลากและวาง

1. เปิด File Explorer/Finder
2. ลากโฟลเดอร์มาวางที่หน้าต่าง dLNk IDE

### วิธีที่ 3: Command Line

```bash
# เปิดโฟลเดอร์ปัจจุบัน
dlnk .

# เปิดโฟลเดอร์ที่ระบุ
dlnk /path/to/project
```

---

## ✏️ การสร้างและแก้ไขไฟล์

### สร้างไฟล์ใหม่

1. คลิกขวาที่ Explorer → **New File**
2. หรือกด `Ctrl+N` (Windows/Linux) / `Cmd+N` (macOS)
3. ตั้งชื่อไฟล์พร้อมนามสกุล (เช่น `main.py`)

### บันทึกไฟล์

- **บันทึก:** `Ctrl+S` / `Cmd+S`
- **บันทึกเป็น:** `Ctrl+Shift+S` / `Cmd+Shift+S`
- **บันทึกทั้งหมด:** `Ctrl+K S` / `Cmd+K S`

---

## 🤖 การใช้งาน AI Features

### เปิด AI Chat

| วิธี | ขั้นตอน |
|------|---------|
| **Keyboard** | กด `Ctrl+Shift+A` / `Cmd+Shift+A` |
| **Activity Bar** | คลิกไอคอน AI ที่แถบด้านซ้าย |
| **Command Palette** | กด `Ctrl+Shift+P` → พิมพ์ "AI Chat" |

### ถาม AI

1. พิมพ์คำถามในช่อง Chat
2. กด **Enter** เพื่อส่ง
3. รอรับคำตอบ

**ตัวอย่างคำถาม:**
```
วิธีอ่านไฟล์ JSON ใน Python
```

### ใช้ AI กับโค้ดที่เลือก

1. **เลือกโค้ด** ที่ต้องการ
2. **คลิกขวา** → เลือกคำสั่ง AI:
   - **Explain Code** - อธิบายโค้ด
   - **Fix Bug** - แก้ไขข้อผิดพลาด
   - **Refactor** - ปรับปรุงโค้ด
   - **Add Comments** - เพิ่ม Comments

### Code Completion

ขณะพิมพ์โค้ด AI จะแนะนำอัตโนมัติ:

1. **Tab** - ยอมรับคำแนะนำ
2. **Esc** - ปิดคำแนะนำ
3. **Arrow Keys** - เลือกคำแนะนำอื่น

---

## ⌨️ Keyboard Shortcuts ที่ควรรู้

### ทั่วไป

| คำสั่ง | Windows/Linux | macOS |
|--------|---------------|-------|
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Quick Open | `Ctrl+P` | `Cmd+P` |
| Settings | `Ctrl+,` | `Cmd+,` |
| Terminal | `` Ctrl+` `` | `` Cmd+` `` |

### AI Features

| คำสั่ง | Windows/Linux | macOS |
|--------|---------------|-------|
| Open AI Chat | `Ctrl+Shift+A` | `Cmd+Shift+A` |
| Send Message | `Enter` | `Enter` |
| New Line | `Shift+Enter` | `Shift+Enter` |
| Clear Chat | `Ctrl+L` | `Cmd+L` |

### การแก้ไข

| คำสั่ง | Windows/Linux | macOS |
|--------|---------------|-------|
| Cut | `Ctrl+X` | `Cmd+X` |
| Copy | `Ctrl+C` | `Cmd+C` |
| Paste | `Ctrl+V` | `Cmd+V` |
| Undo | `Ctrl+Z` | `Cmd+Z` |
| Redo | `Ctrl+Y` | `Cmd+Shift+Z` |

---

## ⚙️ การตั้งค่าพื้นฐาน

### เปิด Settings

1. กด `Ctrl+,` / `Cmd+,`
2. หรือไปที่ **File** → **Preferences** → **Settings**

### การตั้งค่าที่แนะนำ

#### Theme

1. กด `Ctrl+K Ctrl+T` / `Cmd+K Cmd+T`
2. เลือก Theme ที่ต้องการ (แนะนำ: dLNk Dark)

#### Font Size

```json
{
  "editor.fontSize": 14
}
```

#### Auto Save

```json
{
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000
}
```

---

## 🔧 Extensions ที่แนะนำ

### ติดตั้ง Extension

1. คลิกไอคอน **Extensions** ที่ Activity Bar
2. ค้นหา Extension ที่ต้องการ
3. คลิก **Install**

### Extensions ที่แนะนำ

| Extension | คำอธิบาย |
|-----------|----------|
| **Python** | รองรับภาษา Python |
| **Prettier** | Format โค้ดอัตโนมัติ |
| **GitLens** | เครื่องมือ Git ขั้นสูง |
| **Error Lens** | แสดง Error inline |

---

## 💡 เคล็ดลับการใช้งาน

### 1. ใช้ AI อย่างมีประสิทธิภาพ

- **ถามเฉพาะเจาะจง** แทนที่จะถามกว้างๆ
- **ให้ Context** เช่น ภาษาที่ใช้, Framework
- **ถามต่อเนื่อง** AI จำบริบทการสนทนา

### 2. ใช้ Keyboard Shortcuts

- ช่วยประหยัดเวลา
- ทำงานได้เร็วขึ้น
- ดู [รายการ Shortcuts](shortcuts.md) ทั้งหมด

### 3. จัดระเบียบ Workspace

- ใช้ **Folders** แยกโปรเจ็ค
- ใช้ **Workspaces** สำหรับโปรเจ็คใหญ่
- ใช้ **Split Editor** ดูหลายไฟล์พร้อมกัน

---

## ❓ ต้องการความช่วยเหลือ?

- ดู [AI Chat Guide](ai-chat.md) สำหรับการใช้ AI
- ดู [FAQ](faq.md) สำหรับคำถามที่พบบ่อย
- ติดต่อ Telegram: @dlnk_support

---

**ก่อนหน้า:** [← วิธีติดตั้ง](installation.md)  
**ถัดไป:** [AI Chat →](ai-chat.md)
