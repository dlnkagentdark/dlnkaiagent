# 💻 Developer Guide - คู่มือนักพัฒนา dLNk IDE

ยินดีต้อนรับสู่คู่มือนักพัฒนา dLNk IDE

---

## 📖 สารบัญ

1. [Architecture Overview](architecture.md)
2. [API Reference](api-reference.md)
3. [Extension Development](extension-dev.md)
4. [Contributing Guide](contributing.md)
5. [Security Guidelines](security.md)

---

## 🎯 ภาพรวมโปรเจ็ค

dLNk IDE เป็น VS Code Fork ที่มีความสามารถ AI ในตัว ประกอบด้วย:

### Components หลัก

| Component | Technology | คำอธิบาย |
|-----------|------------|----------|
| **Desktop App** | Electron | แอพ Desktop หลัก |
| **Editor Core** | VS Code | Editor พื้นฐาน |
| **dLNk Extension** | TypeScript | AI Chat และ Completion |
| **AI Bridge** | Python/gRPC | เชื่อมต่อ AI Services |
| **License Server** | FastAPI | จัดการ License |
| **Admin Console** | Python/CustomTkinter | จัดการระบบ |
| **Telegram Bot** | python-telegram-bot | แจ้งเตือนและจัดการ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      dLNk IDE (Desktop)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  VS Code    │  │  dLNk       │  │  AI Chat            │  │
│  │  Core       │  │  Extension  │  │  Panel              │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                           │                                  │
│                    ┌──────┴──────┐                          │
│                    │  AI Bridge  │                          │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            │ gRPC / REST
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    ┌──────┴──────┐                          │
│                    │  Antigravity │                          │
│                    │  Proxy       │                          │
│                    └──────┬──────┘                          │
│                           │                                  │
│                    ┌──────┴──────┐                          │
│                    │  Jetski API │                          │
│                    └─────────────┘                          │
│                                                              │
│                      Backend Services                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend (Desktop App)

| Technology | Version | Purpose |
|------------|---------|---------|
| Electron | 28.x | Desktop framework |
| VS Code | 1.85.x | Editor base |
| TypeScript | 5.x | Extension language |
| React | 18.x | UI components |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Backend services |
| FastAPI | 0.100+ | REST API |
| gRPC | 1.60+ | AI communication |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL/SQLite | - | Database |

### AI Integration

| Technology | Purpose |
|------------|---------|
| Antigravity gRPC | Primary AI provider |
| Gemini API | Fallback provider |
| OpenAI API | Fallback provider |
| Groq API | Fallback provider |
| Ollama | Local fallback |

---

## 📁 Project Structure

```
dLNk-IDE/
├── vscode-fork/              # VS Code fork
│   ├── src/
│   │   └── vs/
│   │       └── workbench/
│   ├── product.json          # Branding
│   └── package.json
├── extension/                # dLNk Extension
│   ├── src/
│   │   ├── extension.ts      # Entry point
│   │   ├── chatPanel.ts      # Chat UI
│   │   └── aiClient.ts       # AI client
│   └── package.json
├── backend/
│   ├── ai-bridge/            # AI Bridge service
│   │   ├── bridge.py
│   │   ├── providers/
│   │   └── proto/
│   └── license/              # License server
│       ├── server.py
│       └── models.py
├── admin-console/            # Admin app
│   ├── main.py
│   └── ui/
├── telegram-bot/             # Telegram bot
│   └── bot.py
├── security/                 # Security modules
│   ├── prompt_filter.py
│   └── anomaly_detection.py
└── docs/                     # Documentation
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Node.js 18+
node --version

# Python 3.11+
python3 --version

# pnpm
pnpm --version
```

### Clone Repository

```bash
git clone https://github.com/dlnk/dlnk-ide.git
cd dlnk-ide
```

### Install Dependencies

```bash
# VS Code fork
cd vscode-fork
pnpm install

# Extension
cd ../extension
pnpm install

# Backend
cd ../backend
pip install -r requirements.txt
```

### Build

```bash
# Build VS Code fork
cd vscode-fork
pnpm run compile

# Build Extension
cd ../extension
pnpm run build

# Package
pnpm run package
```

### Run Development

```bash
# Run VS Code in development mode
cd vscode-fork
pnpm run watch

# Run AI Bridge
cd ../backend/ai-bridge
python bridge.py

# Run License Server
cd ../backend/license
python server.py
```

---

## 🔧 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Changes

- Follow coding standards
- Write tests
- Update documentation

### 3. Test

```bash
# Run tests
pnpm test

# Run linter
pnpm lint
```

### 4. Commit

```bash
git add .
git commit -m "feat: add my feature"
```

### 5. Push and Create PR

```bash
git push origin feature/my-feature
```

---

## 📚 Documentation

| Document | คำอธิบาย |
|----------|----------|
| [Architecture](architecture.md) | รายละเอียดสถาปัตยกรรม |
| [API Reference](api-reference.md) | เอกสาร API |
| [Extension Dev](extension-dev.md) | พัฒนา Extension |
| [Contributing](contributing.md) | แนวทางการมีส่วนร่วม |
| [Security](security.md) | แนวทางด้านความปลอดภัย |

---

## 🔗 Related Resources

- [VS Code API](https://code.visualstudio.com/api)
- [Electron Documentation](https://www.electronjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [gRPC Documentation](https://grpc.io/docs/)

---

## 📞 Support

- GitHub Issues: [dlnk/dlnk-ide/issues](https://github.com/dlnk/dlnk-ide/issues)
- Email: dev@dlnk.io
- Telegram: @dlnk_dev

---

**ถัดไป:** [Architecture Overview →](architecture.md)
