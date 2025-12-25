"""
dLNk AI Bridge - Helper Utilities
=================================
Common utility functions for the AI Bridge system.

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import json
import uuid
import time
import hashlib
from datetime import datetime
from typing import Any, Optional, Dict


def generate_uuid() -> str:
    """Generate a unique UUID string"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short unique ID"""
    return uuid.uuid4().hex[:length]


def timestamp_now() -> float:
    """Get current timestamp"""
    return time.time()


def timestamp_iso() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON string
    
    Args:
        data: JSON string to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any, default: str = "{}") -> str:
    """
    Safely serialize to JSON string
    
    Args:
        data: Data to serialize
        default: Default value if serialization fails
    
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default


def hash_string(text: str, algorithm: str = 'sha256') -> str:
    """
    Hash a string using specified algorithm
    
    Args:
        text: String to hash
        algorithm: Hash algorithm (md5, sha1, sha256, etc.)
    
    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(text.encode('utf-8'))
    return hasher.hexdigest()


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_bytes(size: int) -> str:
    """
    Format bytes to human readable string
    
    Args:
        size: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration to human readable string
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "2h 30m 15s")
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    
    parts = []
    
    hours = int(seconds // 3600)
    if hours:
        parts.append(f"{hours}h")
        seconds %= 3600
    
    minutes = int(seconds // 60)
    if minutes:
        parts.append(f"{minutes}m")
        seconds %= 60
    
    if seconds or not parts:
        parts.append(f"{seconds:.1f}s")
    
    return ' '.join(parts)


def merge_dicts(base: Dict, override: Dict) -> Dict:
    """
    Deep merge two dictionaries
    
    Args:
        base: Base dictionary
        override: Dictionary to merge (takes precedence)
    
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def extract_error_message(error: Exception) -> str:
    """
    Extract clean error message from exception
    
    Args:
        error: Exception instance
    
    Returns:
        Error message string
    """
    error_str = str(error)
    
    # Clean up common error prefixes
    prefixes_to_remove = [
        'Error: ',
        'Exception: ',
        'RuntimeError: ',
        'ValueError: ',
    ]
    
    for prefix in prefixes_to_remove:
        if error_str.startswith(prefix):
            error_str = error_str[len(prefix):]
            break
    
    return error_str


class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize rate limiter
        
        Args:
            rate: Tokens per second
            capacity: Maximum tokens (burst capacity)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
    
    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens
        
        Args:
            tokens: Number of tokens to acquire
        
        Returns:
            True if tokens acquired, False otherwise
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        
        # Add tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        
        return False
    
    def wait_time(self, tokens: int = 1) -> float:
        """
        Get wait time needed to acquire tokens
        
        Args:
            tokens: Number of tokens needed
        
        Returns:
            Wait time in seconds
        """
        if self.tokens >= tokens:
            return 0
        
        return (tokens - self.tokens) / self.rate
