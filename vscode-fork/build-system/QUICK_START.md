# dLNk IDE - Quick Start Guide
**Welcome to dLNk IDE!** 🎉

Get started with AI-powered coding in 5 minutes.

---

## 📥 Installation

### Windows
1. Download `dLNk-IDE-1.0.0-win-x64.exe`
2. Run the installer
3. Follow the installation wizard
4. Launch dLNk IDE from Start Menu

### macOS
1. Download `dLNk-IDE-1.0.0-mac.dmg`
2. Open the DMG file
3. Drag dLNk IDE to Applications folder
4. Launch from Applications

### Linux (Ubuntu/Debian)
```bash
# Download .deb package
wget https://releases.dlnk.dev/dLNk-IDE-1.0.0-linux-x64.deb

# Install
sudo dpkg -i dLNk-IDE-1.0.0-linux-x64.deb

# Fix dependencies if needed
sudo apt-get install -f

# Launch
dlnk-ide
```

### Linux (AppImage)
```bash
# Download AppImage
wget https://releases.dlnk.dev/dLNk-IDE-1.0.0-linux-x64.AppImage

# Make executable
chmod +x dLNk-IDE-1.0.0-linux-x64.AppImage

# Run
./dLNk-IDE-1.0.0-linux-x64.AppImage
```

---

## 🔐 First Launch

### 1. Login or Register

**First Time Users:**
- Click **Register**
- Enter email and password
- Receive license key via email
- Enter license key

**Existing Users:**
- Click **Login**
- Enter email and password
- Your license will be validated automatically

### 2. License Activation

Your license key format: `DLNK-XXXX-XXXX-XXXX-XXXX`

**License Types:**
- **Trial:** 7 days, all features
- **Personal:** 1 year, single device
- **Professional:** 1 year, 3 devices
- **Enterprise:** Unlimited, custom support

---

## 🤖 Using AI Features

### Open AI Chat Panel

**Method 1:** Click the dLNk AI icon in the left sidebar  
**Method 2:** Press `Ctrl+Shift+A` (Windows/Linux) or `Cmd+Shift+A` (Mac)  
**Method 3:** Command Palette → "dLNk AI: Open Chat"

### Basic AI Commands

#### 1. Ask Questions
```
Type in chat: "How do I create a REST API in Python?"
```

#### 2. Explain Code
1. Select code in editor
2. Right-click → "dLNk AI: Explain Selected Code"
3. Or press `Ctrl+Shift+E`

#### 3. Fix Code
1. Select problematic code
2. Right-click → "dLNk AI: Fix Selected Code"
3. AI will suggest fixes

#### 4. Generate Code
```
Type in chat: "Generate a function to sort array of objects by date"
```

---

## ⚡ Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Open AI Chat | `Ctrl+Shift+A` | `Cmd+Shift+A` |
| Explain Code | `Ctrl+Shift+E` | `Cmd+Shift+E` |
| Command Palette | `Ctrl+Shift+P` | `Cmd+Shift+P` |
| Quick Open | `Ctrl+P` | `Cmd+P` |
| Terminal | `Ctrl+` ` | `Cmd+` ` |

---

## 🎨 Customization

### Change Theme
1. File → Preferences → Color Theme
2. Select "dLNk Dark" (default) or any VSCode theme

### AI Settings
1. File → Preferences → Settings
2. Search "dLNk AI"
3. Configure:
   - Auto-connect on startup
   - Streaming response
   - Server URL (if using custom backend)

---

## 💡 Tips & Tricks

### 1. Context-Aware AI
Select code before asking questions for better context:
```python
# Select this function
def calculate_total(items):
    return sum(item.price for item in items)

# Then ask: "Can you optimize this function?"
```

### 2. Multi-line Prompts
Use Shift+Enter for multi-line prompts in chat:
```
Create a Python class that:
- Connects to PostgreSQL
- Has CRUD operations
- Uses connection pooling
```

### 3. Code Snippets
Ask AI to generate snippets:
```
"Create a React component for user login form with validation"
```

### 4. Export Chat History
- Click menu (⋮) in chat panel
- Select "Export History"
- Save as JSON or Markdown

---

## 🔧 Troubleshooting

### AI Chat Not Responding

**Check Connection:**
1. Look for green dot in AI panel (connected)
2. If red, check Settings → dLNk AI → Server URL
3. Default: `ws://localhost:8765`

**Restart Backend:**
```bash
# If running locally
docker-compose restart ai-bridge
```

### License Issues

**Invalid License:**
- Check email for correct license key
- Ensure no extra spaces when pasting
- Contact support if expired

**Hardware ID Changed:**
- Contact support to unbind old device
- Reactivate on new device

### Performance Issues

**Slow Response:**
- Check internet connection
- Try different AI provider in settings
- Restart IDE

---

## 📚 Learn More

### Documentation
- **User Guide:** https://docs.dlnk.dev/user-guide
- **API Reference:** https://docs.dlnk.dev/api
- **Video Tutorials:** https://youtube.com/@dlnk-ide

### Community
- **Discord:** https://discord.gg/dlnk
- **GitHub:** https://github.com/dlnk/dlnk-ide
- **Forum:** https://forum.dlnk.dev

### Support
- **Email:** support@dlnk.dev
- **Telegram:** @dlnk_support
- **FAQ:** https://dlnk.dev/faq

---

## 🎯 Next Steps

1. ✅ Install dLNk IDE
2. ✅ Activate license
3. ✅ Try AI chat
4. 📖 Read full documentation
5. 🎓 Watch video tutorials
6. 💬 Join community

---

## 🚀 Pro Tips

### For Python Developers
```
"Generate FastAPI endpoint with Pydantic validation"
"Create pytest fixtures for database testing"
"Optimize this pandas dataframe operation"
```

### For JavaScript Developers
```
"Convert this callback to async/await"
"Create React hooks for API calls"
"Generate TypeScript interfaces from this JSON"
```

### For DevOps
```
"Create Dockerfile for Node.js app"
"Generate Kubernetes deployment YAML"
"Write GitHub Actions workflow for CI/CD"
```

---

**Happy Coding with dLNk IDE!** 🎉

*No Limits AI - Powered by Your Imagination*

---

*Version 1.0.0 | Last Updated: 2025-12-24*
