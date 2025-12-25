# dLNk IDE - Icon Integration Guide

**Created:** 2024-12-24  
**Author:** AI-02 (VS Code Core Developer)  
**Purpose:** Guide for integrating dLNk branding icons into VS Code fork

---

## 📦 Available Assets

### Logo Files (from AI-04)
```
ui-assets/logo/
├── dlnk-logo.svg          (4.0 KB) - Vector logo
├── dlnk-logo-16.png       (295 B)  - Favicon
├── dlnk-logo-32.png       (566 B)  - Small icon
├── dlnk-logo-64.png       (893 B)  - Medium icon
├── dlnk-logo-128.png      (1.6 KB) - Standard icon
├── dlnk-logo-256.png      (3.0 KB) - Large icon
├── dlnk-logo-512.png      (6.0 KB) - Extra large icon
└── dlnk-logo.ico          (317 B)  - Windows icon
```

### Icon Files
```
ui-assets/icons/
└── activity-bar-icon.svg  (668 B)  - Activity bar icon
```

---

## 🎯 Integration Plan

### 1. Application Icons (Product Icons)

**Location in VS Code:** `resources/[platform]/`

#### Windows
- **Path:** `resources/win32/code.ico`
- **Replace with:** `dlnk-logo.ico`
- **Usage:** Taskbar, window title, executable icon

#### macOS
- **Path:** `resources/darwin/code.icns`
- **Action:** Convert PNG to ICNS format
- **Command:** 
  ```bash
  # Create iconset
  mkdir dlnk-logo.iconset
  cp dlnk-logo-16.png dlnk-logo.iconset/icon_16x16.png
  cp dlnk-logo-32.png dlnk-logo.iconset/icon_16x16@2x.png
  cp dlnk-logo-32.png dlnk-logo.iconset/icon_32x32.png
  cp dlnk-logo-64.png dlnk-logo.iconset/icon_32x32@2x.png
  cp dlnk-logo-128.png dlnk-logo.iconset/icon_128x128.png
  cp dlnk-logo-256.png dlnk-logo.iconset/icon_128x128@2x.png
  cp dlnk-logo-256.png dlnk-logo.iconset/icon_256x256.png
  cp dlnk-logo-512.png dlnk-logo.iconset/icon_256x256@2x.png
  cp dlnk-logo-512.png dlnk-logo.iconset/icon_512x512.png
  
  # Convert to ICNS (requires macOS or iconutil alternative)
  iconutil -c icns dlnk-logo.iconset -o dlnk-logo.icns
  ```

#### Linux
- **Path:** `resources/linux/code.png`
- **Replace with:** `dlnk-logo-512.png` (renamed to `code.png`)
- **Usage:** Desktop icon, application menu

---

### 2. Product Icon References

**File:** `product.json`

Update icon references:
```json
{
  "linuxIconName": "dlnk-ide",
  "darwinBundleIdentifier": "com.dlnk.ide"
}
```

**Desktop Entry (Linux):**
- **Path:** `resources/linux/code.desktop`
- Update `Icon=dlnk-ide`

---

### 3. Web/UI Icons

**Location:** `src/vs/workbench/browser/parts/`

#### Favicon
- **Path:** `src/vs/workbench/browser/parts/editor/media/favicon.ico`
- **Replace with:** `dlnk-logo.ico`

#### Welcome Page
- **Path:** `src/vs/workbench/contrib/welcome/page/browser/media/`
- Add `dlnk-logo.svg` for welcome screen

---

### 4. Activity Bar Icon (Extension)

**Note:** Activity bar icons are typically provided by extensions, not core VS Code.

For dLNk AI Extension (handled by AI-03):
- **Path:** `extensions/dlnk-ai/media/activity-bar-icon.svg`
- **Usage:** Shows in activity bar when extension is active

---

## 🔧 Implementation Steps

### Step 1: Prepare Icon Files
```bash
# Create directory structure
mkdir -p vscode-fork/resources/win32
mkdir -p vscode-fork/resources/darwin
mkdir -p vscode-fork/resources/linux
mkdir -p vscode-fork/src/vs/workbench/browser/parts/editor/media

# Copy Windows icon
cp ui-assets/logo/dlnk-logo.ico vscode-fork/resources/win32/code.ico

# Copy Linux icon
cp ui-assets/logo/dlnk-logo-512.png vscode-fork/resources/linux/code.png

# Copy favicon
cp ui-assets/logo/dlnk-logo.ico vscode-fork/src/vs/workbench/browser/parts/editor/media/favicon.ico
```

### Step 2: Generate macOS ICNS (if possible)
```bash
# This requires macOS or a tool like libicns
# For now, document the requirement
echo "macOS ICNS generation requires macOS environment or iconutil alternative"
```

### Step 3: Update Desktop Entry (Linux)
```bash
# Edit resources/linux/code.desktop
sed -i 's/Icon=code/Icon=dlnk-ide/g' vscode-fork/resources/linux/code.desktop
```

### Step 4: Update Build Scripts
- Ensure build scripts reference new icon names
- Update `build/gulpfile.vscode.js` if needed

---

## 📋 Checklist

- [ ] Windows icon (`.ico`) replaced
- [ ] Linux icon (`.png`) replaced
- [ ] macOS icon (`.icns`) generated and replaced
- [ ] Favicon replaced
- [ ] Desktop entry updated
- [ ] Build scripts verified
- [ ] Test build on each platform
- [ ] Document in CHANGES.md

---

## 🚨 Important Notes

1. **macOS ICNS:** Requires macOS environment or `png2icns` tool
2. **Build Testing:** Icons only visible after full build
3. **Extension Icons:** Activity bar icons handled by AI-03 extension
4. **Cache Clearing:** May need to clear icon cache on some systems

---

## 📝 Files to Upload

After integration:
```
vscode-fork/
├── resources/
│   ├── win32/code.ico
│   ├── darwin/code.icns (if generated)
│   ├── linux/code.png
│   └── linux/code.desktop (updated)
├── src/vs/workbench/browser/parts/editor/media/
│   └── favicon.ico
└── ICON_INTEGRATION_GUIDE.md (this file)
```

---

**Status:** Ready for implementation  
**Next:** Execute integration steps
