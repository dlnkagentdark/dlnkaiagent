# License & Authentication API

**Version:** 1.0
**Last Updated:** December 25, 2025

## Overview

The License & Authentication service is a backend component responsible for managing user licenses, validating access, and handling user authentication. It is built with FastAPI and uses a local SQLite database for persistence.

- **Base URL:** `http://localhost:8088/api/v1`
- **Database:** `~/.dlnk-ide/dlnk_license.db`

## Authentication

Most endpoints require a valid admin token, which should be passed in the `Authorization` header.

`Authorization: Bearer <ADMIN_TOKEN>`

## Endpoints

### License Management

#### `POST /licenses/create`

Creates a new license key.

**Request Body:**
```json
{
  "user_email": "test@example.com",
  "license_type": "pro", // pro, trial, enterprise
  "duration_days": 365,
  "bind_hardware": true
}
```

**Response:**
```json
{
  "license_key": "DLNK-ABCD-1234-EFGH-5678",
  "user_email": "test@example.com",
  "expires_at": "2026-12-25T12:00:00Z"
}
```

#### `POST /licenses/validate`

Validates a license key and hardware ID.

**Request Body:**
```json
{
  "license_key": "DLNK-ABCD-1234-EFGH-5678",
  "hardware_id": "HWID-XYZ-987"
}
```

**Response (Success):**
```json
{
  "is_valid": true,
  "session_token": "...",
  "expires_at": "2026-12-25T12:00:00Z"
}
```

**Response (Failure):**
```json
{
  "is_valid": false,
  "error": "Invalid license key or hardware ID"
}
```

#### `POST /licenses/revoke`

Revokes an existing license key.

**Request Body:**
```json
{
  "license_key": "DLNK-ABCD-1234-EFGH-5678"
}
```

**Response:**
```json
{
  "status": "revoked",
  "license_key": "DLNK-ABCD-1234-EFGH-5678"
}
```

### User Authentication

#### `POST /auth/register`

Registers a new user. This typically sends a request to an admin for approval.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "name": "New User"
}
```

**Response:**
```json
{
  "status": "pending_approval",
  "message": "Registration request sent to administrator."
}
```

#### `POST /auth/login`

Handles user login. This is primarily for the client-side application to validate its license and get a session token.

**Request Body:**
```json
{
  "license_key": "DLNK-ABCD-1234-EFGH-5678"
}
```

**Response:**
```json
{
  "status": "success",
  "session_token": "...",
  "message": "Login successful. Offline validation is active for 7 days."
}
```

### 2FA (Two-Factor Authentication)

#### `POST /auth/2fa/setup`

Sets up TOTP-based 2FA for an admin account.

**Response:**
```json
{
  "secret_key": "...",
  "qr_code_uri": "otpauth://totp/dLNkAdmin:admin?secret=..."
}
```

#### `POST /auth/2fa/verify`

Verifies a TOTP code.

**Request Body:**
```json
{
  "totp_code": "123456"
}
```

**Response:**
```json
{
  "verified": true
}
```
