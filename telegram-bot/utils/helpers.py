"""
dLNk Telegram Bot - Helper Functions

This module contains utility functions used throughout the bot.
"""

import re
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Tuple
from html import escape


def format_number(num: int) -> str:
    """
    Format a number with thousand separators.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string (e.g., "1,234,567")
    """
    return f"{num:,}"


def format_datetime(
    dt: datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format a datetime object.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def format_relative_time(dt: datetime) -> str:
    """
    Format datetime as relative time (e.g., "2 hours ago").
    
    Args:
        dt: Datetime object
        
    Returns:
        Relative time string
    """
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text
    """
    return escape(text)


def generate_license_key(prefix: str = "DLNK") -> str:
    """
    Generate a random license key.
    
    Args:
        prefix: Key prefix
        
    Returns:
        License key (e.g., "DLNK-ABCD-1234-WXYZ")
    """
    chars = string.ascii_uppercase + string.digits
    parts = [prefix]
    
    for _ in range(3):
        part = ''.join(random.choices(chars, k=4))
        parts.append(part)
    
    return '-'.join(parts)


def validate_license_key(key: str) -> bool:
    """
    Validate license key format.
    
    Args:
        key: License key to validate
        
    Returns:
        True if valid format
    """
    # Format: DLNK-XXXX-XXXX-XXXX
    pattern = r'^DLNK-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
    return bool(re.match(pattern, key))


def parse_duration(duration_str: str) -> Optional[timedelta]:
    """
    Parse duration string to timedelta.
    
    Args:
        duration_str: Duration string (e.g., "30d", "2h", "15m")
        
    Returns:
        timedelta object or None if invalid
    """
    pattern = r'^(\d+)([dhms])$'
    match = re.match(pattern, duration_str.lower())
    
    if not match:
        return None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    units = {
        'd': timedelta(days=value),
        'h': timedelta(hours=value),
        'm': timedelta(minutes=value),
        's': timedelta(seconds=value)
    }
    
    return units.get(unit)


def get_severity_emoji(severity: int) -> str:
    """
    Get emoji for severity level.
    
    Args:
        severity: Severity level (1-4)
        
    Returns:
        Emoji string
    """
    emojis = {
        1: "ℹ️",   # Low/Info
        2: "⚠️",   # Medium/Warning
        3: "🚨",   # High/Alert
        4: "🔴"    # Critical
    }
    return emojis.get(severity, "ℹ️")


def get_status_emoji(status: str) -> str:
    """
    Get emoji for status.
    
    Args:
        status: Status string
        
    Returns:
        Emoji string
    """
    status_lower = status.lower()
    
    emojis = {
        "active": "✅",
        "online": "🟢",
        "offline": "🔴",
        "expired": "⏰",
        "revoked": "🚫",
        "pending": "⏳",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
        "banned": "🚫",
        "trial": "🆓",
        "basic": "📦",
        "pro": "⭐",
        "enterprise": "🏢"
    }
    
    return emojis.get(status_lower, "❓")


def mask_license_key(key: str, visible_chars: int = 4) -> str:
    """
    Mask a license key for display.
    
    Args:
        key: License key
        visible_chars: Number of visible characters at start
        
    Returns:
        Masked key (e.g., "DLNK-****-****-WXYZ")
    """
    if len(key) <= visible_chars * 2:
        return key
    
    parts = key.split('-')
    if len(parts) != 4:
        return key[:visible_chars] + "****" + key[-visible_chars:]
    
    return f"{parts[0]}-****-****-{parts[3]}"


def calculate_expiry_date(days: int) -> datetime:
    """
    Calculate expiry date from now.
    
    Args:
        days: Number of days
        
    Returns:
        Expiry datetime
    """
    return datetime.now() + timedelta(days=days)


def is_expired(expiry_date: datetime) -> bool:
    """
    Check if a date has expired.
    
    Args:
        expiry_date: Expiry datetime
        
    Returns:
        True if expired
    """
    return datetime.now() > expiry_date


def days_until_expiry(expiry_date: datetime) -> int:
    """
    Calculate days until expiry.
    
    Args:
        expiry_date: Expiry datetime
        
    Returns:
        Days until expiry (negative if expired)
    """
    diff = expiry_date - datetime.now()
    return diff.days


def parse_user_id(text: str) -> Optional[str]:
    """
    Parse user ID from text.
    
    Args:
        text: Text containing user ID
        
    Returns:
        User ID or None
    """
    # Try to extract numeric ID
    match = re.search(r'\b(\d{5,15})\b', text)
    if match:
        return match.group(1)
    
    # Try to extract username
    match = re.search(r'@(\w+)', text)
    if match:
        return match.group(1)
    
    return None


def format_bytes(size: int) -> str:
    """
    Format bytes to human readable string.
    
    Args:
        size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a value as percentage.
    
    Args:
        value: Value (0-1 or 0-100)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value <= 1:
        value *= 100
    return f"{value:.{decimals}f}%"


def sanitize_callback_data(data: str, max_length: int = 64) -> str:
    """
    Sanitize callback data for Telegram.
    
    Args:
        data: Callback data
        max_length: Maximum length (Telegram limit is 64 bytes)
        
    Returns:
        Sanitized callback data
    """
    # Remove special characters
    sanitized = re.sub(r'[^\w\-_]', '', data)
    
    # Truncate if too long
    if len(sanitized.encode('utf-8')) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized
