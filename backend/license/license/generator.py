"""
License Key Generator
ระบบสร้าง License Key แบบเข้ารหัส
Based on: /source-files/dlnk_core/dlnk_license_manager.py
"""

import uuid
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

import sys
sys.path.append('..')
from config import get_config
from utils.encryption import encryption_manager

logger = logging.getLogger('dLNk-LicenseGen')
config = get_config()


class LicenseType(Enum):
    """ประเภท License"""
    TRIAL = "trial"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class LicenseStatus(Enum):
    """สถานะ License"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


@dataclass
class LicenseData:
    """โครงสร้างข้อมูล License"""
    license_id: str
    user_id: str
    license_type: str  # 'trial', 'pro', 'enterprise'
    created_at: str
    expires_at: str
    hardware_id: Optional[str] = None
    features: List[str] = field(default_factory=list)
    max_devices: int = 1
    owner_name: str = ""
    email: str = ""
    
    def to_dict(self) -> Dict:
        """แปลงเป็น dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LicenseData':
        """สร้างจาก dictionary"""
        return cls(**data)
    
    def is_expired(self) -> bool:
        """ตรวจสอบว่าหมดอายุหรือยัง"""
        expires = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expires
    
    def days_remaining(self) -> int:
        """จำนวนวันที่เหลือ"""
        expires = datetime.fromisoformat(self.expires_at)
        delta = expires - datetime.now()
        return max(0, delta.days)


class LicenseGenerator:
    """
    สร้าง License Key แบบเข้ารหัส
    """
    
    def __init__(self):
        self.encryption = encryption_manager
        self._license_cache: Dict[str, str] = {}  # key -> encrypted_data mapping
    
    def generate(
        self,
        user_id: str,
        license_type: str = 'pro',
        duration_days: int = 365,
        features: List[str] = None,
        hardware_id: Optional[str] = None,
        max_devices: int = 1,
        owner_name: str = "",
        email: str = ""
    ) -> tuple[str, str]:
        """
        สร้าง License Key ใหม่
        
        Args:
            user_id: User identifier
            license_type: 'trial', 'pro', or 'enterprise'
            duration_days: จำนวนวันที่ใช้งานได้
            features: รายการ features ที่เปิดใช้
            hardware_id: Hardware ID สำหรับผูกเครื่อง (optional)
            max_devices: จำนวนเครื่องสูงสุด
            owner_name: ชื่อเจ้าของ
            email: อีเมล
        
        Returns:
            Tuple of (license_key, encrypted_data)
        """
        
        # Default features based on type
        if features is None:
            features = self._get_default_features(license_type)
        
        # Create license data
        license_data = LicenseData(
            license_id=str(uuid.uuid4()),
            user_id=user_id,
            license_type=license_type,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=duration_days)).isoformat(),
            hardware_id=hardware_id,
            features=features,
            max_devices=max_devices,
            owner_name=owner_name,
            email=email
        )
        
        # Encrypt license data
        encrypted_data = self.encryption.encrypt(license_data.to_dict())
        
        # Generate formatted license key
        license_key = self._generate_license_key()
        
        # Store mapping (in production, this should be in database)
        self._license_cache[license_key] = encrypted_data
        
        logger.info(f"License generated: {license_key} for user {user_id}")
        
        return license_key, encrypted_data
    
    def generate_encrypted_only(
        self,
        user_id: str,
        license_type: str = 'pro',
        duration_days: int = 365,
        features: List[str] = None,
        owner_name: str = "User"
    ) -> str:
        """
        สร้าง License Key แบบเข้ารหัสอย่างเดียว (compatible กับระบบเดิม)
        
        Returns:
            Encrypted license string
        """
        if features is None:
            features = self._get_default_features(license_type)
        
        data = {
            "license_id": str(uuid.uuid4()),
            "user_id": user_id,
            "owner": owner_name,
            "license_type": license_type,
            "expiry": (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d"),
            "features": features,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.encryption.encrypt(data)
    
    def _generate_license_key(self) -> str:
        """
        สร้าง License Key ในรูปแบบ DLNK-XXXX-XXXX-XXXX-XXXX
        """
        segments = [secrets.token_hex(2).upper() for _ in range(4)]
        return f"{config.LICENSE_PREFIX}-{'-'.join(segments)}"
    
    def _get_default_features(self, license_type: str) -> List[str]:
        """Get default features for license type"""
        return config.FEATURES.get(license_type, config.FEATURES['trial'])
    
    def get_encrypted_data(self, license_key: str) -> Optional[str]:
        """ดึง encrypted data จาก license key"""
        return self._license_cache.get(license_key)
    
    def store_license_mapping(self, license_key: str, encrypted_data: str):
        """เก็บ mapping ระหว่าง license key และ encrypted data"""
        self._license_cache[license_key] = encrypted_data
    
    @staticmethod
    def calculate_checksum(data: str) -> str:
        """คำนวณ checksum"""
        return hashlib.sha256(data.encode()).hexdigest()[:8]


# Global instance
license_generator = LicenseGenerator()


def generate_license(
    user_id: str,
    license_type: str = 'pro',
    duration_days: int = 365,
    **kwargs
) -> tuple[str, str]:
    """Shortcut function for generating license"""
    return license_generator.generate(
        user_id=user_id,
        license_type=license_type,
        duration_days=duration_days,
        **kwargs
    )


def generate_encrypted_license(
    days_valid: int = 30,
    owner: str = "User",
    features: List[str] = None
) -> str:
    """
    Compatible function with original dlnk_license_manager.py
    """
    return license_generator.generate_encrypted_only(
        user_id="legacy",
        license_type="pro",
        duration_days=days_valid,
        features=features,
        owner_name=owner
    )
