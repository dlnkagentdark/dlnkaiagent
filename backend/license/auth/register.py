"""
Registration System
ระบบลงทะเบียนผู้ใช้ เชื่อมต่อกับ Admin
"""

import aiohttp
import asyncio
from dataclasses import dataclass
from typing import Optional
import logging

import sys
sys.path.append('..')
from config import get_config
from license.hardware import get_hardware_id
from .login import login_manager, User

logger = logging.getLogger('dLNk-Register')
config = get_config()


@dataclass
class RegistrationRequest:
    """ข้อมูลการลงทะเบียน"""
    username: str
    email: str
    password: str
    hardware_id: str = ""
    requested_type: str = "trial"
    
    def __post_init__(self):
        if not self.hardware_id:
            self.hardware_id = get_hardware_id()


@dataclass
class RegistrationResult:
    """ผลลัพธ์การลงทะเบียน"""
    success: bool
    message: str
    user: Optional[User] = None
    license_key: Optional[str] = None
    pending_approval: bool = False


class RegistrationManager:
    """
    จัดการการลงทะเบียนผู้ใช้
    รองรับทั้ง Local และ Remote Registration
    """
    
    def __init__(self, admin_api_url: str = None):
        self.admin_api_url = admin_api_url or config.ADMIN_API_URL
    
    async def register_remote(self, request: RegistrationRequest) -> RegistrationResult:
        """
        ลงทะเบียนผ่าน Admin API
        
        Args:
            request: ข้อมูลการลงทะเบียน
        
        Returns:
            RegistrationResult
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.admin_api_url}/api/register",
                    json={
                        'username': request.username,
                        'email': request.email,
                        'hardware_id': request.hardware_id,
                        'requested_type': request.requested_type
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        # Registration approved immediately
                        license_key = data.get('license_key')
                        
                        # Create local user
                        success, msg, user = login_manager.create_user(
                            username=request.username,
                            password=request.password,
                            email=request.email,
                            license_key=license_key
                        )
                        
                        if success:
                            return RegistrationResult(
                                success=True,
                                message="Registration successful",
                                user=user,
                                license_key=license_key
                            )
                        else:
                            return RegistrationResult(
                                success=False,
                                message=f"Local user creation failed: {msg}"
                            )
                    
                    elif response.status == 202:
                        # Registration pending approval
                        return RegistrationResult(
                            success=True,
                            message="Registration pending admin approval",
                            pending_approval=True
                        )
                    
                    else:
                        return RegistrationResult(
                            success=False,
                            message=data.get('error', 'Registration failed')
                        )
                        
        except aiohttp.ClientError as e:
            logger.error(f"Connection error during registration: {e}")
            return RegistrationResult(
                success=False,
                message=f"Connection error: {str(e)}"
            )
        except asyncio.TimeoutError:
            return RegistrationResult(
                success=False,
                message="Registration request timed out"
            )
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return RegistrationResult(
                success=False,
                message=f"Registration error: {str(e)}"
            )
    
    def register_local(self, request: RegistrationRequest) -> RegistrationResult:
        """
        ลงทะเบียนแบบ Local (ไม่ต้องเชื่อมต่อ Admin)
        
        Args:
            request: ข้อมูลการลงทะเบียน
        
        Returns:
            RegistrationResult
        """
        
        # Validate email
        from utils.helpers import validate_email
        if request.email and not validate_email(request.email):
            return RegistrationResult(
                success=False,
                message="Invalid email format"
            )
        
        # Create user
        success, msg, user = login_manager.create_user(
            username=request.username,
            password=request.password,
            email=request.email
        )
        
        if success:
            logger.info(f"Local registration successful: {request.username}")
            return RegistrationResult(
                success=True,
                message="Registration successful. Please contact admin for license.",
                user=user
            )
        else:
            return RegistrationResult(
                success=False,
                message=msg
            )
    
    async def register(self, request: RegistrationRequest) -> RegistrationResult:
        """
        ลงทะเบียน (พยายาม remote ก่อน, fallback เป็น local)
        
        Args:
            request: ข้อมูลการลงทะเบียน
        
        Returns:
            RegistrationResult
        """
        
        # Try remote registration first
        try:
            result = await self.register_remote(request)
            if result.success:
                return result
        except Exception as e:
            logger.warning(f"Remote registration failed: {e}")
        
        # Fallback to local registration
        return self.register_local(request)
    
    def register_sync(self, request: RegistrationRequest) -> RegistrationResult:
        """
        Synchronous wrapper for register
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.register(request))
    
    async def check_username_available(self, username: str) -> bool:
        """ตรวจสอบว่า username ว่างหรือไม่"""
        
        # Check local
        import sqlite3
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
        exists = cursor.fetchone() is not None
        conn.close()
        
        if exists:
            return False
        
        # Check remote
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.admin_api_url}/api/check-username/{username}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('available', False)
        except Exception:
            pass
        
        return True
    
    async def request_trial(self, request: RegistrationRequest) -> RegistrationResult:
        """
        ขอ Trial License
        
        Args:
            request: ข้อมูลการลงทะเบียน
        
        Returns:
            RegistrationResult
        """
        request.requested_type = "trial"
        return await self.register(request)


# Global instance
registration_manager = RegistrationManager()


def register_user(
    username: str,
    email: str,
    password: str,
    requested_type: str = "trial"
) -> RegistrationResult:
    """
    Shortcut function for registration
    """
    request = RegistrationRequest(
        username=username,
        email=email,
        password=password,
        requested_type=requested_type
    )
    return registration_manager.register_sync(request)


async def register_user_async(
    username: str,
    email: str,
    password: str,
    requested_type: str = "trial"
) -> RegistrationResult:
    """
    Async shortcut function for registration
    """
    request = RegistrationRequest(
        username=username,
        email=email,
        password=password,
        requested_type=requested_type
    )
    return await registration_manager.register(request)
