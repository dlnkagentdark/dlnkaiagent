#!/usr/bin/env python3
"""
dLNk Security Module - Two-Factor Authentication
=================================================
ระบบ 2FA สำหรับ Admin App

Features:
- TOTP (Time-based One-Time Password)
- QR Code generation
- Backup codes
- Session management

Author: dLNk IDE Project (AI-01 The Architect)
Date: December 25, 2025
"""

import os
import json
import hmac
import time
import struct
import base64
import hashlib
import secrets
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TOTPGenerator:
    """
    TOTP Generator (RFC 6238)
    
    ใช้งาน:
    ```python
    totp = TOTPGenerator(secret)
    
    # Generate code
    code = totp.generate()
    
    # Verify code
    is_valid = totp.verify("123456")
    ```
    """
    
    DIGITS = 6
    INTERVAL = 30  # seconds
    ALGORITHM = 'sha1'
    
    def __init__(self, secret: Optional[str] = None):
        if secret:
            self.secret = secret
        else:
            self.secret = self._generate_secret()
    
    @staticmethod
    def _generate_secret(length: int = 32) -> str:
        """สร้าง secret ใหม่"""
        # Generate random bytes and encode as base32
        random_bytes = secrets.token_bytes(length)
        return base64.b32encode(random_bytes).decode('utf-8').rstrip('=')
    
    def _get_counter(self, timestamp: Optional[float] = None) -> int:
        """คำนวณ counter จาก timestamp"""
        if timestamp is None:
            timestamp = time.time()
        return int(timestamp // self.INTERVAL)
    
    def _hotp(self, counter: int) -> str:
        """Generate HOTP code"""
        # Decode secret
        secret_bytes = base64.b32decode(self.secret + '=' * (8 - len(self.secret) % 8))
        
        # Pack counter as big-endian 64-bit integer
        counter_bytes = struct.pack('>Q', counter)
        
        # Calculate HMAC
        hmac_hash = hmac.new(secret_bytes, counter_bytes, self.ALGORITHM).digest()
        
        # Dynamic truncation
        offset = hmac_hash[-1] & 0x0f
        truncated = struct.unpack('>I', hmac_hash[offset:offset + 4])[0]
        truncated &= 0x7fffffff
        
        # Generate code
        code = truncated % (10 ** self.DIGITS)
        return str(code).zfill(self.DIGITS)
    
    def generate(self, timestamp: Optional[float] = None) -> str:
        """
        Generate TOTP code
        
        Args:
            timestamp: Unix timestamp (default: current time)
            
        Returns:
            6-digit code
        """
        counter = self._get_counter(timestamp)
        return self._hotp(counter)
    
    def verify(
        self,
        code: str,
        window: int = 1,
        timestamp: Optional[float] = None
    ) -> bool:
        """
        Verify TOTP code
        
        Args:
            code: Code to verify
            window: Number of intervals to check (before and after)
            timestamp: Unix timestamp (default: current time)
            
        Returns:
            True if valid
        """
        if not code or len(code) != self.DIGITS:
            return False
        
        counter = self._get_counter(timestamp)
        
        # Check current and adjacent intervals
        for offset in range(-window, window + 1):
            expected = self._hotp(counter + offset)
            if hmac.compare_digest(code, expected):
                return True
        
        return False
    
    def get_provisioning_uri(
        self,
        account_name: str,
        issuer: str = "dLNk IDE"
    ) -> str:
        """
        Generate provisioning URI for QR code
        
        Args:
            account_name: User's account name/email
            issuer: Application name
            
        Returns:
            otpauth:// URI
        """
        from urllib.parse import quote
        
        params = {
            'secret': self.secret,
            'issuer': issuer,
            'algorithm': self.ALGORITHM.upper(),
            'digits': str(self.DIGITS),
            'period': str(self.INTERVAL)
        }
        
        param_str = '&'.join(f'{k}={quote(v)}' for k, v in params.items())
        
        return f"otpauth://totp/{quote(issuer)}:{quote(account_name)}?{param_str}"


@dataclass
class TwoFactorConfig:
    """Configuration สำหรับ 2FA"""
    user_id: str
    secret: str
    enabled: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified_at: Optional[str] = None
    backup_codes: List[str] = field(default_factory=list)
    used_backup_codes: List[str] = field(default_factory=list)
    last_used: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """แปลงเป็น dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TwoFactorConfig':
        """สร้างจาก dictionary"""
        return cls(**data)


class BackupCodeGenerator:
    """สร้าง Backup Codes"""
    
    CODE_LENGTH = 8
    CODE_COUNT = 10
    
    @classmethod
    def generate(cls, count: int = None) -> List[str]:
        """
        สร้าง backup codes
        
        Args:
            count: จำนวน codes (default: 10)
            
        Returns:
            List of backup codes
        """
        count = count or cls.CODE_COUNT
        codes = []
        
        for _ in range(count):
            # Generate random code
            code = secrets.token_hex(cls.CODE_LENGTH // 2).upper()
            # Format: XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        
        return codes
    
    @classmethod
    def verify(cls, code: str, valid_codes: List[str]) -> bool:
        """
        Verify backup code
        
        Args:
            code: Code to verify
            valid_codes: List of valid codes
            
        Returns:
            True if valid
        """
        # Normalize code
        normalized = code.upper().replace('-', '').replace(' ', '')
        
        for valid in valid_codes:
            valid_normalized = valid.upper().replace('-', '').replace(' ', '')
            if hmac.compare_digest(normalized, valid_normalized):
                return True
        
        return False


class TwoFactorAuth:
    """
    ระบบ Two-Factor Authentication หลัก
    
    ใช้งาน:
    ```python
    tfa = TwoFactorAuth()
    
    # Setup 2FA
    setup = tfa.setup("user123")
    print(f"Secret: {setup['secret']}")
    print(f"QR URI: {setup['qr_uri']}")
    
    # Verify and enable
    if tfa.verify_setup("user123", "123456"):
        print("2FA enabled!")
    
    # Verify login
    if tfa.verify("user123", "123456"):
        print("Login successful!")
    ```
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), "2fa_config.json"
        )
        self.configs: Dict[str, TwoFactorConfig] = {}
        self._load()
    
    def _load(self) -> None:
        """โหลด configs จากไฟล์"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.configs = {
                        k: TwoFactorConfig.from_dict(v) 
                        for k, v in data.items()
                    }
                logger.info(f"✅ Loaded {len(self.configs)} 2FA configs")
        except Exception as e:
            logger.error(f"❌ Error loading 2FA configs: {e}")
            self.configs = {}
    
    def _save(self) -> None:
        """บันทึก configs ลงไฟล์"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                data = {k: v.to_dict() for k, v in self.configs.items()}
                json.dump(data, f, indent=2)
            # Set restrictive permissions
            os.chmod(self.storage_path, 0o600)
            logger.info(f"✅ Saved {len(self.configs)} 2FA configs")
        except Exception as e:
            logger.error(f"❌ Error saving 2FA configs: {e}")
    
    def setup(
        self,
        user_id: str,
        account_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Setup 2FA สำหรับ user
        
        Args:
            user_id: User ID
            account_name: Account name for QR code (default: user_id)
            
        Returns:
            Setup information
        """
        # Generate new secret
        totp = TOTPGenerator()
        
        # Generate backup codes
        backup_codes = BackupCodeGenerator.generate()
        
        # Create config
        config = TwoFactorConfig(
            user_id=user_id,
            secret=totp.secret,
            backup_codes=backup_codes
        )
        
        self.configs[user_id] = config
        self._save()
        
        # Generate provisioning URI
        qr_uri = totp.get_provisioning_uri(account_name or user_id)
        
        logger.info(f"✅ 2FA setup for user: {user_id}")
        
        return {
            "secret": totp.secret,
            "qr_uri": qr_uri,
            "backup_codes": backup_codes,
            "message": "Scan QR code with authenticator app, then verify with a code"
        }
    
    def verify_setup(self, user_id: str, code: str) -> bool:
        """
        Verify setup และ enable 2FA
        
        Args:
            user_id: User ID
            code: TOTP code from authenticator
            
        Returns:
            True if verified and enabled
        """
        config = self.configs.get(user_id)
        if not config:
            logger.warning(f"⚠️ No 2FA config for user: {user_id}")
            return False
        
        if config.enabled:
            logger.warning(f"⚠️ 2FA already enabled for user: {user_id}")
            return False
        
        # Verify code
        totp = TOTPGenerator(config.secret)
        if totp.verify(code):
            config.enabled = True
            config.verified_at = datetime.now().isoformat()
            self._save()
            
            logger.info(f"✅ 2FA enabled for user: {user_id}")
            return True
        
        logger.warning(f"⚠️ Invalid code for user: {user_id}")
        return False
    
    def verify(
        self,
        user_id: str,
        code: str,
        allow_backup: bool = True
    ) -> Tuple[bool, str]:
        """
        Verify 2FA code
        
        Args:
            user_id: User ID
            code: TOTP or backup code
            allow_backup: Allow backup codes
            
        Returns:
            Tuple of (success, method)
        """
        config = self.configs.get(user_id)
        if not config:
            return False, "no_config"
        
        if not config.enabled:
            return True, "disabled"  # 2FA not enabled, allow
        
        # Try TOTP first
        totp = TOTPGenerator(config.secret)
        if totp.verify(code):
            config.last_used = datetime.now().isoformat()
            self._save()
            return True, "totp"
        
        # Try backup code
        if allow_backup:
            available_codes = [
                c for c in config.backup_codes 
                if c not in config.used_backup_codes
            ]
            
            if BackupCodeGenerator.verify(code, available_codes):
                # Mark code as used
                normalized = code.upper().replace('-', '').replace(' ', '')
                for bc in config.backup_codes:
                    if bc.upper().replace('-', '') == normalized:
                        config.used_backup_codes.append(bc)
                        break
                
                config.last_used = datetime.now().isoformat()
                self._save()
                
                logger.info(f"✅ Backup code used for user: {user_id}")
                return True, "backup"
        
        return False, "invalid"
    
    def is_enabled(self, user_id: str) -> bool:
        """ตรวจสอบว่า 2FA เปิดใช้งานหรือไม่"""
        config = self.configs.get(user_id)
        return config.enabled if config else False
    
    def disable(self, user_id: str) -> bool:
        """ปิด 2FA"""
        config = self.configs.get(user_id)
        if not config:
            return False
        
        config.enabled = False
        self._save()
        
        logger.info(f"❌ 2FA disabled for user: {user_id}")
        return True
    
    def regenerate_backup_codes(self, user_id: str) -> Optional[List[str]]:
        """สร้าง backup codes ใหม่"""
        config = self.configs.get(user_id)
        if not config:
            return None
        
        new_codes = BackupCodeGenerator.generate()
        config.backup_codes = new_codes
        config.used_backup_codes = []
        self._save()
        
        logger.info(f"✅ Regenerated backup codes for user: {user_id}")
        return new_codes
    
    def get_status(self, user_id: str) -> Dict[str, Any]:
        """ดึงสถานะ 2FA"""
        config = self.configs.get(user_id)
        if not config:
            return {
                "configured": False,
                "enabled": False
            }
        
        return {
            "configured": True,
            "enabled": config.enabled,
            "verified_at": config.verified_at,
            "last_used": config.last_used,
            "backup_codes_remaining": len([
                c for c in config.backup_codes 
                if c not in config.used_backup_codes
            ])
        }


# ==================== Singleton Instance ====================

_tfa_instance: Optional[TwoFactorAuth] = None


def get_two_factor_auth() -> TwoFactorAuth:
    """ดึง Singleton instance ของ TwoFactorAuth"""
    global _tfa_instance
    if _tfa_instance is None:
        _tfa_instance = TwoFactorAuth()
    return _tfa_instance


# ==================== Test ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing Security Module - Two-Factor Authentication")
    print("=" * 60)
    
    # Test 1: TOTP Generation
    print("\n📤 Test 1: TOTP Generation")
    totp = TOTPGenerator()
    print(f"  Secret: {totp.secret}")
    
    code = totp.generate()
    print(f"  Current code: {code}")
    
    is_valid = totp.verify(code)
    print(f"  Verify current: {is_valid}")
    
    # Test 2: QR URI
    print("\n📤 Test 2: QR URI Generation")
    uri = totp.get_provisioning_uri("admin@dlnk.local")
    print(f"  URI: {uri[:80]}...")
    
    # Test 3: Backup Codes
    print("\n📤 Test 3: Backup Codes")
    codes = BackupCodeGenerator.generate(5)
    print(f"  Generated codes:")
    for c in codes:
        print(f"    - {c}")
    
    is_valid = BackupCodeGenerator.verify(codes[0], codes)
    print(f"  Verify first code: {is_valid}")
    
    # Test 4: Full 2FA Flow
    print("\n📤 Test 4: Full 2FA Flow")
    tfa = TwoFactorAuth()
    
    # Setup
    setup = tfa.setup("test_user")
    print(f"  Setup secret: {setup['secret'][:20]}...")
    print(f"  Backup codes: {len(setup['backup_codes'])}")
    
    # Verify setup (simulate with current code)
    test_totp = TOTPGenerator(setup['secret'])
    current_code = test_totp.generate()
    
    verified = tfa.verify_setup("test_user", current_code)
    print(f"  Setup verified: {verified}")
    
    # Verify login
    new_code = test_totp.generate()
    success, method = tfa.verify("test_user", new_code)
    print(f"  Login verified: {success} (method: {method})")
    
    # Status
    status = tfa.get_status("test_user")
    print(f"  Status: enabled={status['enabled']}, backup_remaining={status['backup_codes_remaining']}")
    
    print("\n✅ Two-Factor Authentication test completed!")
