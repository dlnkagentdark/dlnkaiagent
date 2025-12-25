"""
dLNk Security Module
====================
ระบบรักษาความปลอดภัย

Modules:
- encryption: เข้ารหัสข้อมูล
- two_factor: Two-Factor Authentication
"""

from .encryption import (
    KeyManager,
    DataEncryptor,
    SecureTokenStorage,
    PromptFilter,
    EncryptionError,
    get_key_manager,
    get_encryptor,
    get_secure_storage
)

from .two_factor import (
    TOTPGenerator,
    TwoFactorConfig,
    BackupCodeGenerator,
    TwoFactorAuth,
    get_two_factor_auth
)

__all__ = [
    # Encryption
    'KeyManager',
    'DataEncryptor',
    'SecureTokenStorage',
    'PromptFilter',
    'EncryptionError',
    'get_key_manager',
    'get_encryptor',
    'get_secure_storage',
    
    # Two-Factor Auth
    'TOTPGenerator',
    'TwoFactorConfig',
    'BackupCodeGenerator',
    'TwoFactorAuth',
    'get_two_factor_auth'
]

__version__ = '1.0.0'
