"""
Helper Utilities
ฟังก์ชันช่วยเหลือทั่วไป
"""

import re
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List


def generate_token(length: int = 32) -> str:
    """สร้าง random token"""
    return secrets.token_urlsafe(length)


def generate_hex_token(length: int = 16) -> str:
    """สร้าง hex token"""
    return secrets.token_hex(length)


def hash_password(password: str, salt: str) -> str:
    """Hash password ด้วย PBKDF2"""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000
    ).hex()


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """ตรวจสอบ password"""
    return hash_password(password, salt) == password_hash


def validate_password(password: str, min_length: int = 8, require_special: bool = True) -> tuple[bool, str]:
    """
    ตรวจสอบความแข็งแรงของ password
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if require_special:
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"


def validate_email(email: str) -> bool:
    """ตรวจสอบรูปแบบ email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_datetime(dt: datetime) -> str:
    """Format datetime เป็น ISO format"""
    return dt.isoformat()


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse datetime จาก string"""
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return None


def is_expired(expires_at: str) -> bool:
    """ตรวจสอบว่าหมดอายุหรือยัง"""
    expiry = parse_datetime(expires_at)
    if expiry is None:
        return True
    return datetime.now() > expiry


def days_until_expiry(expires_at: str) -> int:
    """คำนวณจำนวนวันก่อนหมดอายุ"""
    expiry = parse_datetime(expires_at)
    if expiry is None:
        return 0
    delta = expiry - datetime.now()
    return max(0, delta.days)


def add_days(dt: datetime, days: int) -> datetime:
    """เพิ่มจำนวนวันให้ datetime"""
    return dt + timedelta(days=days)


def get_client_ip(request) -> str:
    """ดึง IP address จาก request"""
    # Check for forwarded headers
    if hasattr(request, 'headers'):
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
    
    # Fallback to remote address
    if hasattr(request, 'remote_addr'):
        return request.remote_addr
    if hasattr(request, 'client'):
        return request.client.host
    
    return '127.0.0.1'


def mask_license_key(key: str) -> str:
    """ซ่อนส่วนของ license key"""
    if len(key) <= 10:
        return key[:4] + '****'
    return key[:8] + '****' + key[-4:]


def sanitize_string(s: str, max_length: int = 255) -> str:
    """ทำความสะอาด string"""
    if not s:
        return ''
    # Remove control characters
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)
    # Truncate
    return s[:max_length].strip()


def generate_license_key_format(prefix: str = "DLNK") -> str:
    """
    สร้าง License Key ในรูปแบบ DLNK-XXXX-XXXX-XXXX-XXXX
    """
    segments = [secrets.token_hex(2).upper() for _ in range(4)]
    return f"{prefix}-{'-'.join(segments)}"


def validate_license_key_format(key: str, prefix: str = "DLNK") -> bool:
    """ตรวจสอบรูปแบบ License Key"""
    pattern = rf'^{prefix}-[A-F0-9]{{4}}-[A-F0-9]{{4}}-[A-F0-9]{{4}}-[A-F0-9]{{4}}$'
    return bool(re.match(pattern, key, re.IGNORECASE))
