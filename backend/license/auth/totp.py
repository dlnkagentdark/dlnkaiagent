"""
TOTP 2FA Authentication
ระบบยืนยันตัวตนแบบ 2 ขั้นตอน (Two-Factor Authentication)
"""

import base64
import io
from typing import Optional, Tuple
import logging

# Try to import pyotp
try:
    import pyotp
    TOTP_AVAILABLE = True
except ImportError:
    TOTP_AVAILABLE = False

# Try to import qrcode for QR generation
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

import sys
sys.path.append('..')
from config import get_config

logger = logging.getLogger('dLNk-TOTP')
config = get_config()


class TOTPManager:
    """
    จัดการ TOTP (Time-based One-Time Password) สำหรับ 2FA
    """
    
    def __init__(self):
        self.issuer = config.TOTP_ISSUER
        self._check_availability()
    
    def _check_availability(self):
        """ตรวจสอบว่า pyotp พร้อมใช้งานหรือไม่"""
        if not TOTP_AVAILABLE:
            logger.warning("pyotp not installed. 2FA will not be available.")
    
    @property
    def is_available(self) -> bool:
        """ตรวจสอบว่า TOTP พร้อมใช้งานหรือไม่"""
        return TOTP_AVAILABLE
    
    def generate_secret(self) -> str:
        """
        สร้าง secret key ใหม่สำหรับ TOTP
        
        Returns:
            Base32 encoded secret
        """
        if not TOTP_AVAILABLE:
            raise RuntimeError("pyotp is not installed")
        
        return pyotp.random_base32()
    
    def get_totp_uri(self, secret: str, username: str) -> str:
        """
        สร้าง TOTP URI สำหรับ QR Code
        
        Args:
            secret: TOTP secret
            username: Username
        
        Returns:
            otpauth:// URI
        """
        if not TOTP_AVAILABLE:
            raise RuntimeError("pyotp is not installed")
        
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=username, issuer_name=self.issuer)
    
    def generate_qr_code(self, secret: str, username: str) -> Optional[str]:
        """
        สร้าง QR Code เป็น base64 image
        
        Args:
            secret: TOTP secret
            username: Username
        
        Returns:
            Base64 encoded PNG image หรือ None ถ้าไม่สามารถสร้างได้
        """
        if not TOTP_AVAILABLE:
            return None
        
        if not QRCODE_AVAILABLE:
            logger.warning("qrcode library not installed. Cannot generate QR code.")
            return None
        
        try:
            uri = self.get_totp_uri(secret, username)
            
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return None
    
    def verify_code(self, secret: str, code: str) -> bool:
        """
        ตรวจสอบ TOTP code
        
        Args:
            secret: TOTP secret
            code: 6-digit code จาก authenticator app
        
        Returns:
            True ถ้า code ถูกต้อง
        """
        if not TOTP_AVAILABLE:
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)  # Allow 1 window tolerance
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    def get_current_code(self, secret: str) -> str:
        """
        ดึง TOTP code ปัจจุบัน (สำหรับ testing)
        
        Args:
            secret: TOTP secret
        
        Returns:
            Current 6-digit code
        """
        if not TOTP_AVAILABLE:
            raise RuntimeError("pyotp is not installed")
        
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def setup_2fa(self, username: str) -> Tuple[str, str, Optional[str]]:
        """
        ตั้งค่า 2FA สำหรับ user
        
        Args:
            username: Username
        
        Returns:
            Tuple of (secret, uri, qr_code_base64)
        """
        secret = self.generate_secret()
        uri = self.get_totp_uri(secret, username)
        qr_code = self.generate_qr_code(secret, username)
        
        return secret, uri, qr_code
    
    def validate_setup(self, secret: str, code: str) -> bool:
        """
        ตรวจสอบว่า user ตั้งค่า 2FA ถูกต้อง
        
        Args:
            secret: TOTP secret ที่สร้างไว้
            code: Code จาก authenticator app
        
        Returns:
            True ถ้าตั้งค่าถูกต้อง
        """
        return self.verify_code(secret, code)


# Global instance
totp_manager = TOTPManager()


def is_2fa_available() -> bool:
    """Check if 2FA is available"""
    return totp_manager.is_available


def setup_2fa(username: str) -> Tuple[str, str, Optional[str]]:
    """Setup 2FA for user"""
    return totp_manager.setup_2fa(username)


def verify_2fa(secret: str, code: str) -> bool:
    """Verify 2FA code"""
    return totp_manager.verify_code(secret, code)
