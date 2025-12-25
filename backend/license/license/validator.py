"""
License Key Validator
ระบบตรวจสอบ License Key
"""

import json
from datetime import datetime
from typing import Optional, Tuple, List
from dataclasses import dataclass
import logging

import sys
sys.path.append('..')
from config import get_config
from utils.encryption import encryption_manager
from .generator import LicenseData, LicenseStatus
from .hardware import HardwareID, get_hardware_id
from .storage import license_storage, LicenseStorage

logger = logging.getLogger('dLNk-LicenseValidator')
config = get_config()


@dataclass
class ValidationResult:
    """ผลลัพธ์การตรวจสอบ License"""
    valid: bool
    license_data: Optional[LicenseData] = None
    error: Optional[str] = None
    warning: Optional[str] = None
    features: List[str] = None
    days_remaining: int = 0
    
    def __post_init__(self):
        if self.features is None:
            self.features = []


class LicenseValidator:
    """
    ตรวจสอบ License Key
    รองรับทั้ง License Key แบบ DLNK-XXXX-XXXX-XXXX-XXXX และ Encrypted License
    """
    
    def __init__(self, storage: LicenseStorage = None):
        self.encryption = encryption_manager
        self.storage = storage or license_storage
    
    def validate(
        self,
        license_key: str,
        hardware_id: Optional[str] = None,
        ip_address: str = None
    ) -> ValidationResult:
        """
        ตรวจสอบ License Key
        
        Args:
            license_key: License key หรือ encrypted license string
            hardware_id: Hardware ID ของเครื่องปัจจุบัน
            ip_address: IP address (สำหรับ logging)
        
        Returns:
            ValidationResult พร้อมสถานะและข้อมูล
        """
        
        # Get current hardware ID if not provided
        if hardware_id is None:
            hardware_id = get_hardware_id()
        
        # Try to validate as formatted license key (DLNK-XXXX-XXXX-XXXX-XXXX)
        if self._is_formatted_key(license_key):
            return self._validate_formatted_key(license_key, hardware_id, ip_address)
        
        # Try to validate as encrypted license string
        return self._validate_encrypted_key(license_key, hardware_id)
    
    def _is_formatted_key(self, key: str) -> bool:
        """ตรวจสอบว่าเป็น formatted key หรือไม่"""
        import re
        pattern = rf'^{config.LICENSE_PREFIX}-[A-F0-9]{{4}}-[A-F0-9]{{4}}-[A-F0-9]{{4}}-[A-F0-9]{{4}}$'
        return bool(re.match(pattern, key, re.IGNORECASE))
    
    def _validate_formatted_key(
        self,
        license_key: str,
        hardware_id: str,
        ip_address: str = None
    ) -> ValidationResult:
        """ตรวจสอบ formatted license key จาก database"""
        
        # Get license from storage
        license_dict = self.storage.get_license(license_key)
        
        if not license_dict:
            return ValidationResult(
                valid=False,
                error="License key not found"
            )
        
        # Check if revoked
        if self.storage.is_revoked(license_key):
            return ValidationResult(
                valid=False,
                error="License has been revoked"
            )
        
        # Check status
        status = license_dict.get('status')
        if status == LicenseStatus.REVOKED.value:
            return ValidationResult(
                valid=False,
                error="License has been revoked"
            )
        
        if status == LicenseStatus.SUSPENDED.value:
            return ValidationResult(
                valid=False,
                error="License has been suspended"
            )
        
        # Check expiration
        expires_at = license_dict.get('expires_at')
        if expires_at:
            expiry_date = datetime.fromisoformat(expires_at)
            if datetime.now() > expiry_date:
                # Update status to expired
                self.storage.update_license_status(license_key, LicenseStatus.EXPIRED)
                return ValidationResult(
                    valid=False,
                    error="License has expired"
                )
        
        # Check hardware binding
        stored_hwid = license_dict.get('hardware_id')
        max_devices = license_dict.get('max_devices', 1)
        
        if stored_hwid and stored_hwid != hardware_id:
            # Check if max devices exceeded
            activation_count = self.storage.get_activation_count(license_key)
            if activation_count >= max_devices:
                return ValidationResult(
                    valid=False,
                    error=f"Maximum devices exceeded ({activation_count}/{max_devices})"
                )
        
        # Record activation
        self.storage.record_activation(
            license_key=license_key,
            hardware_id=hardware_id,
            ip_address=ip_address
        )
        
        # Update hardware ID if not set
        if not stored_hwid:
            self.storage.update_hardware_id(license_key, hardware_id)
        
        # Create license data object
        license_data = LicenseData(
            license_id=license_dict.get('license_id'),
            user_id=license_dict.get('user_id'),
            license_type=license_dict.get('license_type'),
            created_at=license_dict.get('created_at'),
            expires_at=license_dict.get('expires_at'),
            hardware_id=hardware_id,
            features=license_dict.get('features', []),
            max_devices=max_devices,
            owner_name=license_dict.get('owner_name', ''),
            email=license_dict.get('email', '')
        )
        
        # Calculate days remaining
        days_remaining = license_data.days_remaining()
        warning = None
        if days_remaining <= 7:
            warning = f"License expires in {days_remaining} days"
        
        return ValidationResult(
            valid=True,
            license_data=license_data,
            features=license_data.features,
            days_remaining=days_remaining,
            warning=warning
        )
    
    def _validate_encrypted_key(
        self,
        encrypted_key: str,
        hardware_id: str
    ) -> ValidationResult:
        """ตรวจสอบ encrypted license string (compatible กับระบบเดิม)"""
        
        try:
            # Decrypt
            decrypted = self.encryption.decrypt(encrypted_key)
            
            if decrypted is None:
                return ValidationResult(
                    valid=False,
                    error="Invalid license key format"
                )
            
            # Check expiration
            expiry_str = decrypted.get('expiry')
            if expiry_str:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                if datetime.now() > expiry_date:
                    return ValidationResult(
                        valid=False,
                        error=f"License expired on {expiry_str}"
                    )
            
            # Create license data
            license_data = LicenseData(
                license_id=decrypted.get('license_id', 'encrypted'),
                user_id=decrypted.get('user_id', 'legacy'),
                license_type=decrypted.get('license_type', 'pro'),
                created_at=decrypted.get('created_at', ''),
                expires_at=expiry_str + "T23:59:59" if expiry_str else '',
                hardware_id=hardware_id,
                features=decrypted.get('features', []),
                owner_name=decrypted.get('owner', '')
            )
            
            days_remaining = license_data.days_remaining()
            warning = None
            if days_remaining <= 7:
                warning = f"License expires in {days_remaining} days"
            
            return ValidationResult(
                valid=True,
                license_data=license_data,
                features=license_data.features,
                days_remaining=days_remaining,
                warning=warning
            )
            
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return ValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}"
            )
    
    def get_features(self, license_key: str) -> List[str]:
        """ดึงรายการ features ที่เปิดใช้งาน"""
        result = self.validate(license_key)
        return result.features if result.valid else []
    
    def get_expiry(self, license_key: str) -> Optional[datetime]:
        """ดึงวันหมดอายุ"""
        result = self.validate(license_key)
        if result.valid and result.license_data:
            return datetime.fromisoformat(result.license_data.expires_at)
        return None
    
    def has_feature(self, license_key: str, feature: str) -> bool:
        """ตรวจสอบว่ามี feature หรือไม่"""
        features = self.get_features(license_key)
        return feature in features or 'all_features' in features
    
    def is_valid(self, license_key: str) -> bool:
        """ตรวจสอบว่า license valid หรือไม่ (quick check)"""
        result = self.validate(license_key)
        return result.valid


# Global instance
license_validator = LicenseValidator()


def validate_license(license_key: str, hardware_id: str = None) -> ValidationResult:
    """Shortcut function for validation"""
    return license_validator.validate(license_key, hardware_id)


def is_license_valid(license_key: str) -> bool:
    """Quick validation check"""
    return license_validator.is_valid(license_key)
