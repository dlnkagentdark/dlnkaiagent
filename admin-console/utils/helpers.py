#!/usr/bin/env python3
"""
dLNk Admin Console - Helper Functions
"""

from datetime import datetime
from typing import Optional

def format_datetime(dt_string: str, format_type: str = 'full') -> str:
    """Format datetime string for display"""
    try:
        if isinstance(dt_string, str):
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        else:
            dt = dt_string
        
        if format_type == 'full':
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'date':
            return dt.strftime('%Y-%m-%d')
        elif format_type == 'time':
            return dt.strftime('%H:%M:%S')
        elif format_type == 'short':
            return dt.strftime('%m/%d %H:%M')
        else:
            return str(dt)
    except Exception:
        return dt_string or 'N/A'

def format_number(num: int, abbreviate: bool = True) -> str:
    """Format number with abbreviation"""
    if not abbreviate or num < 1000:
        return f"{num:,}"
    elif num < 1000000:
        return f"{num/1000:.1f}K"
    elif num < 1000000000:
        return f"{num/1000000:.1f}M"
    else:
        return f"{num/1000000000:.1f}B"

def truncate_text(text: str, max_length: int = 50, suffix: str = '...') -> str:
    """Truncate text to max length"""
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def validate_admin_key(key: str) -> bool:
    """Validate admin key format"""
    if not key:
        return False
    return key.startswith('DLNK-ADMIN-') and len(key) >= 20

def get_status_text(status: str) -> str:
    """Get display text for status"""
    status_map = {
        'active': '✓ Active',
        'expired': '⏱ Expired',
        'revoked': '✗ Revoked',
        'blocked': '⛔ Blocked',
        'pending': '⏳ Pending',
    }
    return status_map.get(status.lower(), status)

def calculate_days_remaining(expiry_date: str) -> int:
    """Calculate days remaining until expiry"""
    try:
        expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
        delta = expiry - datetime.now()
        return max(0, delta.days)
    except Exception:
        return 0
