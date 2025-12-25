"""
API Routes Module
"""

from .license import router as license_router
from .auth import router as auth_router

__all__ = ['license_router', 'auth_router']
