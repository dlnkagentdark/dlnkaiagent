#!/usr/bin/env python3
"""
Config Encryption
เข้ารหัสไฟล์ Configuration
"""

import os
import json
import base64
import hashlib
import secrets
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger('ConfigEncryption')


@dataclass
class EncryptedConfig:
    """โครงสร้างข้อมูล Config ที่เข้ารหัส"""
    version: int
    encrypted_data: str
    salt: str
    checksum: str


class ConfigEncryption:
    """
    Encrypt and decrypt configuration files
    """
    
    VERSION = 1
    
    def __init__(
        self,
        key: bytes = None,
        key_file: str = None
    ):
        self.key_file = Path(key_file) if key_file else Path.home() / ".dlnk-ide" / ".config_key"
        self.key = key or self._load_or_generate_key()
        
        # Try to use cryptography library
        self._fernet = None
        try:
            from cryptography.fernet import Fernet
            fernet_key = base64.urlsafe_b64encode(self.key[:32])
            self._fernet = Fernet(fernet_key)
        except ImportError:
            logger.warning("cryptography library not available")
    
    def _load_or_generate_key(self) -> bytes:
        """Load existing key or generate new one"""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = secrets.token_bytes(32)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)
            logger.info("Generated new config encryption key")
            return key
    
    def _compute_checksum(self, data: str) -> str:
        """Compute checksum of data"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def encrypt_config(self, config: Dict[str, Any]) -> EncryptedConfig:
        """
        Encrypt configuration dictionary
        
        Args:
            config: Configuration dictionary
        
        Returns:
            EncryptedConfig object
        """
        # Convert to JSON
        json_data = json.dumps(config, sort_keys=True)
        checksum = self._compute_checksum(json_data)
        
        salt = secrets.token_bytes(16)
        
        if self._fernet:
            encrypted = self._fernet.encrypt(json_data.encode())
            encrypted_data = base64.b64encode(encrypted).decode()
        else:
            encrypted_data = self._fallback_encrypt(json_data, salt)
        
        return EncryptedConfig(
            version=self.VERSION,
            encrypted_data=encrypted_data,
            salt=base64.b64encode(salt).decode(),
            checksum=checksum
        )
    
    def decrypt_config(self, encrypted: EncryptedConfig) -> Optional[Dict[str, Any]]:
        """
        Decrypt configuration
        
        Args:
            encrypted: EncryptedConfig object
        
        Returns:
            Configuration dictionary or None if invalid
        """
        salt = base64.b64decode(encrypted.salt)
        
        try:
            if self._fernet:
                encrypted_bytes = base64.b64decode(encrypted.encrypted_data)
                decrypted = self._fernet.decrypt(encrypted_bytes)
                json_data = decrypted.decode()
            else:
                json_data = self._fallback_decrypt(encrypted.encrypted_data, salt)
            
            # Verify checksum
            if self._compute_checksum(json_data) != encrypted.checksum:
                logger.error("Config checksum mismatch")
                return None
            
            return json.loads(json_data)
            
        except Exception as e:
            logger.error(f"Config decryption failed: {e}")
            return None
    
    def _fallback_encrypt(self, data: str, salt: bytes) -> str:
        """Fallback encryption"""
        derived = hashlib.pbkdf2_hmac('sha256', self.key, salt, 100000)
        data_bytes = data.encode()
        encrypted = bytes(a ^ b for a, b in zip(data_bytes, derived * (len(data_bytes) // len(derived) + 1)))
        return base64.b64encode(encrypted).decode()
    
    def _fallback_decrypt(self, encrypted_data: str, salt: bytes) -> str:
        """Fallback decryption"""
        derived = hashlib.pbkdf2_hmac('sha256', self.key, salt, 100000)
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = bytes(a ^ b for a, b in zip(encrypted_bytes, derived * (len(encrypted_bytes) // len(derived) + 1)))
        return decrypted.decode()
    
    def save_encrypted_config(
        self,
        config: Dict[str, Any],
        file_path: str
    ):
        """
        Save encrypted config to file
        
        Args:
            config: Configuration dictionary
            file_path: Path to save encrypted config
        """
        encrypted = self.encrypt_config(config)
        
        data = {
            'version': encrypted.version,
            'encrypted_data': encrypted.encrypted_data,
            'salt': encrypted.salt,
            'checksum': encrypted.checksum
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        os.chmod(file_path, 0o600)
        logger.info(f"Encrypted config saved to {file_path}")
    
    def load_encrypted_config(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load encrypted config from file
        
        Args:
            file_path: Path to encrypted config file
        
        Returns:
            Configuration dictionary or None if invalid
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            encrypted = EncryptedConfig(
                version=data['version'],
                encrypted_data=data['encrypted_data'],
                salt=data['salt'],
                checksum=data['checksum']
            )
            
            return self.decrypt_config(encrypted)
            
        except Exception as e:
            logger.error(f"Failed to load encrypted config: {e}")
            return None


class SecureConfigManager:
    """
    Manage secure configuration files
    """
    
    def __init__(
        self,
        config_dir: str = None,
        encryption: ConfigEncryption = None
    ):
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".dlnk-ide" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.encryption = encryption or ConfigEncryption()
        
        # Cache
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def save(self, name: str, config: Dict[str, Any], encrypt: bool = True):
        """
        Save configuration
        
        Args:
            name: Configuration name
            config: Configuration dictionary
            encrypt: Whether to encrypt
        """
        file_path = self.config_dir / f"{name}.{'enc' if encrypt else 'json'}"
        
        if encrypt:
            self.encryption.save_encrypted_config(config, str(file_path))
        else:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        self._cache[name] = config
        logger.info(f"Config saved: {name}")
    
    def load(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Load configuration
        
        Args:
            name: Configuration name
        
        Returns:
            Configuration dictionary or None
        """
        # Check cache
        if name in self._cache:
            return self._cache[name]
        
        # Try encrypted first
        enc_path = self.config_dir / f"{name}.enc"
        if enc_path.exists():
            config = self.encryption.load_encrypted_config(str(enc_path))
            if config:
                self._cache[name] = config
                return config
        
        # Try plain JSON
        json_path = self.config_dir / f"{name}.json"
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    config = json.load(f)
                self._cache[name] = config
                return config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        return None
    
    def delete(self, name: str) -> bool:
        """Delete configuration"""
        deleted = False
        
        for ext in ['enc', 'json']:
            path = self.config_dir / f"{name}.{ext}"
            if path.exists():
                path.unlink()
                deleted = True
        
        self._cache.pop(name, None)
        
        if deleted:
            logger.info(f"Config deleted: {name}")
        
        return deleted
    
    def list_configs(self) -> list:
        """List available configurations"""
        configs = set()
        
        for path in self.config_dir.glob("*"):
            if path.suffix in ['.enc', '.json']:
                configs.add(path.stem)
        
        return sorted(configs)
    
    def clear_cache(self):
        """Clear configuration cache"""
        self._cache.clear()
    
    def get(self, name: str, key: str, default: Any = None) -> Any:
        """
        Get a specific key from configuration
        
        Args:
            name: Configuration name
            key: Key to get (supports dot notation)
            default: Default value if not found
        """
        config = self.load(name)
        if not config:
            return default
        
        # Support dot notation
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, name: str, key: str, value: Any, encrypt: bool = True):
        """
        Set a specific key in configuration
        
        Args:
            name: Configuration name
            key: Key to set (supports dot notation)
            value: Value to set
            encrypt: Whether to encrypt when saving
        """
        config = self.load(name) or {}
        
        # Support dot notation
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        
        self.save(name, config, encrypt)
