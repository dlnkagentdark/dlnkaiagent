"""
dLNk License Module
ระบบจัดการ License Key
"""

from .generator import (
    LicenseGenerator,
    LicenseData,
    LicenseType,
    LicenseStatus,
    license_generator,
    generate_license,
    generate_encrypted_license
)

from .validator import (
    LicenseValidator,
    ValidationResult,
    license_validator,
    validate_license,
    is_license_valid
)

from .hardware import (
    HardwareID,
    get_hardware_id,
    get_hardware_id_short,
    verify_hardware
)

from .storage import (
    LicenseStorage,
    license_storage
)

__all__ = [
    # Generator
    'LicenseGenerator',
    'LicenseData',
    'LicenseType',
    'LicenseStatus',
    'license_generator',
    'generate_license',
    'generate_encrypted_license',
    
    # Validator
    'LicenseValidator',
    'ValidationResult',
    'license_validator',
    'validate_license',
    'is_license_valid',
    
    # Hardware
    'HardwareID',
    'get_hardware_id',
    'get_hardware_id_short',
    'verify_hardware',
    
    # Storage
    'LicenseStorage',
    'license_storage'
]
