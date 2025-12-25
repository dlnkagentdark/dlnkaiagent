# 🎨 dLNk IDE Style Guide

**Version:** 1.0.0  
**Author:** AI-04 UI/UX Designer  
**Last Updated:** December 2025

---

## 📋 Table of Contents

1. [Brand Overview](#brand-overview)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components](#components)
6. [Icons & Logo](#icons--logo)
7. [Animations](#animations)
8. [Accessibility](#accessibility)
9. [Implementation Guidelines](#implementation-guidelines)

---

## 🎯 Brand Overview

### Brand Identity

**dLNk IDE** is an AI-powered development environment designed for modern developers. The visual identity reflects:

- **Innovation** - Cutting-edge AI integration
- **Professionalism** - Clean, focused interface
- **Accessibility** - Easy on the eyes, comfortable for long coding sessions
- **Power** - Advanced capabilities with intuitive controls

### Design Principles

1. **Dark-First Design** - Optimized for extended use
2. **Clarity** - Clear visual hierarchy and readable typography
3. **Consistency** - Unified design language across all components
4. **Performance** - Lightweight, efficient UI elements
5. **Accessibility** - WCAG 2.1 AA compliance

---

## 🎨 Color System

### Primary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **BG Primary** | `#1a1a2e` | `26, 26, 46` | Main background |
| **BG Secondary** | `#16213e` | `22, 33, 62` | Panels, sidebars |
| **BG Tertiary** | `#0f3460` | `15, 52, 96` | Highlights, selections |

### Accent Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Accent Primary** | `#e94560` | `233, 69, 96` | Primary buttons, links, highlights |
| **Accent Secondary** | `#533483` | `83, 52, 131` | Secondary actions, gradients |
| **Success** | `#00d9ff` | `0, 217, 255` | Success states, online status |
| **Warning** | `#ffc107` | `255, 193, 7` | Warnings, cautions |
| **Error** | `#ff4757` | `255, 71, 87` | Errors, destructive actions |

### Text Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Text Primary** | `#ffffff` | Main text, headings |
| **Text Secondary** | `#a0a0a0` | Descriptions, labels |
| **Text Muted** | `#6c757d` | Placeholders, disabled |
| **Text Link** | `#00d9ff` | Links, interactive text |

### Border & Shadow

| Name | Value | Usage |
|------|-------|-------|
| **Border Color** | `#2d2d44` | Borders, dividers |
| **Shadow Color** | `rgba(0, 0, 0, 0.3)` | Drop shadows |

### Color Usage Guidelines

```css
/* Primary Button */
.btn-primary {
    background-color: #e94560;
    color: #ffffff;
}

.btn-primary:hover {
    background-color: #c73e54;
}

/* Secondary Button */
.btn-secondary {
    background-color: #533483;
    color: #ffffff;
}

/* Success State */
.status-success {
    color: #00d9ff;
}

/* Error State */
.status-error {
    color: #ff4757;
}
```

---

## 📝 Typography

### Font Families

| Type | Font | Fallback |
|------|------|----------|
| **Sans-serif** | Inter | -apple-system, BlinkMacSystemFont, Segoe UI, Roboto |
| **Monospace** | Fira Code | Consolas, Monaco, monospace |

### Font Sizes

| Name | Size | Line Height | Usage |
|------|------|-------------|-------|
| **XS** | 11px | 1.25 | Badges, labels |
| **SM** | 13px | 1.4 | Secondary text |
| **MD** | 14px | 1.5 | Body text |
| **LG** | 16px | 1.5 | Emphasized text |
| **XL** | 18px | 1.4 | Section headers |
| **2XL** | 24px | 1.3 | Page titles |
| **3XL** | 32px | 1.2 | Hero text |
| **4XL** | 48px | 1.1 | Logo text |

### Font Weights

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text |
| Medium | 500 | Labels, buttons |
| Semi-bold | 600 | Headings |
| Bold | 700 | Emphasis, logo |

### Typography Examples

```css
/* Heading 1 */
h1 {
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    font-weight: 600;
    line-height: 1.3;
    color: #ffffff;
}

/* Body Text */
p {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.6;
    color: #a0a0a0;
}

/* Code */
code {
    font-family: 'Fira Code', monospace;
    font-size: 13px;
    line-height: 1.5;
}
```

---

## 📐 Spacing & Layout

### Spacing Scale

| Name | Value | Usage |
|------|-------|-------|
| **XS** | 4px | Tight spacing |
| **SM** | 8px | Element gaps |
| **MD** | 16px | Section padding |
| **LG** | 24px | Card padding |
| **XL** | 32px | Section margins |
| **2XL** | 48px | Page sections |
| **3XL** | 64px | Hero sections |

### Border Radius

| Name | Value | Usage |
|------|-------|-------|
| **SM** | 4px | Small elements |
| **MD** | 8px | Buttons, inputs |
| **LG** | 12px | Cards |
| **XL** | 16px | Modals |
| **2XL** | 24px | Large containers |
| **Full** | 9999px | Pills, circles |

### Layout Grid

- **Container Max Width:** 1200px
- **Column Gap:** 24px
- **Row Gap:** 16px

---

## 🧩 Components

### Buttons

#### Primary Button
```css
.btn-primary {
    background-color: #e94560;
    color: #ffffff;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    border: none;
    cursor: pointer;
    transition: background-color 0.15s ease;
}

.btn-primary:hover {
    background-color: #c73e54;
}

.btn-primary:disabled {
    background-color: #0f3460;
    cursor: not-allowed;
    opacity: 0.6;
}
```

#### Secondary Button
```css
.btn-secondary {
    background-color: transparent;
    color: #a0a0a0;
    padding: 12px 24px;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
    border: 1px solid #2d2d44;
    cursor: pointer;
    transition: all 0.15s ease;
}

.btn-secondary:hover {
    background-color: #16213e;
    color: #ffffff;
    border-color: #e94560;
}
```

### Input Fields

```css
.input {
    background-color: #16213e;
    color: #ffffff;
    padding: 12px 16px;
    border-radius: 8px;
    border: 2px solid #2d2d44;
    font-size: 14px;
    transition: border-color 0.15s ease;
}

.input:focus {
    outline: none;
    border-color: #e94560;
}

.input::placeholder {
    color: #6c757d;
}
```

### Cards

```css
.card {
    background-color: #16213e;
    border-radius: 12px;
    border: 1px solid #2d2d44;
    padding: 24px;
}

.card-header {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 16px;
}

.card-body {
    color: #a0a0a0;
}
```

### Tooltips

```css
.tooltip {
    background-color: #0f3460;
    color: #ffffff;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.25);
}
```

---

## 🖼️ Icons & Logo

### Logo Specifications

| Variant | Size | Format | Usage |
|---------|------|--------|-------|
| **Full Logo** | 512x512 | SVG, PNG | Marketing, splash |
| **Medium** | 128x128 | PNG | App icon |
| **Small** | 64x64 | PNG | Favicon |
| **Tiny** | 32x32 | PNG | Tab icon |
| **Micro** | 16x16 | PNG, ICO | System tray |

### Logo Colors

- **Primary Gradient:** `#e94560` → `#533483`
- **AI Indicator:** `#00d9ff`
- **Background:** `#1a1a2e`

### Icon Guidelines

- **Activity Bar Icons:** 24x24px, single color
- **File Icons:** 16x16px
- **Status Icons:** 16x16px
- **Stroke Width:** 2px for outlined icons

---

## ✨ Animations

### Transition Timings

| Name | Duration | Easing | Usage |
|------|----------|--------|-------|
| **Fast** | 0.15s | ease | Hover states |
| **Normal** | 0.25s | ease | Panel transitions |
| **Slow** | 0.4s | ease | Page transitions |
| **Bounce** | 0.3s | cubic-bezier(0.68, -0.55, 0.265, 1.55) | Playful interactions |

### Animation Examples

```css
/* Fade In Up */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-fade-in-up {
    animation: fadeInUp 0.3s ease;
}

/* Loading Dots */
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

.loading-dot {
    animation: bounce 1.4s infinite ease-in-out both;
}

/* Pulse */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.animate-pulse {
    animation: pulse 1.5s infinite;
}
```

---

## ♿ Accessibility

### Color Contrast

All text must meet WCAG 2.1 AA standards:
- **Normal text:** 4.5:1 minimum
- **Large text (18px+):** 3:1 minimum

### Focus States

```css
.focusable:focus {
    outline: 2px solid #e94560;
    outline-offset: 2px;
}

.focusable:focus:not(:focus-visible) {
    outline: none;
}

.focusable:focus-visible {
    outline: 2px solid #e94560;
    outline-offset: 2px;
}
```

### Screen Reader Support

- Use semantic HTML elements
- Include ARIA labels for icons
- Provide alt text for images
- Ensure keyboard navigation

---

## 🛠️ Implementation Guidelines

### CSS Variables Setup

```css
:root {
    /* Colors */
    --dlnk-bg-primary: #1a1a2e;
    --dlnk-bg-secondary: #16213e;
    --dlnk-bg-tertiary: #0f3460;
    --dlnk-accent-primary: #e94560;
    --dlnk-accent-secondary: #533483;
    --dlnk-accent-success: #00d9ff;
    --dlnk-accent-warning: #ffc107;
    --dlnk-accent-error: #ff4757;
    --dlnk-text-primary: #ffffff;
    --dlnk-text-secondary: #a0a0a0;
    --dlnk-text-muted: #6c757d;
    --dlnk-border-color: #2d2d44;
    
    /* Spacing */
    --dlnk-space-xs: 4px;
    --dlnk-space-sm: 8px;
    --dlnk-space-md: 16px;
    --dlnk-space-lg: 24px;
    --dlnk-space-xl: 32px;
    
    /* Border Radius */
    --dlnk-radius-sm: 4px;
    --dlnk-radius-md: 8px;
    --dlnk-radius-lg: 12px;
    
    /* Transitions */
    --dlnk-transition-fast: 0.15s ease;
    --dlnk-transition-normal: 0.25s ease;
}
```

### Python CustomTkinter Colors

```python
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_tertiary': '#0f3460',
    'accent_primary': '#e94560',
    'accent_secondary': '#533483',
    'accent_success': '#00d9ff',
    'accent_warning': '#ffc107',
    'accent_error': '#ff4757',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'text_muted': '#6c757d',
    'border_color': '#2d2d44',
}
```

### File Naming Convention

- **CSS files:** `kebab-case.css` (e.g., `chat-panel.css`)
- **Python files:** `snake_case.py` (e.g., `login_window.py`)
- **Images:** `kebab-case-size.ext` (e.g., `dlnk-logo-128.png`)
- **Icons:** `icon-name.svg` (e.g., `activity-bar-icon.svg`)

---

## 📁 File Structure

```
ui-design/
├── STYLE_GUIDE.md          # This document
├── login/
│   ├── login_window.py     # Login window UI
│   ├── register_window.py  # Registration UI
│   └── screenshots/        # UI screenshots
├── chat-panel/
│   ├── chat.html           # Chat panel HTML
│   ├── chat.css            # Chat panel styles
│   ├── chat.js             # Chat panel logic
│   └── screenshots/        # UI screenshots
├── theme/
│   ├── dlnk-dark-theme.json # VS Code theme
│   ├── colors.css          # CSS variables
│   └── animations.css      # Animation library
├── logo/
│   ├── dlnk-logo.svg       # Vector logo
│   ├── dlnk-logo-16.png    # 16x16 icon
│   ├── dlnk-logo-32.png    # 32x32 icon
│   ├── dlnk-logo-64.png    # 64x64 icon
│   ├── dlnk-logo-128.png   # 128x128 icon
│   ├── dlnk-logo-256.png   # 256x256 icon
│   └── dlnk-logo.ico       # Windows icon
├── icons/
│   ├── activity-bar-icon.svg
│   ├── status-icons.svg      # Status indicator icons
│   └── file-icons/
└── splash/
    ├── splash_screen.py    # Splash screen UI
    └── splash.png          # Splash image
```

---

## ✅ Checklist for New Components

- [ ] Uses official color palette
- [ ] Follows typography guidelines
- [ ] Includes hover/focus states
- [ ] Has proper spacing
- [ ] Supports dark theme
- [ ] Meets accessibility standards
- [ ] Uses consistent border radius
- [ ] Includes appropriate animations
- [ ] Works with keyboard navigation
- [ ] Has proper documentation

---

**Document maintained by AI-04 UI/UX Designer**  
**For questions, contact: AI-01 Controller**
