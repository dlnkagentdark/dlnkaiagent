# 📚 API Reference

เอกสาร API สำหรับ dLNk IDE

---

## 📋 Overview

dLNk IDE มี API หลัก 3 ส่วน:

| API | Port | Purpose |
|-----|------|---------|
| **AI Bridge WebSocket** | 8765 | Real-time AI communication |
| **AI Bridge REST** | 8766 | AI requests via HTTP |
| **License Server** | 8767 | License management |
| **Admin API** | 8768 | Admin operations |

---

## 🔌 AI Bridge WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8765');

ws.onopen = () => {
    console.log('Connected to AI Bridge');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

### Message Format

```typescript
interface Message {
    type: 'chat' | 'completion' | 'explain' | 'refactor';
    id: string;
    payload: any;
}

interface Response {
    type: 'response' | 'stream' | 'error' | 'done';
    id: string;
    payload: any;
}
```

### Chat Request

```json
{
    "type": "chat",
    "id": "msg-123",
    "payload": {
        "message": "How do I create a REST API in Python?",
        "context": {
            "file": "main.py",
            "language": "python",
            "selection": ""
        },
        "history": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help?"}
        ]
    }
}
```

### Chat Response (Streaming)

```json
// Stream chunks
{"type": "stream", "id": "msg-123", "payload": {"content": "To create"}}
{"type": "stream", "id": "msg-123", "payload": {"content": " a REST API"}}
{"type": "stream", "id": "msg-123", "payload": {"content": " in Python..."}}

// Done
{"type": "done", "id": "msg-123", "payload": {"total_tokens": 150}}
```

### Completion Request

```json
{
    "type": "completion",
    "id": "comp-456",
    "payload": {
        "prefix": "def calculate_sum(",
        "suffix": ":\n    pass",
        "language": "python",
        "max_tokens": 100
    }
}
```

### Completion Response

```json
{
    "type": "response",
    "id": "comp-456",
    "payload": {
        "completion": "a: int, b: int) -> int",
        "confidence": 0.95
    }
}
```

### Explain Request

```json
{
    "type": "explain",
    "id": "exp-789",
    "payload": {
        "code": "const result = arr.reduce((a, b) => a + b, 0);",
        "language": "javascript"
    }
}
```

### Refactor Request

```json
{
    "type": "refactor",
    "id": "ref-101",
    "payload": {
        "code": "function foo(x) { return x * 2; }",
        "language": "javascript",
        "instruction": "Convert to arrow function"
    }
}
```

### Error Response

```json
{
    "type": "error",
    "id": "msg-123",
    "payload": {
        "code": "RATE_LIMIT",
        "message": "Rate limit exceeded. Please wait 60 seconds."
    }
}
```

---

## 🌐 AI Bridge REST API

### Base URL

```
http://localhost:8766/api/v1
```

### Authentication

```http
Authorization: Bearer <license_token>
```

### Endpoints

#### POST /chat

Send a chat message.

**Request:**
```http
POST /api/v1/chat
Content-Type: application/json
Authorization: Bearer <token>

{
    "message": "How do I create a REST API?",
    "context": {
        "file": "main.py",
        "language": "python"
    },
    "stream": false
}
```

**Response:**
```json
{
    "success": true,
    "response": "To create a REST API in Python...",
    "tokens_used": 150
}
```

#### POST /completion

Get code completion.

**Request:**
```http
POST /api/v1/completion
Content-Type: application/json
Authorization: Bearer <token>

{
    "prefix": "def calculate_sum(",
    "suffix": ":\n    pass",
    "language": "python"
}
```

**Response:**
```json
{
    "success": true,
    "completion": "a: int, b: int) -> int",
    "confidence": 0.95
}
```

#### POST /explain

Explain code.

**Request:**
```http
POST /api/v1/explain
Content-Type: application/json
Authorization: Bearer <token>

{
    "code": "const result = arr.reduce((a, b) => a + b, 0);",
    "language": "javascript"
}
```

**Response:**
```json
{
    "success": true,
    "explanation": "This code uses the reduce method..."
}
```

#### GET /status

Get AI Bridge status.

**Request:**
```http
GET /api/v1/status
Authorization: Bearer <token>
```

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "providers": {
        "antigravity": "connected",
        "gemini": "available",
        "openai": "available"
    }
}
```

---

## 🔑 License Server API

### Base URL

```
http://localhost:8767/api/v1
```

### Endpoints

#### POST /verify

Verify a license key.

**Request:**
```http
POST /api/v1/verify
Content-Type: application/json

{
    "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
    "hardware_id": "ABC123..."
}
```

**Response (Success):**
```json
{
    "valid": true,
    "license": {
        "type": "pro",
        "expires_at": "2026-12-25T00:00:00Z",
        "features": ["chat", "completion", "explain", "refactor"]
    },
    "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (Invalid):**
```json
{
    "valid": false,
    "error": {
        "code": "LICENSE_EXPIRED",
        "message": "License has expired"
    }
}
```

#### POST /activate

Activate a license on a device.

**Request:**
```http
POST /api/v1/activate
Content-Type: application/json

{
    "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
    "hardware_id": "ABC123...",
    "device_info": {
        "os": "Windows 11",
        "hostname": "MY-PC"
    }
}
```

**Response:**
```json
{
    "success": true,
    "message": "License activated successfully",
    "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### POST /deactivate

Deactivate a license from a device.

**Request:**
```http
POST /api/v1/deactivate
Content-Type: application/json
Authorization: Bearer <token>

{
    "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX"
}
```

**Response:**
```json
{
    "success": true,
    "message": "License deactivated successfully"
}
```

#### GET /status

Get license status.

**Request:**
```http
GET /api/v1/status
Authorization: Bearer <token>
```

**Response:**
```json
{
    "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
    "type": "pro",
    "status": "active",
    "expires_at": "2026-12-25T00:00:00Z",
    "usage": {
        "requests_today": 150,
        "requests_limit": 1000
    }
}
```

---

## 🔧 Admin API

### Base URL

```
http://localhost:8768/api/v1/admin
```

### Authentication

```http
Authorization: Bearer <admin_token>
```

### License Management

#### GET /licenses

List all licenses.

**Request:**
```http
GET /api/v1/admin/licenses?status=active&limit=50&offset=0
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
    "licenses": [
        {
            "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
            "email": "user@email.com",
            "type": "pro",
            "status": "active",
            "created_at": "2025-01-01T00:00:00Z",
            "expires_at": "2026-01-01T00:00:00Z"
        }
    ],
    "total": 100,
    "limit": 50,
    "offset": 0
}
```

#### POST /licenses

Create a new license.

**Request:**
```http
POST /api/v1/admin/licenses
Content-Type: application/json
Authorization: Bearer <admin_token>

{
    "email": "user@email.com",
    "type": "pro",
    "duration_days": 365,
    "hardware_binding": true
}
```

**Response:**
```json
{
    "success": true,
    "license_key": "DLNK-ABCD-EFGH-IJKL-MNOP",
    "expires_at": "2026-12-25T00:00:00Z"
}
```

#### GET /licenses/{key}

Get license details.

**Request:**
```http
GET /api/v1/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
    "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
    "email": "user@email.com",
    "type": "pro",
    "status": "active",
    "hardware_id": "ABC123...",
    "created_at": "2025-01-01T00:00:00Z",
    "expires_at": "2026-01-01T00:00:00Z",
    "last_used": "2025-12-25T10:30:00Z",
    "usage": {
        "requests_today": 150,
        "requests_total": 5000
    }
}
```

#### POST /licenses/{key}/extend

Extend license duration.

**Request:**
```http
POST /api/v1/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX/extend
Content-Type: application/json
Authorization: Bearer <admin_token>

{
    "days": 365
}
```

**Response:**
```json
{
    "success": true,
    "new_expires_at": "2027-01-01T00:00:00Z"
}
```

#### POST /licenses/{key}/revoke

Revoke a license.

**Request:**
```http
POST /api/v1/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX/revoke
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
    "success": true,
    "message": "License revoked"
}
```

#### POST /licenses/{key}/reset-hardware

Reset hardware binding.

**Request:**
```http
POST /api/v1/admin/licenses/DLNK-XXXX-XXXX-XXXX-XXXX/reset-hardware
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
    "success": true,
    "message": "Hardware binding reset"
}
```

### User Management

#### GET /users

List all users.

**Request:**
```http
GET /api/v1/admin/users?status=active&limit=50
Authorization: Bearer <admin_token>
```

#### POST /users/{id}/approve

Approve a pending user.

**Request:**
```http
POST /api/v1/admin/users/1/approve
Content-Type: application/json
Authorization: Bearer <admin_token>

{
    "license_type": "trial",
    "duration_days": 7
}
```

#### POST /users/{id}/suspend

Suspend a user.

**Request:**
```http
POST /api/v1/admin/users/1/suspend
Content-Type: application/json
Authorization: Bearer <admin_token>

{
    "reason": "Violation of terms",
    "duration_days": 30
}
```

### Statistics

#### GET /stats

Get system statistics.

**Request:**
```http
GET /api/v1/admin/stats
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
    "users": {
        "total": 1000,
        "active": 850,
        "pending": 20
    },
    "licenses": {
        "total": 1000,
        "active": 850,
        "expired": 100
    },
    "ai_usage": {
        "requests_today": 15000,
        "requests_this_month": 450000
    }
}
```

---

## ❌ Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_LICENSE` | 401 | License key is invalid |
| `LICENSE_EXPIRED` | 401 | License has expired |
| `LICENSE_REVOKED` | 401 | License has been revoked |
| `HARDWARE_MISMATCH` | 401 | Hardware ID doesn't match |
| `RATE_LIMIT` | 429 | Rate limit exceeded |
| `PROMPT_BLOCKED` | 403 | Prompt blocked by filter |
| `PROVIDER_ERROR` | 502 | AI provider error |
| `INTERNAL_ERROR` | 500 | Internal server error |

---

## 📝 Rate Limits

| License Type | Requests/Minute | Requests/Day |
|--------------|-----------------|--------------|
| Trial | 10 | 100 |
| Standard | 30 | 500 |
| Pro | 60 | 1000 |
| Enterprise | Unlimited | Unlimited |

---

## 🔐 Authentication

### License Token

```javascript
// Get token from license verification
const response = await fetch('/api/v1/verify', {
    method: 'POST',
    body: JSON.stringify({
        license_key: 'DLNK-XXXX-XXXX-XXXX-XXXX',
        hardware_id: getHardwareId()
    })
});
const { token } = await response.json();

// Use token in subsequent requests
const aiResponse = await fetch('/api/v1/chat', {
    headers: {
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ message: 'Hello' })
});
```

### Admin Token

```python
from dlnk_admin import AdminClient

client = AdminClient()
token = client.login(admin_key="your-admin-key", otp="123456")

# Use token
licenses = client.get_licenses(token=token)
```

---

**ก่อนหน้า:** [← Architecture](architecture.md)  
**ถัดไป:** [Extension Development →](extension-dev.md)
