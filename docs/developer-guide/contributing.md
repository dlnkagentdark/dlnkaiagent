# 🤝 Contributing Guide

แนวทางการมีส่วนร่วมในการพัฒนา dLNk IDE

---

## 📋 Overview

ขอบคุณที่สนใจมีส่วนร่วมในการพัฒนา dLNk IDE! เอกสารนี้จะอธิบายขั้นตอนและแนวทางในการ contribute

---

## 🚀 Getting Started

### 1. Fork Repository

1. ไปที่ GitHub repository
2. คลิก "Fork"
3. Clone fork ของคุณ:

```bash
git clone https://github.com/YOUR_USERNAME/dlnk-ide.git
cd dlnk-ide
```

### 2. Setup Development Environment

```bash
# ติดตั้ง dependencies
pnpm install

# Setup pre-commit hooks
pnpm run setup-hooks

# Build
pnpm run build
```

### 3. Create Branch

```bash
# สร้าง branch ใหม่
git checkout -b feature/my-feature

# หรือสำหรับ bug fix
git checkout -b fix/bug-description
```

---

## 📝 Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | คำอธิบาย |
|------|----------|
| `feat` | Feature ใหม่ |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting, missing semicolons |
| `refactor` | Code refactoring |
| `test` | Adding tests |
| `chore` | Maintenance |
| `perf` | Performance improvement |

### Examples

```bash
# Feature
git commit -m "feat(chat): add message history export"

# Bug fix
git commit -m "fix(license): correct expiry date calculation"

# Documentation
git commit -m "docs(api): update WebSocket examples"

# With body
git commit -m "feat(completion): add multi-line completion support

- Support for completing multiple lines
- Add context-aware suggestions
- Improve performance for large files

Closes #123"
```

---

## 🔄 Pull Request Process

### 1. Before Creating PR

- [ ] Code builds without errors
- [ ] All tests pass
- [ ] Linter passes
- [ ] Documentation updated
- [ ] Commit messages follow guidelines

### 2. Create Pull Request

1. Push branch ไปยัง fork:
   ```bash
   git push origin feature/my-feature
   ```

2. ไปที่ GitHub และสร้าง Pull Request

3. กรอก PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test these changes

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Added comments where necessary
- [ ] Updated documentation
- [ ] Added tests
- [ ] All tests pass
```

### 3. Code Review

- Maintainer จะ review PR
- แก้ไขตาม feedback
- PR จะถูก merge เมื่อได้รับ approval

---

## 💻 Code Style

### TypeScript

```typescript
// ใช้ 4 spaces สำหรับ indentation
// ใช้ single quotes
// ใช้ semicolons

// Good
function calculateSum(a: number, b: number): number {
    return a + b;
}

// Bad
function calculateSum(a,b){
return a+b
}
```

### Python

```python
# ใช้ 4 spaces สำหรับ indentation
# Follow PEP 8
# ใช้ type hints

# Good
def calculate_sum(a: int, b: int) -> int:
    """Calculate sum of two numbers."""
    return a + b

# Bad
def calculateSum(a,b):
    return a+b
```

### Linting

```bash
# TypeScript
pnpm run lint

# Python
pip install flake8 black
flake8 .
black .
```

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pnpm test

# Specific test file
pnpm test -- src/test/suite/extension.test.ts

# With coverage
pnpm test -- --coverage
```

### Writing Tests

```typescript
// src/test/suite/myFeature.test.ts
import * as assert from 'assert';
import { myFunction } from '../../myFeature';

suite('My Feature Test Suite', () => {
    test('should return correct result', () => {
        const result = myFunction(1, 2);
        assert.strictEqual(result, 3);
    });
    
    test('should handle edge cases', () => {
        const result = myFunction(0, 0);
        assert.strictEqual(result, 0);
    });
});
```

### Test Coverage

- ต้องมี coverage อย่างน้อย 80%
- ทุก feature ใหม่ต้องมี tests

---

## 📁 Project Structure

```
dlnk-ide/
├── vscode-fork/              # VS Code fork
│   ├── src/                  # Source code
│   └── test/                 # Tests
├── extension/                # dLNk Extension
│   ├── src/                  # Source code
│   └── test/                 # Tests
├── backend/                  # Backend services
│   ├── ai-bridge/            # AI Bridge
│   ├── license/              # License server
│   └── tests/                # Tests
├── admin-console/            # Admin app
├── telegram-bot/             # Telegram bot
├── docs/                     # Documentation
└── scripts/                  # Build scripts
```

---

## 🐛 Bug Reports

### Before Reporting

1. ค้นหาว่ามี issue ที่เหมือนกันหรือไม่
2. ทดสอบกับเวอร์ชันล่าสุด
3. รวบรวมข้อมูลที่จำเป็น

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11]
- dLNk IDE Version: [e.g., 1.0.0]
- Extension Version: [e.g., 0.1.0]

## Screenshots
If applicable

## Additional Context
Any other relevant information
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should it work?

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other relevant information
```

---

## 📚 Documentation

### When to Update Docs

- เพิ่ม feature ใหม่
- เปลี่ยน API
- แก้ไข behavior
- เพิ่ม configuration options

### Documentation Structure

```
docs/
├── user-guide/           # สำหรับผู้ใช้ทั่วไป
├── admin-guide/          # สำหรับ Admin
├── developer-guide/      # สำหรับนักพัฒนา
├── test-plan/            # Test documentation
└── CHANGELOG.md          # Change history
```

### Writing Style

- ใช้ภาษาที่เข้าใจง่าย
- ให้ตัวอย่างที่ชัดเจน
- ใช้ screenshots เมื่อจำเป็น
- อัพเดท table of contents

---

## 🏷️ Versioning

เราใช้ [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes
```

### Examples

- `1.0.0` → `2.0.0`: Breaking API change
- `1.0.0` → `1.1.0`: New feature added
- `1.0.0` → `1.0.1`: Bug fix

---

## 🔐 Security

### Reporting Security Issues

**อย่ารายงาน security issues ผ่าน public issues!**

ส่งอีเมลไปที่: security@dlnk.io

รวมข้อมูล:
- คำอธิบายปัญหา
- ขั้นตอนการ reproduce
- Potential impact
- Suggested fix (ถ้ามี)

---

## 📞 Getting Help

- GitHub Discussions
- Telegram: @dlnk_dev
- Email: dev@dlnk.io

---

## 🎉 Recognition

Contributors จะได้รับการ recognize ใน:
- CONTRIBUTORS.md
- Release notes
- Website credits

---

## 📜 Code of Conduct

### Our Standards

- ใช้ภาษาที่เป็นมิตร
- เคารพความคิดเห็นที่แตกต่าง
- รับ feedback อย่างสร้างสรรค์
- Focus on what's best for the community

### Unacceptable Behavior

- Harassment
- Trolling
- Personal attacks
- Publishing private information

### Enforcement

ผู้ละเมิดอาจถูก:
- Warning
- Temporary ban
- Permanent ban

---

ขอบคุณที่มีส่วนร่วมในการพัฒนา dLNk IDE! 🙏

---

**ก่อนหน้า:** [← Extension Development](extension-dev.md)  
**ถัดไป:** [Security Guidelines →](security.md)
