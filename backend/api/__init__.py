"""
dLNk API Module
===============
REST API สำหรับ dLNk IDE

Modules:
- admin_api: Admin API endpoints
"""

from .admin_api import (
    admin_bp,
    create_app,
    create_token,
    verify_token,
    require_auth,
    require_admin
)

__all__ = [
    'admin_bp',
    'create_app',
    'create_token',
    'verify_token',
    'require_auth',
    'require_admin'
]

__version__ = '1.0.0'
