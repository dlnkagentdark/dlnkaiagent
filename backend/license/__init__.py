"""
dLNk License Module
===================
ระบบจัดการ License Keys

Modules:
- license_system: ระบบ License หลัก
"""

from .license_system import (
    License,
    LicenseType,
    LicenseStatus,
    LicenseGenerator,
    LicenseStorage,
    LicenseSystem,
    HWIDGenerator,
    get_license_system
)

__all__ = [
    'License',
    'LicenseType',
    'LicenseStatus',
    'LicenseGenerator',
    'LicenseStorage',
    'LicenseSystem',
    'HWIDGenerator',
    'get_license_system'
]

__version__ = '1.0.0'
