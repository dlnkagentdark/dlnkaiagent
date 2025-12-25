"""
Authentication API Routes
API endpoints สำหรับ Authentication
"""

from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import logging

import sys
sys.path.append('../..')
from auth import (
    login_manager, registration_manager, session_manager, totp_manager,
    LoginResult, RegistrationRequest, RegistrationResult,
    is_2fa_available, setup_2fa, verify_2fa
)
from utils.helpers import get_client_ip

logger = logging.getLogger('dLNk-AuthAPI')
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


# ==================== Request/Response Models ====================

class LoginRequest(BaseModel):
    """Request สำหรับ Login"""
    username: str
    password: str
    license_key: Optional[str] = None
    totp_code: Optional[str] = None
    remember: bool = False


class RegisterRequest(BaseModel):
    """Request สำหรับ Registration"""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)
    requested_type: str = "trial"


class ChangePasswordRequest(BaseModel):
    """Request สำหรับเปลี่ยน Password"""
    old_password: str
    new_password: str = Field(min_length=8)


class Setup2FARequest(BaseModel):
    """Request สำหรับตั้งค่า 2FA"""
    verification_code: str = Field(min_length=6, max_length=6)


class Verify2FARequest(BaseModel):
    """Request สำหรับยืนยัน 2FA"""
    code: str = Field(min_length=6, max_length=6)


class AuthResponse(BaseModel):
    """Response สำหรับ Authentication"""
    success: bool
    message: str
    session_id: Optional[str] = None
    user: Optional[dict] = None
    requires_2fa: bool = False
    requires_password_change: bool = False


# ==================== Helper Functions ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[dict]:
    """ดึง user จาก session token"""
    if not credentials:
        return None
    
    session_data = session_manager.validate_session(credentials.credentials)
    return session_data


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Require authentication"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    session_data = session_manager.validate_session(credentials.credentials)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return session_data


# ==================== API Endpoints ====================

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, req: Request):
    """
    Login ด้วย username และ password
    
    - **username**: Username หรือ email
    - **password**: Password
    - **license_key**: License key (optional)
    - **totp_code**: 2FA code (ถ้าเปิดใช้งาน)
    - **remember**: บันทึก credentials สำหรับ offline login
    """
    try:
        ip_address = get_client_ip(req)
        user_agent = req.headers.get('user-agent', '')
        
        result = login_manager.login(
            username=request.username,
            password=request.password,
            license_key=request.license_key,
            totp_code=request.totp_code,
            ip_address=ip_address,
            user_agent=user_agent,
            remember=request.remember
        )
        
        if result.success:
            return AuthResponse(
                success=True,
                message="Login successful",
                session_id=result.session_id,
                user=result.user.to_dict() if result.user else None,
                requires_password_change=result.requires_password_change
            )
        else:
            return AuthResponse(
                success=False,
                message=result.error or "Login failed",
                requires_2fa=result.requires_2fa
            )
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, req: Request):
    """
    ลงทะเบียนผู้ใช้ใหม่
    
    - **username**: Username (3-50 ตัวอักษร)
    - **email**: Email address
    - **password**: Password (อย่างน้อย 8 ตัวอักษร)
    - **requested_type**: ประเภท License ที่ต้องการ (trial, pro, enterprise)
    """
    try:
        from license.hardware import get_hardware_id
        
        reg_request = RegistrationRequest(
            username=request.username,
            email=request.email,
            password=request.password,
            hardware_id=get_hardware_id(),
            requested_type=request.requested_type
        )
        
        result = await registration_manager.register(reg_request)
        
        if result.success:
            response_data = {
                "success": True,
                "message": result.message
            }
            
            if result.user:
                response_data["user"] = result.user.to_dict()
            
            if result.pending_approval:
                response_data["message"] = "Registration pending admin approval"
            
            return AuthResponse(**response_data)
        else:
            return AuthResponse(
                success=False,
                message=result.message
            )
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(session: dict = Depends(require_auth)):
    """
    Logout และยกเลิก session ปัจจุบัน
    """
    try:
        session_manager.invalidate_session(session['session_id'])
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout-all")
async def logout_all(session: dict = Depends(require_auth)):
    """
    Logout จากทุกอุปกรณ์
    """
    try:
        count = session_manager.invalidate_user_sessions(session['user_id'])
        
        return {
            "success": True,
            "message": f"Logged out from {count} sessions"
        }
        
    except Exception as e:
        logger.error(f"Logout all error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def get_current_user_info(session: dict = Depends(require_auth)):
    """
    ดึงข้อมูล user ปัจจุบัน
    """
    return {
        "success": True,
        "user": {
            "user_id": session['user_id'],
            "username": session['username'],
            "offline_mode": session.get('offline_mode', False)
        }
    }


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    session: dict = Depends(require_auth)
):
    """
    เปลี่ยน Password
    """
    try:
        success, message = login_manager.change_password(
            user_id=session['user_id'],
            old_password=request.old_password,
            new_password=request.new_password
        )
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def get_user_sessions(session: dict = Depends(require_auth)):
    """
    ดึงรายการ sessions ของ user
    """
    sessions = session_manager.get_user_sessions(session['user_id'])
    
    return {
        "success": True,
        "count": len(sessions),
        "sessions": sessions
    }


@router.post("/validate-session")
async def validate_session(session: dict = Depends(require_auth)):
    """
    ตรวจสอบ session ปัจจุบัน
    """
    return {
        "success": True,
        "valid": True,
        "session": session
    }


# ==================== 2FA Endpoints ====================

@router.get("/2fa/status")
async def get_2fa_status(session: dict = Depends(require_auth)):
    """
    ตรวจสอบสถานะ 2FA
    """
    return {
        "success": True,
        "available": is_2fa_available(),
        "enabled": False  # TODO: Check from user data
    }


@router.post("/2fa/setup")
async def setup_2fa_endpoint(session: dict = Depends(require_auth)):
    """
    เริ่มตั้งค่า 2FA
    """
    if not is_2fa_available():
        raise HTTPException(status_code=400, detail="2FA is not available")
    
    secret, uri, qr_code = setup_2fa(session['username'])
    
    return {
        "success": True,
        "secret": secret,
        "uri": uri,
        "qr_code": qr_code  # Base64 encoded PNG
    }


@router.post("/2fa/verify")
async def verify_2fa_setup(
    request: Setup2FARequest,
    session: dict = Depends(require_auth)
):
    """
    ยืนยันการตั้งค่า 2FA
    """
    # TODO: Get secret from setup process and verify
    # Then save to user data
    
    return {
        "success": True,
        "message": "2FA setup verified"
    }


@router.post("/2fa/disable")
async def disable_2fa(
    request: Verify2FARequest,
    session: dict = Depends(require_auth)
):
    """
    ปิดใช้งาน 2FA
    """
    # TODO: Verify code and disable 2FA
    
    return {
        "success": True,
        "message": "2FA disabled"
    }


# ==================== Utility Endpoints ====================

@router.get("/check-username/{username}")
async def check_username_available(username: str):
    """
    ตรวจสอบว่า username ว่างหรือไม่
    """
    available = await registration_manager.check_username_available(username)
    
    return {
        "success": True,
        "available": available
    }
