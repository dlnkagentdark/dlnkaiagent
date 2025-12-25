# dLNk IDE - Build Instructions

## Prerequisites

### System Requirements
- **OS:** Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** 10GB free space
- **Node.js:** v20.x LTS (use nvm for version management)
- **Python:** 3.x (for native module compilation)
- **Git:** Latest version

### Platform-Specific Requirements

#### Windows
```powershell
# Install Visual Studio Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools

# Or install via npm
npm install --global windows-build-tools
```

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y build-essential g++ libx11-dev libxkbfile-dev libsecret-1-dev libkrb5-dev python3 libnss3 libatk-bridge2.0-0 libgtk-3-0 libgbm1
```

---

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/dlnk/dlnk-ide.git
cd dlnk-ide
```

### 2. Apply dLNk Modifications
Copy the modified files from this folder to the cloned repository:

```bash
# Copy product.json
cp vscode-fork/product.json dlnk-ide/product.json

# Copy package.json
cp vscode-fork/package.json dlnk-ide/package.json

# Copy telemetry service (disabled)
cp vscode-fork/modified-files/src/vs/platform/telemetry/common/telemetryService.ts \
   dlnk-ide/src/vs/platform/telemetry/common/telemetryService.ts

# Copy theme
mkdir -p dlnk-ide/extensions/dlnk-theme/themes
cp vscode-fork/theme/dlnk-dark-theme.json \
   dlnk-ide/extensions/dlnk-theme/themes/dlnk-dark-theme.json
```

### 3. Install Dependencies
```bash
cd dlnk-ide
npm install
```

### 4. Build
```bash
# Development build
npm run compile

# Production build
npm run compile-build
```

### 5. Run
```bash
# Development
./scripts/code.sh  # Linux/macOS
./scripts/code.bat # Windows

# Or using npm
npm run watch
```

---

## Build for Distribution

### Windows
```bash
npm run gulp vscode-win32-x64-min
npm run gulp vscode-win32-x64-inno-updater
npm run gulp vscode-win32-x64-archive
```

Output: `.build/win32-x64/`

### macOS
```bash
npm run gulp vscode-darwin-x64-min
npm run gulp vscode-darwin-arm64-min
```

Output: `.build/darwin-x64/` or `.build/darwin-arm64/`

### Linux
```bash
npm run gulp vscode-linux-x64-min
npm run gulp vscode-linux-x64-build-deb
npm run gulp vscode-linux-x64-build-rpm
```

Output: `.build/linux-x64/`

---

## Creating Theme Extension

### 1. Create Extension Structure
```
extensions/dlnk-theme/
├── package.json
├── themes/
│   └── dlnk-dark-theme.json
└── README.md
```

### 2. Extension package.json
```json
{
  "name": "dlnk-theme",
  "displayName": "dLNk Dark Theme",
  "description": "Official dark theme for dLNk IDE",
  "version": "1.0.0",
  "publisher": "dlnk",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": ["Themes"],
  "contributes": {
    "themes": [
      {
        "label": "dLNk Dark",
        "uiTheme": "vs-dark",
        "path": "./themes/dlnk-dark-theme.json"
      }
    ]
  }
}
```

### 3. Set as Default Theme
In `product.json`, add:
```json
{
  "extensionAllowedProposedApi": ["dlnk.dlnk-theme"],
  "builtInExtensions": [
    {
      "name": "dlnk-theme",
      "version": "1.0.0",
      "repo": "local"
    }
  ]
}
```

---

## Icon Replacement

### Required Icon Files

| Platform | File | Size | Format |
|----------|------|------|--------|
| Windows | resources/win32/code.ico | Multi-size | ICO |
| macOS | resources/darwin/code.icns | Multi-size | ICNS |
| Linux | resources/linux/code.png | 512x512 | PNG |
| UI | src/vs/workbench/browser/media/code-icon.svg | Vector | SVG |

### Icon Sizes Required

**Windows ICO:**
- 16x16, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256

**macOS ICNS:**
- 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024

**Linux PNG:**
- 512x512 (primary)
- Also create: 16x16, 22x22, 24x24, 32x32, 48x48, 64x64, 128x128, 256x256

---

## Environment Variables

```bash
# Disable telemetry (already disabled in code, but for safety)
export DLNK_DISABLE_TELEMETRY=1

# Set custom extension gallery (Open VSX)
export DLNK_EXTENSIONS_GALLERY='{"serviceUrl":"https://open-vsx.org/vscode/gallery","itemUrl":"https://open-vsx.org/vscode/item"}'

# Development mode
export NODE_ENV=development
```

---

## Troubleshooting

### Common Issues

#### 1. Native Module Compilation Errors
```bash
# Clear node_modules and rebuild
rm -rf node_modules
npm cache clean --force
npm install
```

#### 2. Electron Download Issues
```bash
# Set mirror
export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
npm install
```

#### 3. Build Memory Issues
```bash
# Increase Node.js memory
export NODE_OPTIONS="--max-old-space-size=8192"
npm run compile
```

#### 4. Permission Issues (Linux)
```bash
# Fix permissions
sudo chown -R $USER:$USER ~/.npm
sudo chown -R $USER:$USER ~/.config
```

---

## CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Build dLNk IDE

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: npm install
        
      - name: Build
        run: npm run compile-build
        
      - name: Package
        run: npm run gulp vscode-${{ matrix.platform }}-min
```

---

## Support

- **Issues:** https://github.com/dlnk/dlnk-ide/issues
- **Documentation:** https://github.com/dlnk/dlnk-ide/wiki
- **Report to AI-01:** Contact via dLNk Team channel

---

**Author:** AI-02 VS Code Core Developer  
**Version:** 1.0.0  
**Last Updated:** 2024-12-25
