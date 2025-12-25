"""
dLNk IDE - Authentication API Routes
API endpoints สำหรับระบบยืนยันตัวตน

Endpoints:
- POST /api/auth/login - Login with license_key and hwid
- POST /api/auth/register - Register new user
- GET /api/auth/verify - Verify JWT token
- POST /api/auth/refresh - Refresh JWT token
- POST /api/auth/logout - Logout and invalidate token
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import hashlib
import secrets
import logging

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'license'))

from fastapi import APIRouter, HTTPException, Request, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
import jwt

logger = logging.getLogger('dLNk-AuthAPI')
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


# ==================== Configuration ====================

class AuthConfig:
    """Authentication Configuration"""
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dlnk-ide-secret-key-change-in-production')
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_HOURS: int = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    REFRESH_TOKEN_DAYS: int = int(os.getenv('REFRESH_TOKEN_DAYS', '30'))
    
    # Admin notification settings
    ADMIN_EMAIL: str = os.getenv('ADMIN_EMAIL', 'admin@dlnk-ide.com')
    ADMIN_TELEGRAM_CHAT_ID: str = os.getenv('ADMIN_TELEGRAM_CHAT_ID', '')
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')


auth_config = AuthConfig()


# ==================== Request/Response Models ====================

class LoginRequest(BaseModel):
    """Request model สำหรับ Login"""
    license_key: str = Field(..., description="License key for authentication")
    hwid: str = Field(..., description="Hardware ID of the client machine")
    device_name: Optional[str] = Field(None, description="Optional device name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
                "hwid": "ABC123DEF456",
                "device_name": "My Development PC"
            }
        }


class LoginResponse(BaseModel):
    """Response model สำหรับ Login"""
    success: bool
    message: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 0
    user: Optional[dict] = None
    license_info: Optional[dict] = None


class RegisterRequest(BaseModel):
    """Request model สำหรับ Registration"""
    email: EmailStr = Field(..., description="Email address")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    company: Optional[str] = Field(None, description="Company name")
    phone: Optional[str] = Field(None, description="Phone number")
    requested_license_type: str = Field(default="trial", description="Requested license type")
    message: Optional[str] = Field(None, description="Additional message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "company": "Example Corp",
                "requested_license_type": "pro"
            }
        }


class RegisterResponse(BaseModel):
    """Response model สำหรับ Registration"""
    success: bool
    message: str
    registration_id: Optional[str] = None
    estimated_response_time: Optional[str] = None


class TokenVerifyResponse(BaseModel):
    """Response model สำหรับ Token Verification"""
    valid: bool
    message: str
    user_id: Optional[str] = None
    license_key: Optional[str] = None
    expires_at: Optional[str] = None
    remaining_seconds: int = 0


class RefreshTokenRequest(BaseModel):
    """Request model สำหรับ Refresh Token"""
    refresh_token: str = Field(..., description="Refresh token")


# ==================== JWT Helper Functions ====================

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=auth_config.JWT_EXPIRATION_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        auth_config.SECRET_KEY,
        algorithm=auth_config.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=auth_config.REFRESH_TOKEN_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        auth_config.SECRET_KEY,
        algorithm=auth_config.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            auth_config.SECRET_KEY,
            algorithms=[auth_config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ==================== License Validation Helper ====================

def validate_license_key(license_key: str, hwid: str) -> tuple[bool, dict]:
    """
    Validate license key and hardware ID
    
    Returns:
        Tuple of (is_valid, license_info)
    """
    try:
        # Try to import from license module
        try:
            from license.license.validator import LicenseValidator
            from license.license.storage import LicenseStorage
            
            validator = LicenseValidator()
            storage = LicenseStorage()
            
            # Get license data
            license_data = storage.get_license(license_key)
            if not license_data:
                return False, {"error": "License not found"}
            
            # Validate license
            result = validator.validate(license_key, hwid)
            
            if result.valid:
                return True, {
                    "license_type": result.license_data.license_type if result.license_data else "unknown",
                    "features": result.features or [],
                    "days_remaining": result.days_remaining,
                    "max_devices": license_data.get('max_devices', 1),
                    "owner_name": license_data.get('owner_name', ''),
                    "expires_at": license_data.get('expires_at', '')
                }
            else:
                return False, {"error": result.error or "Invalid license"}
                
        except ImportError:
            # Fallback: Simple validation for testing
            logger.warning("License module not available, using simple validation")
            
            # Simple validation logic
            if license_key.startswith("DLNK-") and len(license_key) >= 20:
                return True, {
                    "license_type": "pro",
                    "features": ["code_completion", "ai_assistant", "debugging"],
                    "days_remaining": 365,
                    "max_devices": 3
                }
            
            return False, {"error": "Invalid license format"}
            
    except Exception as e:
        logger.error(f"License validation error: {e}")
        return False, {"error": str(e)}


# ==================== Admin Notification Helper ====================

async def notify_admin_registration(registration_data: dict):
    """Send notification to admin about new registration"""
    try:
        # Log the registration
        logger.info(f"New registration request: {registration_data}")
        
        # Try to send Telegram notification
        if auth_config.TELEGRAM_BOT_TOKEN and auth_config.ADMIN_TELEGRAM_CHAT_ID:
            try:
                import httpx
                
                message = f"""
🆕 **New Registration Request**

📧 Email: {registration_data.get('email')}
👤 Name: {registration_data.get('name')}
🏢 Company: {registration_data.get('company', 'N/A')}
📱 Phone: {registration_data.get('phone', 'N/A')}
📋 License Type: {registration_data.get('requested_license_type')}
💬 Message: {registration_data.get('message', 'N/A')}
🕐 Time: {datetime.now().isoformat()}
                """
                
                async with httpx.AsyncClient() as client:
                    await client.post(
                        f"https://api.telegram.org/bot{auth_config.TELEGRAM_BOT_TOKEN}/sendMessage",
                        json={
                            "chat_id": auth_config.ADMIN_TELEGRAM_CHAT_ID,
                            "text": message,
                            "parse_mode": "Markdown"
                        }
                    )
                    
                logger.info("Admin notification sent via Telegram")
                
            except Exception as e:
                logger.warning(f"Failed to send Telegram notification: {e}")
        
        # Store registration in file for later processing
        registrations_dir = Path(__file__).parent.parent.parent / 'data' / 'registrations'
        registrations_dir.mkdir(parents=True, exist_ok=True)
        
        registration_id = secrets.token_hex(8)
        registration_file = registrations_dir / f"{registration_id}.json"
        
        import json
        with open(registration_file, 'w') as f:
            json.dump({
                **registration_data,
                "registration_id": registration_id,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }, f, indent=2)
        
        return registration_id
        
    except Exception as e:
        logger.error(f"Failed to process registration notification: {e}")
        return None


# ==================== Dependency Functions ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """Get current user from JWT token"""
    if not credentials:
        return None
    
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    
    return payload


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Require valid authentication"""
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


# ==================== API Endpoints ====================

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request):
    """
    Login with license key and hardware ID
    
    - **license_key**: Valid dLNk IDE license key
    - **hwid**: Hardware ID of the client machine
    - **device_name**: Optional name for this device
    
    Returns JWT access token and refresh token on success.
    """
    try:
        client_ip = get_client_ip(req)
        user_agent = req.headers.get('user-agent', '')
        
        logger.info(f"Login attempt from {client_ip} with license: {request.license_key[:10]}...")
        
        # Validate license
        is_valid, license_info = validate_license_key(request.license_key, request.hwid)
        
        if not is_valid:
            logger.warning(f"Login failed for {client_ip}: {license_info.get('error')}")
            return LoginResponse(
                success=False,
                message=license_info.get('error', 'Invalid license or hardware ID')
            )
        
        # Create user data for token
        user_data = {
            "license_key": request.license_key,
            "hwid": request.hwid,
            "device_name": request.device_name,
            "ip_address": client_ip,
            "user_agent": user_agent,
            "license_type": license_info.get('license_type', 'unknown')
        }
        
        # Generate tokens
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token({"license_key": request.license_key, "hwid": request.hwid})
        
        logger.info(f"Login successful for license: {request.license_key[:10]}...")
        
        return LoginResponse(
            success=True,
            message="Login successful",
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=auth_config.JWT_EXPIRATION_HOURS * 3600,
            user={
                "license_key": request.license_key,
                "hwid": request.hwid,
                "device_name": request.device_name,
                "license_type": license_info.get('license_type')
            },
            license_info=license_info
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, req: Request):
    """
    Register new user - sends notification to admin
    
    - **email**: Email address for contact
    - **name**: Full name
    - **company**: Company name (optional)
    - **phone**: Phone number (optional)
    - **requested_license_type**: Type of license requested (trial, pro, enterprise)
    - **message**: Additional message (optional)
    
    Registration requests are reviewed by admin before license is issued.
    """
    try:
        client_ip = get_client_ip(req)
        
        logger.info(f"Registration request from {client_ip}: {request.email}")
        
        # Prepare registration data
        registration_data = {
            "email": request.email,
            "name": request.name,
            "company": request.company,
            "phone": request.phone,
            "requested_license_type": request.requested_license_type,
            "message": request.message,
            "ip_address": client_ip,
            "user_agent": req.headers.get('user-agent', '')
        }
        
        # Notify admin and store registration
        registration_id = await notify_admin_registration(registration_data)
        
        if registration_id:
            return RegisterResponse(
                success=True,
                message="Registration request submitted successfully. Admin will review and contact you.",
                registration_id=registration_id,
                estimated_response_time="1-2 business days"
            )
        else:
            return RegisterResponse(
                success=True,
                message="Registration request received. Admin will contact you soon.",
                estimated_response_time="1-2 business days"
            )
        
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token(user: dict = Depends(require_auth)):
    """
    Verify JWT token validity
    
    Requires Bearer token in Authorization header.
    Returns token validity status and remaining time.
    """
    try:
        exp_timestamp = user.get('exp', 0)
        expires_at = datetime.fromtimestamp(exp_timestamp)
        remaining = max(0, int((expires_at - datetime.utcnow()).total_seconds()))
        
        return TokenVerifyResponse(
            valid=True,
            message="Token is valid",
            user_id=user.get('license_key'),
            license_key=user.get('license_key'),
            expires_at=expires_at.isoformat(),
            remaining_seconds=remaining
        )
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh JWT access token using refresh token
    
    - **refresh_token**: Valid refresh token from login
    
    Returns new access token and refresh token.
    """
    try:
        # Decode refresh token
        payload = decode_token(request.refresh_token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Validate license again
        license_key = payload.get('license_key')
        hwid = payload.get('hwid')
        
        is_valid, license_info = validate_license_key(license_key, hwid)
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="License no longer valid")
        
        # Create new tokens
        user_data = {
            "license_key": license_key,
            "hwid": hwid,
            "license_type": license_info.get('license_type', 'unknown')
        }
        
        new_access_token = create_access_token(user_data)
        new_refresh_token = create_refresh_token({"license_key": license_key, "hwid": hwid})
        
        return LoginResponse(
            success=True,
            message="Token refreshed successfully",
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=auth_config.JWT_EXPIRATION_HOURS * 3600,
            license_info=license_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(user: dict = Depends(require_auth)):
    """
    Logout and invalidate current token
    
    Note: JWT tokens cannot be truly invalidated server-side without a blacklist.
    Client should discard the token.
    """
    try:
        logger.info(f"Logout for license: {user.get('license_key', 'unknown')[:10]}...")
        
        return {
            "success": True,
            "message": "Logged out successfully. Please discard your tokens."
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user_info(user: dict = Depends(require_auth)):
    """
    Get current authenticated user information
    """
    return {
        "success": True,
        "user": {
            "license_key": user.get('license_key'),
            "hwid": user.get('hwid'),
            "device_name": user.get('device_name'),
            "license_type": user.get('license_type'),
            "ip_address": user.get('ip_address')
        }
    }


@router.get("/status")
async def auth_status():
    """
    Get authentication service status
    """
    return {
        "success": True,
        "service": "dLNk-Auth",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "jwt_expiration_hours": auth_config.JWT_EXPIRATION_HOURS,
        "refresh_token_days": auth_config.REFRESH_TOKEN_DAYS
    }
