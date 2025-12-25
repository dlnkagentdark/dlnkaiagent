# dLNk Security Module v1.0

ระบบ Security & Protection สำหรับ dLNk IDE

## Features

### 1. Prompt Filter
- บล็อก Prompt Injection attacks
- ตรวจจับการโจมตี dLNk/AntiGravity
- กรอง Prompt อันตรายหลายประเภท
- รองรับ Pattern matching และ Keyword detection

### 2. Activity Logger
- บันทึกกิจกรรมผู้ใช้ทั้งหมด
- รองรับการเข้ารหัส Log
- Auto-rotate log files
- ค้นหาและกรอง logs

### 3. Anomaly Detection
- Rate Limiting (per minute/hour/day)
- Brute Force Detection
- ตรวจจับพฤติกรรมผิดปกติ
- Risk scoring system

### 4. Alert System
- แจ้งเตือนผ่าน Telegram
- ระดับความรุนแรง 4 ระดับ
- Emergency Shutdown system
- Rate limiting สำหรับ alerts

### 5. Encryption
- Token Encryption (API keys, secrets)
- Config Encryption
- Log Encryption
- Secure storage

## Installation

```bash
# Clone หรือ copy โฟลเดอร์ security ไปยังโปรเจค
cp -r security /path/to/your/project/

# ติดตั้ง dependencies (optional)
pip install cryptography aiohttp
```

## Quick Start

### Basic Usage

```python
from security import get_security_system

# Initialize
security = get_security_system()

# Filter prompt
result = security.filter_prompt(
    "User prompt here",
    user_id="user123"
)

if result['allowed']:
    # Process prompt
    pass
else:
    # Handle blocked prompt
    print(result['response'])
```

### With Telegram Alerts

```python
from security import init_security

security = init_security(
    telegram_bot_token="YOUR_BOT_TOKEN",
    telegram_chat_id="YOUR_CHAT_ID"
)
```

### Prompt Filter Only

```python
from security.prompt_filter import create_filter

pf = create_filter()
result = pf.filter("user prompt", user_id="user123")

if result.allowed:
    print("Prompt is safe")
else:
    print(f"Blocked: {result.reason}")
```

### Rate Limiting

```python
from security.anomaly import RateLimiter, RateLimitConfig

config = RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=500
)
limiter = RateLimiter(config)

status = limiter.check("user123")
if status.allowed:
    # Process request
    pass
else:
    print(f"Rate limited: {status.message}")
```

### Activity Logging

```python
from security.activity import ActivityLogger, ActivityType

logger = ActivityLogger(log_dir="./logs")

logger.log(
    user_id="user123",
    action="code_generation",
    action_type=ActivityType.AI_INTERACTION,
    details={"model": "gpt-4", "tokens": 150}
)
```

### Encryption

```python
from security.encryption import TokenEncryption, SecureTokenStorage

# Encrypt token
enc = TokenEncryption()
encrypted = enc.encrypt("sk-api-key-12345")
decrypted = enc.decrypt(encrypted)

# Secure storage
storage = SecureTokenStorage()
storage.store("openai_key", "sk-api-key-12345")
key = storage.retrieve("openai_key")
```

## Integration with AI Bridge

### Middleware Approach

```python
from security.prompt_filter import PromptFilterMiddleware, create_filter

pf = create_filter()
middleware = PromptFilterMiddleware(pf)

# In your AI Bridge
def process_prompt(prompt, user_id):
    result = middleware.process(prompt, user_id)
    if not result['allowed']:
        return {'error': result['response']}
    
    # Continue processing...
```

### Direct Integration

```python
from security.prompt_filter import integrate_with_ai_bridge

# Integrate with existing AI Bridge
integrate_with_ai_bridge(your_ai_bridge)
```

## Configuration

### Environment Variables

```bash
# Telegram
export DLNK_TELEGRAM_BOT_TOKEN="your_bot_token"
export DLNK_TELEGRAM_ADMIN_ID="your_chat_id"

# Encryption keys (optional, auto-generated if not set)
export DLNK_ENCRYPTION_KEY="your_32_byte_key"
```

### Config File

```python
from security.config import security_config

# Modify settings
security_config.LOG_DIR = "/custom/log/path"
security_config.ENCRYPT_LOGS = True
security_config.MAX_REQUESTS_PER_MINUTE = 100
```

## Module Structure

```
security/
├── __init__.py           # Main exports
├── main.py               # SecuritySystem class
├── config.py             # Configuration
├── prompt_filter/        # Prompt filtering
│   ├── patterns.py       # Attack patterns
│   ├── analyzer.py       # Prompt analysis
│   ├── filter.py         # Main filter
│   └── logger.py         # Filter logging
├── activity/             # Activity tracking
│   ├── logger.py         # Activity logger
│   ├── tracker.py        # Session tracker
│   └── storage.py        # Activity storage
├── anomaly/              # Anomaly detection
│   ├── detector.py       # Anomaly detector
│   ├── rate_limiter.py   # Rate limiting
│   └── brute_force.py    # Brute force detection
├── alerts/               # Alert system
│   ├── alert_manager.py  # Alert management
│   ├── telegram_alert.py # Telegram integration
│   └── emergency.py      # Emergency shutdown
├── encryption/           # Encryption utilities
│   ├── token_encryption.py
│   ├── config_encryption.py
│   └── log_encryption.py
├── utils/                # Utilities
│   └── helpers.py        # Helper functions
├── tests/                # Test suite
└── examples/             # Usage examples
```

## Testing

```bash
# Run all tests
cd security
python -m pytest tests/

# Run specific test
python tests/test_prompt_filter.py
python tests/test_anomaly.py
python tests/test_encryption.py
```

## API Reference

### SecuritySystem

| Method | Description |
|--------|-------------|
| `filter_prompt(prompt, user_id)` | Filter a prompt |
| `check_rate_limit(user_id)` | Check rate limit |
| `record_login(user_id, success)` | Record login attempt |
| `log_activity(user_id, action)` | Log activity |
| `get_stats()` | Get statistics |
| `trigger_emergency(reason)` | Trigger emergency |

### PromptFilter

| Method | Description |
|--------|-------------|
| `filter(prompt, user_id)` | Filter prompt |
| `add_pattern(pattern, severity)` | Add custom pattern |
| `get_stats()` | Get filter statistics |

### RateLimiter

| Method | Description |
|--------|-------------|
| `check(user_id)` | Check rate limit |
| `is_allowed(user_id)` | Quick check |
| `reset_user(user_id)` | Reset user limit |
| `block_user(user_id, minutes)` | Block user |

### AlertManager

| Method | Description |
|--------|-------------|
| `send_alert(title, message, severity)` | Send alert |
| `info/warning/high/critical(...)` | Convenience methods |
| `acknowledge(alert_id)` | Acknowledge alert |
| `get_alerts(severity, limit)` | Get alerts |

## Security Best Practices

1. **Always filter prompts** before sending to AI
2. **Enable rate limiting** to prevent abuse
3. **Log all activities** for audit trail
4. **Encrypt sensitive data** (tokens, configs)
5. **Set up Telegram alerts** for real-time monitoring
6. **Review logs regularly** for suspicious activity
7. **Keep patterns updated** for new attack vectors

## License

MIT License - dLNk Team 2024
