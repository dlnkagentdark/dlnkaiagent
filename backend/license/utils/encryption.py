"""
Encryption Utilities
ระบบเข้ารหัสด้วย Fernet Encryption
"""

import base64
import json
from typing import Any, Optional
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

import sys
sys.path.append('..')
from config import get_config

config = get_config()


class EncryptionManager:
    """
    จัดการการเข้ารหัสและถอดรหัสข้อมูล
    ใช้ Fernet Symmetric Encryption
    """
    
    _instance = None
    _fernet = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_fernet()
        return cls._instance
    
    def _init_fernet(self):
        """Initialize Fernet with derived key"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=config.SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(config.MASTER_SECRET))
        self._fernet = Fernet(key)
    
    @property
    def fernet(self) -> Fernet:
        """Get Fernet instance"""
        return self._fernet
    
    def encrypt(self, data: Any) -> str:
        """
        เข้ารหัสข้อมูล
        
        Args:
            data: ข้อมูลที่ต้องการเข้ารหัส (dict, str, หรือ bytes)
        
        Returns:
            Encrypted string
        """
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self._fernet.encrypt(data)
        return encrypted.decode('utf-8')
    
    def decrypt(self, encrypted_data: str) -> Optional[Any]:
        """
        ถอดรหัสข้อมูล
        
        Args:
            encrypted_data: ข้อมูลที่เข้ารหัสแล้ว
        
        Returns:
            Decrypted data หรือ None ถ้าถอดรหัสไม่ได้
        """
        try:
            decrypted = self._fernet.decrypt(encrypted_data.encode('utf-8'))
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted.decode('utf-8'))
            except json.JSONDecodeError:
                return decrypted.decode('utf-8')
                
        except InvalidToken:
            return None
        except Exception:
            return None
    
    def encrypt_dict(self, data: dict) -> str:
        """เข้ารหัส dictionary"""
        return self.encrypt(data)
    
    def decrypt_dict(self, encrypted_data: str) -> Optional[dict]:
        """ถอดรหัสเป็น dictionary"""
        result = self.decrypt(encrypted_data)
        if isinstance(result, dict):
            return result
        return None
    
    @staticmethod
    def generate_key() -> bytes:
        """สร้าง Fernet key ใหม่"""
        return Fernet.generate_key()
    
    @staticmethod
    def hash_data(data: str) -> str:
        """Hash ข้อมูลด้วย SHA256"""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()


# Global instance
encryption_manager = EncryptionManager()


def encrypt(data: Any) -> str:
    """Shortcut function for encryption"""
    return encryption_manager.encrypt(data)


def decrypt(encrypted_data: str) -> Optional[Any]:
    """Shortcut function for decryption"""
    return encryption_manager.decrypt(encrypted_data)


def encrypt_string(data: str) -> str:
    """Encrypt a string (alias for encrypt)"""
    return encryption_manager.encrypt(data)


def decrypt_string(encrypted_data: str) -> Optional[str]:
    """Decrypt to string (alias for decrypt)"""
    result = encryption_manager.decrypt(encrypted_data)
    if isinstance(result, str):
        return result
    return str(result) if result else None
