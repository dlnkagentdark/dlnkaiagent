#!/usr/bin/env python3
"""
dLNk License System
====================
ระบบจัดการ License Keys พร้อม Online Validation

Features:
- สร้าง License Keys
- Validate License (Online + Offline)
- HWID Binding
- License Expiration
- Usage Tracking

Author: dLNk IDE Project (AI-01 The Architect)
Date: December 25, 2025
"""

import os
import json
import uuid
import hashlib
import secrets
import platform
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LicenseType(Enum):
    """ประเภท License"""
    TRIAL = "trial"           # ทดลองใช้ 7 วัน
    BASIC = "basic"           # 1 เดือน
    PRO = "pro"               # 3 เดือน
    ENTERPRISE = "enterprise" # 1 ปี
    LIFETIME = "lifetime"     # ตลอดชีพ


class LicenseStatus(Enum):
    """สถานะ License"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    PENDING = "pending"


@dataclass
class License:
    """โครงสร้างข้อมูล License"""
    key: str
    license_type: LicenseType
    status: LicenseStatus = LicenseStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    activated_at: Optional[str] = None
    expires_at: Optional[str] = None
    hwid: Optional[str] = None
    user_email: Optional[str] = None
    max_activations: int = 1
    current_activations: int = 0
    features: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """แปลงเป็น dictionary"""
        data = asdict(self)
        data['license_type'] = self.license_type.value
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'License':
        """สร้างจาก dictionary"""
        data['license_type'] = LicenseType(data['license_type'])
        data['status'] = LicenseStatus(data['status'])
        return cls(**data)
    
    @property
    def is_valid(self) -> bool:
        """ตรวจสอบว่า license ยังใช้ได้"""
        if self.status != LicenseStatus.ACTIVE:
            return False
        
        if self.expires_at:
            expires = datetime.fromisoformat(self.expires_at)
            if datetime.now() > expires:
                return False
        
        return True


class LicenseGenerator:
    """สร้าง License Keys"""
    
    PREFIX = "DLNK"
    SEGMENT_LENGTH = 4
    NUM_SEGMENTS = 4
    
    @classmethod
    def generate(cls, license_type: LicenseType = LicenseType.BASIC) -> str:
        """
        สร้าง License Key ใหม่
        
        Format: DLNK-XXXX-XXXX-XXXX-XXXX
        """
        # สร้าง random segments
        segments = [
            secrets.token_hex(cls.SEGMENT_LENGTH // 2).upper()
            for _ in range(cls.NUM_SEGMENTS)
        ]
        
        # เพิ่ม type indicator ใน segment แรก
        type_codes = {
            LicenseType.TRIAL: "T",
            LicenseType.BASIC: "B",
            LicenseType.PRO: "P",
            LicenseType.ENTERPRISE: "E",
            LicenseType.LIFETIME: "L"
        }
        segments[0] = type_codes.get(license_type, "B") + segments[0][1:]
        
        return f"{cls.PREFIX}-{'-'.join(segments)}"
    
    @classmethod
    def validate_format(cls, key: str) -> bool:
        """ตรวจสอบ format ของ key"""
        if not key:
            return False
        
        parts = key.split('-')
        if len(parts) != cls.NUM_SEGMENTS + 1:
            return False
        
        if parts[0] != cls.PREFIX:
            return False
        
        # First segment can have type indicator (T, B, P, E, L)
        for i, segment in enumerate(parts[1:]):
            if len(segment) != cls.SEGMENT_LENGTH:
                return False
            # First segment: first char can be type indicator
            if i == 0:
                if segment[0] not in 'TBPEL0123456789ABCDEF':
                    return False
                if not all(c in '0123456789ABCDEF' for c in segment[1:]):
                    return False
            else:
                if not all(c in '0123456789ABCDEF' for c in segment):
                    return False
        
        return True


class HWIDGenerator:
    """สร้าง Hardware ID"""
    
    @classmethod
    def generate(cls) -> str:
        """สร้าง HWID จากข้อมูล hardware"""
        components = []
        
        # Machine ID
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'csproduct', 'get', 'uuid'],
                    capture_output=True, text=True, timeout=5
                )
                uuid_line = result.stdout.strip().split('\n')[-1].strip()
                if uuid_line:
                    components.append(uuid_line)
            else:
                # Linux/Mac
                machine_id_paths = [
                    '/etc/machine-id',
                    '/var/lib/dbus/machine-id'
                ]
                for path in machine_id_paths:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            components.append(f.read().strip())
                        break
        except Exception as e:
            logger.warning(f"Could not get machine ID: {e}")
        
        # CPU Info
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'processorid'],
                    capture_output=True, text=True, timeout=5
                )
                cpu_id = result.stdout.strip().split('\n')[-1].strip()
                if cpu_id:
                    components.append(cpu_id)
            else:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'Serial' in line or 'model name' in line:
                            components.append(line.split(':')[-1].strip())
                            break
        except Exception as e:
            logger.warning(f"Could not get CPU info: {e}")
        
        # Fallback
        if not components:
            components.append(platform.node())
            components.append(platform.machine())
        
        # Hash components
        combined = '|'.join(components)
        hwid = hashlib.sha256(combined.encode()).hexdigest()[:32].upper()
        
        return hwid


class LicenseStorage:
    """จัดเก็บ License Data"""
    
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), "licenses.json"
        )
        self.licenses: Dict[str, License] = {}
        self._load()
    
    def _load(self) -> None:
        """โหลด licenses จากไฟล์"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.licenses = {
                        k: License.from_dict(v) 
                        for k, v in data.items()
                    }
                logger.info(f"✅ Loaded {len(self.licenses)} licenses")
        except Exception as e:
            logger.error(f"❌ Error loading licenses: {e}")
            self.licenses = {}
    
    def _save(self) -> None:
        """บันทึก licenses ลงไฟล์"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                data = {k: v.to_dict() for k, v in self.licenses.items()}
                json.dump(data, f, indent=2)
            logger.info(f"✅ Saved {len(self.licenses)} licenses")
        except Exception as e:
            logger.error(f"❌ Error saving licenses: {e}")
    
    def add(self, license: License) -> bool:
        """เพิ่ม license"""
        if license.key in self.licenses:
            return False
        self.licenses[license.key] = license
        self._save()
        return True
    
    def get(self, key: str) -> Optional[License]:
        """ดึง license"""
        return self.licenses.get(key)
    
    def update(self, license: License) -> bool:
        """อัพเดท license"""
        if license.key not in self.licenses:
            return False
        self.licenses[license.key] = license
        self._save()
        return True
    
    def delete(self, key: str) -> bool:
        """ลบ license"""
        if key in self.licenses:
            del self.licenses[key]
            self._save()
            return True
        return False
    
    def list_all(self) -> List[License]:
        """ดึงรายการ licenses ทั้งหมด"""
        return list(self.licenses.values())


class LicenseSystem:
    """
    ระบบจัดการ License หลัก
    
    ใช้งาน:
    ```python
    system = LicenseSystem()
    
    # สร้าง license
    license = system.create_license(LicenseType.PRO)
    
    # Validate
    result = system.validate(license.key, hwid="ABC123")
    ```
    """
    
    # License duration in days
    DURATIONS = {
        LicenseType.TRIAL: 7,
        LicenseType.BASIC: 30,
        LicenseType.PRO: 90,
        LicenseType.ENTERPRISE: 365,
        LicenseType.LIFETIME: None  # No expiration
    }
    
    def __init__(
        self,
        storage: Optional[LicenseStorage] = None,
        validation_server: Optional[str] = None
    ):
        self.storage = storage or LicenseStorage()
        self.validation_server = validation_server
        self.offline_grace_period = 7  # วันที่อนุญาตให้ใช้ offline
    
    def create_license(
        self,
        license_type: LicenseType = LicenseType.BASIC,
        user_email: Optional[str] = None,
        features: Optional[List[str]] = None,
        max_activations: int = 1
    ) -> License:
        """
        สร้าง License ใหม่
        
        Args:
            license_type: ประเภท license
            user_email: Email ของผู้ใช้
            features: Features ที่เปิดใช้งาน
            max_activations: จำนวน activations สูงสุด
            
        Returns:
            License object
        """
        key = LicenseGenerator.generate(license_type)
        
        # คำนวณวันหมดอายุ
        duration = self.DURATIONS.get(license_type)
        expires_at = None
        if duration:
            expires_at = (datetime.now() + timedelta(days=duration)).isoformat()
        
        license = License(
            key=key,
            license_type=license_type,
            status=LicenseStatus.PENDING,
            user_email=user_email,
            expires_at=expires_at,
            max_activations=max_activations,
            features=features or self._get_default_features(license_type)
        )
        
        self.storage.add(license)
        logger.info(f"✅ Created license: {key} ({license_type.value})")
        
        return license
    
    def _get_default_features(self, license_type: LicenseType) -> List[str]:
        """ดึง features เริ่มต้นตามประเภท"""
        base_features = ["ai_chat", "code_completion"]
        
        if license_type == LicenseType.TRIAL:
            return base_features
        
        if license_type == LicenseType.BASIC:
            return base_features + ["all_ai_modes"]
        
        if license_type == LicenseType.PRO:
            return base_features + ["all_ai_modes", "priority_support", "custom_prompts"]
        
        if license_type in [LicenseType.ENTERPRISE, LicenseType.LIFETIME]:
            return base_features + [
                "all_ai_modes", "priority_support", "custom_prompts",
                "team_features", "api_access", "white_label"
            ]
        
        return base_features
    
    def activate(
        self,
        key: str,
        hwid: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Activate License
        
        Args:
            key: License key
            hwid: Hardware ID (จะสร้างอัตโนมัติถ้าไม่ระบุ)
            
        Returns:
            Tuple of (success, message)
        """
        # Validate format
        if not LicenseGenerator.validate_format(key):
            return False, "Invalid license key format"
        
        # Get license
        license = self.storage.get(key)
        if not license:
            return False, "License key not found"
        
        # Check status
        if license.status == LicenseStatus.REVOKED:
            return False, "License has been revoked"
        
        if license.status == LicenseStatus.SUSPENDED:
            return False, "License is suspended"
        
        # Check activations
        if license.current_activations >= license.max_activations:
            if license.hwid and license.hwid != hwid:
                return False, "Maximum activations reached"
        
        # Generate HWID if not provided
        if not hwid:
            hwid = HWIDGenerator.generate()
        
        # Check HWID binding
        if license.hwid and license.hwid != hwid:
            return False, "License is bound to different hardware"
        
        # Activate
        license.status = LicenseStatus.ACTIVE
        license.activated_at = datetime.now().isoformat()
        license.hwid = hwid
        license.current_activations += 1
        
        self.storage.update(license)
        logger.info(f"✅ Activated license: {key}")
        
        return True, "License activated successfully"
    
    def validate(
        self,
        key: str,
        hwid: Optional[str] = None,
        online: bool = True
    ) -> Dict[str, Any]:
        """
        Validate License
        
        Args:
            key: License key
            hwid: Hardware ID
            online: ลอง online validation ก่อน
            
        Returns:
            Validation result
        """
        result = {
            "valid": False,
            "key": key,
            "message": "",
            "license_type": None,
            "features": [],
            "expires_at": None,
            "validation_method": "offline"
        }
        
        # Try online validation first
        if online and self.validation_server:
            online_result = self._validate_online(key, hwid)
            if online_result.get("success"):
                result.update(online_result.get("data", {}))
                result["validation_method"] = "online"
                return result
        
        # Offline validation
        return self._validate_offline(key, hwid)
    
    def _validate_online(
        self,
        key: str,
        hwid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Online validation ผ่าน server"""
        try:
            response = requests.post(
                f"{self.validation_server}/api/licenses/validate",
                json={"license_key": key, "hwid": hwid},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.warning(f"⚠️ Online validation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_offline(
        self,
        key: str,
        hwid: Optional[str] = None
    ) -> Dict[str, Any]:
        """Offline validation"""
        result = {
            "valid": False,
            "key": key,
            "message": "",
            "license_type": None,
            "features": [],
            "expires_at": None,
            "validation_method": "offline"
        }
        
        # Validate format
        if not LicenseGenerator.validate_format(key):
            result["message"] = "Invalid license key format"
            return result
        
        # Get license
        license = self.storage.get(key)
        if not license:
            result["message"] = "License key not found"
            return result
        
        # Check status
        if license.status != LicenseStatus.ACTIVE:
            result["message"] = f"License is {license.status.value}"
            return result
        
        # Check expiration
        if license.expires_at:
            expires = datetime.fromisoformat(license.expires_at)
            if datetime.now() > expires:
                result["message"] = "License has expired"
                return result
        
        # Check HWID
        if hwid and license.hwid and license.hwid != hwid:
            result["message"] = "Hardware mismatch"
            return result
        
        # Valid!
        result["valid"] = True
        result["message"] = "License is valid"
        result["license_type"] = license.license_type.value
        result["features"] = license.features
        result["expires_at"] = license.expires_at
        
        return result
    
    def revoke(self, key: str, reason: str = "") -> bool:
        """Revoke license"""
        license = self.storage.get(key)
        if not license:
            return False
        
        license.status = LicenseStatus.REVOKED
        license.metadata["revoked_at"] = datetime.now().isoformat()
        license.metadata["revoke_reason"] = reason
        
        self.storage.update(license)
        logger.info(f"❌ Revoked license: {key}")
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """ดึงสถิติ licenses"""
        licenses = self.storage.list_all()
        
        stats = {
            "total": len(licenses),
            "by_status": {},
            "by_type": {},
            "active": 0,
            "expired": 0
        }
        
        for license in licenses:
            # By status
            status = license.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # By type
            ltype = license.license_type.value
            stats["by_type"][ltype] = stats["by_type"].get(ltype, 0) + 1
            
            # Active/Expired
            if license.is_valid:
                stats["active"] += 1
            elif license.status == LicenseStatus.ACTIVE:
                stats["expired"] += 1
        
        return stats


# ==================== Singleton Instance ====================

_license_system: Optional[LicenseSystem] = None


def get_license_system(validation_server: Optional[str] = None) -> LicenseSystem:
    """ดึง Singleton instance ของ LicenseSystem"""
    global _license_system
    
    if _license_system is None:
        server = validation_server or os.environ.get("LICENSE_VALIDATION_SERVER")
        _license_system = LicenseSystem(validation_server=server)
    
    return _license_system


# ==================== Test ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing License System")
    print("=" * 60)
    
    # Create system
    system = LicenseSystem()
    
    # Test 1: Generate keys
    print("\n📤 Test 1: Generate license keys")
    for ltype in LicenseType:
        key = LicenseGenerator.generate(ltype)
        print(f"  {ltype.value}: {key}")
    
    # Test 2: Create license
    print("\n📤 Test 2: Create license")
    license = system.create_license(
        license_type=LicenseType.PRO,
        user_email="test@example.com"
    )
    print(f"  Key: {license.key}")
    print(f"  Type: {license.license_type.value}")
    print(f"  Features: {license.features}")
    
    # Test 3: Generate HWID
    print("\n📤 Test 3: Generate HWID")
    hwid = HWIDGenerator.generate()
    print(f"  HWID: {hwid}")
    
    # Test 4: Activate license
    print("\n📤 Test 4: Activate license")
    success, message = system.activate(license.key, hwid)
    print(f"  Success: {success}")
    print(f"  Message: {message}")
    
    # Test 5: Validate license
    print("\n📤 Test 5: Validate license")
    result = system.validate(license.key, hwid, online=False)
    print(f"  Valid: {result['valid']}")
    print(f"  Message: {result['message']}")
    print(f"  Features: {result['features']}")
    
    # Test 6: Get stats
    print("\n📤 Test 6: Get stats")
    stats = system.get_stats()
    print(f"  Total: {stats['total']}")
    print(f"  Active: {stats['active']}")
    print(f"  By type: {stats['by_type']}")
    
    print("\n✅ License System test completed!")
