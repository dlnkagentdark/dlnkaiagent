# Admin API

**Version:** 1.0
**Last Updated:** December 25, 2025

## Overview

The Admin API provides a set of endpoints for managing the dLNk IDE ecosystem. It is used by the Admin Console (TUI) and the Telegram Bot to perform administrative tasks such as managing users, licenses, and viewing system logs.

- **Base URL:** `http://localhost:8088/api/v1/admin`
- **Authentication:** Requires a valid Admin Token.

## Endpoints

All endpoints are prefixed with `/admin`.

### Dashboard & Stats

#### `GET /stats`

Retrieves overall system statistics for the dashboard.

**Response:**
```json
{
  "total_users": 1234,
  "active_users_7d": 456,
  "total_licenses": 987,
  "expiring_soon_30d": 45,
  "ai_requests_24h": 12345,
  "system_status": {
    "ai_bridge": "online",
    "license_server": "online"
  }
}
```

### User Management

#### `GET /users`

Lists all users with pagination.

**Query Parameters:**
- `page`: integer (default: 1)
- `per_page`: integer (default: 20)

**Response:**
```json
{
  "users": [
    {
      "user_id": "user123",
      "email": "user@example.com",
      "license_key": "DLNK-XXXX-YYYY-ZZZZ",
      "created_at": "2025-10-01T10:00:00Z"
    }
  ],
  "total_pages": 10,
  "current_page": 1
}
```

#### `POST /users/ban`

Bans a user, preventing them from using the IDE.

**Request Body:**
```json
{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "User user123 has been banned."
}
```

### License Management

This is handled by the main `/licenses` endpoints but can be accessed with admin privileges.

### Log Viewer

#### `GET /logs`

Retrieves recent system logs.

**Query Parameters:**
- `level`: string (e.g., `INFO`, `WARNING`, `ERROR`)
- `limit`: integer (default: 100)

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2025-12-25T18:00:00Z",
      "level": "ERROR",
      "message": "Failed to connect to AI provider: Connection timed out."
    },
    {
      "timestamp": "2025-12-25T17:55:00Z",
      "level": "INFO",
      "message": "User user123 logged in successfully."
    }
  ]
}
```

### Security

#### `GET /security/alerts`

Retrieves security alerts, such as blocked prompts or detected anomalies.

**Response:**
```json
{
  "alerts": [
    {
      "alert_id": "alert-abc-123",
      "type": "prompt_filter_blocked",
      "severity": "high",
      "details": "Blocked prompt containing malicious pattern.",
      "user_id": "user456",
      "timestamp": "2025-12-25T16:30:00Z"
    }
  ]
}
```
