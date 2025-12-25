"""
dLNk Authentication Module
ระบบยืนยันตัวตน
"""

from .login import (
    LoginManager,
    LoginResult,
    User,
    login_manager
)

from .register import (
    RegistrationManager,
    RegistrationRequest,
    RegistrationResult,
    registration_manager,
    register_user,
    register_user_async
)

from .session import (
    SessionManager,
    session_manager
)

from .totp import (
    TOTPManager,
    totp_manager,
    is_2fa_available,
    setup_2fa,
    verify_2fa
)

__all__ = [
    # Login
    'LoginManager',
    'LoginResult',
    'User',
    'login_manager',
    
    # Register
    'RegistrationManager',
    'RegistrationRequest',
    'RegistrationResult',
    'registration_manager',
    'register_user',
    'register_user_async',
    
    # Session
    'SessionManager',
    'session_manager',
    
    # TOTP
    'TOTPManager',
    'totp_manager',
    'is_2fa_available',
    'setup_2fa',
    'verify_2fa'
]
