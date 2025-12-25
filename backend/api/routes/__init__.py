"""
dLNk IDE API Routes
"""

from .auth import router as auth_router
from .license import router as license_router

__all__ = ['auth_router', 'license_router']
