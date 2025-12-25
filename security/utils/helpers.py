#!/usr/bin/env python3
"""
Security Utilities
ฟังก์ชันช่วยเหลือสำหรับระบบ Security
"""

import os
import re
import hashlib
import secrets
import socket
import platform
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger('SecurityUtils')


# ===== HASH FUNCTIONS =====

def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Hash a string
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (sha256, sha512, md5)
    
    Returns:
        Hex digest
    """
    if algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    elif algorithm == 'sha512':
        return hashlib.sha512(text.encode()).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def hash_file(file_path: str, algorithm: str = 'sha256') -> str:
    """
    Hash a file
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm
    
    Returns:
        Hex digest
    """
    hasher = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def generate_token(length: int = 32) -> str:
    """Generate secure random token"""
    return secrets.token_hex(length // 2)


def generate_password(length: int = 16, include_special: bool = True) -> str:
    """Generate secure random password"""
    import string
    
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += "!@#$%^&*"
    
    return ''.join(secrets.choice(chars) for _ in range(length))


# ===== HWID FUNCTIONS =====

def get_hwid() -> str:
    """
    Get Hardware ID (unique machine identifier)
    
    Returns:
        HWID hash
    """
    components = []
    
    # Platform info
    components.append(platform.node())
    components.append(platform.machine())
    components.append(platform.processor())
    
    # Try to get MAC address
    try:
        import uuid
        mac = uuid.getnode()
        components.append(str(mac))
    except:
        pass
    
    # Try to get disk serial (Linux)
    try:
        if platform.system() == 'Linux':
            with open('/etc/machine-id', 'r') as f:
                components.append(f.read().strip())
    except:
        pass
    
    # Hash all components
    combined = '|'.join(components)
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


def get_machine_info() -> Dict[str, str]:
    """Get machine information"""
    return {
        'hostname': socket.gethostname(),
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
    }


# ===== IP FUNCTIONS =====

def get_local_ip() -> str:
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def is_private_ip(ip: str) -> bool:
    """Check if IP is private"""
    import ipaddress
    try:
        return ipaddress.ip_address(ip).is_private
    except:
        return False


def mask_ip(ip: str) -> str:
    """Mask IP address for privacy"""
    parts = ip.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.xxx.xxx"
    return "xxx.xxx.xxx.xxx"


# ===== SANITIZATION =====

def sanitize_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Truncate
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    return text.strip()


def sanitize_filename(filename: str) -> str:
    """Sanitize filename"""
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename or 'unnamed'


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


# ===== VALIDATION =====

def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_license_key(key: str) -> bool:
    """Validate license key format"""
    # Format: XXXX-XXXX-XXXX-XXXX
    pattern = r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    return bool(re.match(pattern, key.upper()))


def is_valid_hwid(hwid: str) -> bool:
    """Validate HWID format"""
    # 32 character hex string
    pattern = r'^[a-f0-9]{32}$'
    return bool(re.match(pattern, hwid.lower()))


# ===== TIMING =====

def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare strings in constant time (prevent timing attacks)
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    
    return result == 0


# ===== FILE OPERATIONS =====

def secure_delete(file_path: str, passes: int = 3):
    """
    Securely delete a file by overwriting
    
    Args:
        file_path: Path to file
        passes: Number of overwrite passes
    """
    path = Path(file_path)
    if not path.exists():
        return
    
    size = path.stat().st_size
    
    with open(file_path, 'wb') as f:
        for _ in range(passes):
            f.seek(0)
            f.write(secrets.token_bytes(size))
            f.flush()
            os.fsync(f.fileno())
    
    os.remove(file_path)
    logger.info(f"Securely deleted: {file_path}")


def set_secure_permissions(file_path: str, mode: int = 0o600):
    """Set secure file permissions"""
    os.chmod(file_path, mode)


# ===== LOGGING =====

def mask_sensitive_data(data: Dict[str, Any], sensitive_keys: List[str] = None) -> Dict[str, Any]:
    """
    Mask sensitive data in dictionary
    
    Args:
        data: Dictionary to mask
        sensitive_keys: Keys to mask
    
    Returns:
        Masked dictionary
    """
    if sensitive_keys is None:
        sensitive_keys = ['password', 'token', 'api_key', 'secret', 'credential', 'key']
    
    result = {}
    
    for key, value in data.items():
        if any(sk in key.lower() for sk in sensitive_keys):
            if isinstance(value, str) and len(value) > 4:
                result[key] = value[:2] + '*' * (len(value) - 4) + value[-2:]
            else:
                result[key] = '***'
        elif isinstance(value, dict):
            result[key] = mask_sensitive_data(value, sensitive_keys)
        else:
            result[key] = value
    
    return result


def format_timestamp(dt: datetime = None) -> str:
    """Format timestamp for logging"""
    dt = dt or datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


# ===== RATE LIMITING HELPERS =====

class SimpleRateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        import time
        
        now = time.time()
        cutoff = now - self.window_seconds
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]
        
        if len(self.requests[key]) >= self.max_requests:
            return False
        
        self.requests[key].append(now)
        return True
    
    def reset(self, key: str):
        """Reset rate limit for key"""
        self.requests.pop(key, None)
