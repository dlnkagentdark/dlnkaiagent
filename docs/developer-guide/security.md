# 🔐 Security Guidelines

แนวทางด้านความปลอดภัยสำหรับ dLNk IDE

---

## 📋 Overview

เอกสารนี้อธิบายมาตรการความปลอดภัยและแนวทางปฏิบัติสำหรับ dLNk IDE

---

## 🛡️ Security Architecture

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  - Input validation                                          │
│  - Output encoding                                           │
│  - Session management                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Business Layer                            │
│  - Prompt filtering                                          │
│  - Rate limiting                                             │
│  - Anomaly detection                                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    Data Layer                                │
│  - Encryption at rest                                        │
│  - Encryption in transit                                     │
│  - Access control                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Authentication & Authorization

### License Authentication

```python
# License verification flow
def verify_license(license_key: str, hardware_id: str) -> dict:
    # 1. Validate format
    if not is_valid_format(license_key):
        raise InvalidLicenseError("Invalid license format")
    
    # 2. Check database
    license = db.get_license(license_key)
    if not license:
        raise InvalidLicenseError("License not found")
    
    # 3. Check expiry
    if license.expires_at < datetime.now():
        raise LicenseExpiredError("License expired")
    
    # 4. Check hardware binding
    if license.hardware_id and license.hardware_id != hardware_id:
        raise HardwareMismatchError("Hardware mismatch")
    
    # 5. Generate token
    token = generate_jwt(license)
    
    return {
        "valid": True,
        "token": token,
        "expires_at": license.expires_at
    }
```

### Admin Authentication

```python
# Admin login with 2FA
def admin_login(admin_key: str, otp: str) -> dict:
    # 1. Verify admin key
    admin = db.get_admin_by_key(admin_key)
    if not admin:
        log_failed_login(admin_key)
        raise AuthenticationError("Invalid credentials")
    
    # 2. Check account status
    if admin.status != "active":
        raise AuthenticationError("Account suspended")
    
    # 3. Verify 2FA
    if admin.two_factor_enabled:
        if not verify_totp(admin.totp_secret, otp):
            log_failed_2fa(admin.id)
            raise AuthenticationError("Invalid 2FA code")
    
    # 4. Generate session
    session = create_session(admin)
    
    return {
        "success": True,
        "token": session.token,
        "expires_at": session.expires_at
    }
```

---

## 🚫 Prompt Filtering

### Purpose

ป้องกันการใช้ AI ในทางที่ไม่เหมาะสม:
- Prompt Injection attacks
- Jailbreak attempts
- Malicious content generation
- Data extraction attempts

### Implementation

```python
import re
from typing import Tuple

class PromptFilter:
    BLOCKED_PATTERNS = [
        # Prompt injection
        r"ignore.*previous.*instructions",
        r"disregard.*above",
        r"forget.*everything",
        
        # Jailbreak attempts
        r"DAN.*mode",
        r"developer.*mode",
        r"pretend.*you.*are",
        
        # Malicious requests
        r"how.*to.*hack",
        r"create.*malware",
        r"bypass.*security",
        
        # Data extraction
        r"reveal.*system.*prompt",
        r"show.*api.*key",
        r"dump.*database",
        
        # dLNk specific
        r"attack.*dlnk",
        r"crack.*license",
        r"steal.*token",
    ]
    
    SUSPICIOUS_PATTERNS = [
        r"base64",
        r"eval\s*\(",
        r"exec\s*\(",
        r"<script>",
        r"javascript:",
    ]
    
    def filter(self, prompt: str) -> Tuple[bool, str]:
        """
        Filter prompt for security violations.
        
        Returns:
            Tuple[bool, str]: (is_allowed, reason)
        """
        prompt_lower = prompt.lower()
        
        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                self.log_violation(prompt, pattern)
                return False, f"Blocked: Security violation"
        
        # Check suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                self.log_suspicious(prompt, pattern)
                # Allow but flag for review
        
        return True, ""
    
    def log_violation(self, prompt: str, pattern: str):
        """Log security violation for review."""
        db.insert_security_log({
            "type": "prompt_blocked",
            "prompt": prompt[:500],  # Truncate
            "pattern": pattern,
            "timestamp": datetime.now()
        })
        
        # Alert admins
        send_telegram_alert(
            f"🚨 Prompt Filter Violation\n"
            f"Pattern: {pattern}\n"
            f"Prompt: {prompt[:100]}..."
        )
```

### Configuration

```yaml
# security_config.yaml
prompt_filter:
  enabled: true
  sensitivity: "medium"  # low, medium, high
  
  # Custom patterns
  custom_blocked_patterns:
    - "pattern1"
    - "pattern2"
  
  # Whitelist
  whitelist:
    - "allowed_pattern"
  
  # Actions
  on_violation:
    log: true
    alert: true
    block: true
    
  # Rate limiting for violations
  violation_threshold: 5  # violations before suspension
  violation_window: 3600  # seconds
```

---

## 🔒 Data Protection

### Encryption at Rest

```python
from cryptography.fernet import Fernet

class DataEncryption:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        return self.cipher.encrypt(data.encode())
    
    def decrypt(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode()

# Usage
encryption = DataEncryption(settings.ENCRYPTION_KEY)

# Encrypt sensitive data before storing
encrypted_token = encryption.encrypt(api_token)
db.store("api_token", encrypted_token)

# Decrypt when needed
encrypted = db.get("api_token")
api_token = encryption.decrypt(encrypted)
```

### Encryption in Transit

```python
# Always use HTTPS
import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

# For WebSocket
async with websockets.connect(
    "wss://api.dlnk.io/ws",
    ssl=ssl_context
) as ws:
    await ws.send(message)
```

### Secure Storage

```typescript
// VS Code Extension - Use SecretStorage
async function storeApiKey(context: vscode.ExtensionContext, key: string) {
    await context.secrets.store('dlnk.apiKey', key);
}

async function getApiKey(context: vscode.ExtensionContext): Promise<string | undefined> {
    return await context.secrets.get('dlnk.apiKey');
}
```

---

## 🚦 Rate Limiting

### Implementation

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(
        self,
        user_id: str,
        limit: int,
        window: int  # seconds
    ) -> bool:
        now = datetime.now()
        window_start = now - timedelta(seconds=window)
        
        # Clean old requests
        self.requests[user_id] = [
            req for req in self.requests[user_id]
            if req > window_start
        ]
        
        # Check limit
        if len(self.requests[user_id]) >= limit:
            return False
        
        # Record request
        self.requests[user_id].append(now)
        return True

# Usage
rate_limiter = RateLimiter()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = get_user_id(request)
    
    if not rate_limiter.is_allowed(user_id, limit=60, window=60):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    return await call_next(request)
```

### Limits by License Type

| License Type | Requests/Minute | Requests/Day |
|--------------|-----------------|--------------|
| Trial | 10 | 100 |
| Standard | 30 | 500 |
| Pro | 60 | 1,000 |
| Enterprise | Unlimited | Unlimited |

---

## 🔍 Anomaly Detection

### Suspicious Activity Detection

```python
class AnomalyDetector:
    def __init__(self):
        self.user_patterns = {}
    
    def check_login(self, user_id: str, ip: str, country: str) -> dict:
        alerts = []
        
        # Get user's normal pattern
        pattern = self.user_patterns.get(user_id, {})
        
        # Check for new IP
        if ip not in pattern.get('known_ips', []):
            alerts.append({
                "type": "new_ip",
                "severity": "medium",
                "message": f"Login from new IP: {ip}"
            })
        
        # Check for new country
        if country not in pattern.get('known_countries', []):
            alerts.append({
                "type": "new_country",
                "severity": "high",
                "message": f"Login from new country: {country}"
            })
        
        # Check for impossible travel
        last_login = pattern.get('last_login')
        if last_login:
            time_diff = datetime.now() - last_login['time']
            if time_diff < timedelta(hours=1):
                if last_login['country'] != country:
                    alerts.append({
                        "type": "impossible_travel",
                        "severity": "critical",
                        "message": f"Impossible travel detected"
                    })
        
        return {"alerts": alerts}
    
    def check_usage(self, user_id: str, requests_count: int) -> dict:
        alerts = []
        
        pattern = self.user_patterns.get(user_id, {})
        avg_requests = pattern.get('avg_daily_requests', 0)
        
        # Check for unusual spike
        if requests_count > avg_requests * 3:
            alerts.append({
                "type": "usage_spike",
                "severity": "medium",
                "message": f"Unusual usage spike: {requests_count} requests"
            })
        
        return {"alerts": alerts}
```

---

## 🛡️ Input Validation

### License Key Validation

```python
import re

def validate_license_key(key: str) -> bool:
    """
    Validate license key format: DLNK-XXXX-XXXX-XXXX-XXXX
    """
    pattern = r'^DLNK-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    return bool(re.match(pattern, key.upper()))
```

### API Input Validation

```python
from pydantic import BaseModel, validator, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    context: dict = Field(default={})
    
    @validator('message')
    def sanitize_message(cls, v):
        # Remove null bytes
        v = v.replace('\x00', '')
        # Limit consecutive whitespace
        v = re.sub(r'\s{10,}', ' ' * 10, v)
        return v

class LicenseRequest(BaseModel):
    license_key: str
    hardware_id: str = Field(..., min_length=32, max_length=64)
    
    @validator('license_key')
    def validate_key(cls, v):
        if not validate_license_key(v):
            raise ValueError('Invalid license key format')
        return v.upper()
```

---

## 📝 Security Logging

### Log Format

```python
import logging
import json
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('security.log')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        self.logger.addHandler(handler)
    
    def log_event(self, event_type: str, data: dict):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        self.logger.info(json.dumps(log_entry))
    
    def log_login_success(self, user_id: str, ip: str):
        self.log_event("login_success", {
            "user_id": user_id,
            "ip": ip
        })
    
    def log_login_failure(self, identifier: str, ip: str, reason: str):
        self.log_event("login_failure", {
            "identifier": identifier,
            "ip": ip,
            "reason": reason
        })
    
    def log_prompt_violation(self, user_id: str, prompt: str, pattern: str):
        self.log_event("prompt_violation", {
            "user_id": user_id,
            "prompt_preview": prompt[:100],
            "matched_pattern": pattern
        })
```

### Log Retention

```yaml
# logging_config.yaml
security_logs:
  retention_days: 90
  rotation:
    max_size: "100MB"
    backup_count: 10
  
  # Sensitive data handling
  mask_patterns:
    - "license_key"
    - "api_key"
    - "password"
```

---

## 🚨 Incident Response

### Response Procedure

1. **Detection**
   - Automated alerts
   - User reports
   - Log analysis

2. **Assessment**
   - Determine severity
   - Identify affected users
   - Assess impact

3. **Containment**
   - Suspend affected accounts
   - Block malicious IPs
   - Revoke compromised tokens

4. **Eradication**
   - Fix vulnerability
   - Update security rules
   - Deploy patches

5. **Recovery**
   - Restore services
   - Notify affected users
   - Monitor for recurrence

6. **Post-Incident**
   - Document incident
   - Update procedures
   - Conduct review

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| **Critical** | Active attack, data breach | Immediate |
| **High** | Vulnerability exploited | < 1 hour |
| **Medium** | Suspicious activity | < 4 hours |
| **Low** | Minor security issue | < 24 hours |

---

## 🔐 Secure Development

### Code Review Checklist

- [ ] Input validation implemented
- [ ] Output encoding applied
- [ ] Authentication checked
- [ ] Authorization verified
- [ ] Sensitive data encrypted
- [ ] Logging implemented
- [ ] Error handling secure
- [ ] Dependencies updated

### Security Testing

```bash
# Static analysis
bandit -r src/

# Dependency check
safety check

# Secret scanning
git secrets --scan
```

---

## 📞 Reporting Security Issues

**อย่ารายงานผ่าน public channels!**

Email: security@dlnk.io

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

Response time: < 48 hours

---

**ก่อนหน้า:** [← Contributing Guide](contributing.md)  
**กลับหน้าหลัก:** [Developer Guide](README.md)
