"""
dLNk AI Bridge - Token Encryption
=================================
Secure encryption for token storage using Fernet.

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import os
import base64
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger('TokenEncryption')


class TokenEncryption:
    """
    Handles encryption/decryption of tokens using Fernet symmetric encryption.
    
    Fernet guarantees that a message encrypted using it cannot be
    manipulated or read without the key.
    
    Features:
    - Automatic key generation
    - Key persistence
    - Secure token encryption/decryption
    """
    
    def __init__(self, key: Optional[str] = None, key_file: Optional[Path] = None):
        """
        Initialize encryption handler
        
        Args:
            key: Fernet key as string (base64 encoded)
            key_file: Path to key file for persistence
        """
        self.key_file = key_file
        self._fernet = None
        
        # Initialize with provided key or load/generate
        if key:
            self._init_with_key(key)
        elif key_file and key_file.exists():
            self._load_key()
        else:
            self._generate_key()
    
    def _init_with_key(self, key: str):
        """Initialize Fernet with provided key"""
        try:
            from cryptography.fernet import Fernet
            
            # Ensure key is bytes
            if isinstance(key, str):
                key = key.encode('utf-8')
            
            self._fernet = Fernet(key)
            logger.info("Encryption initialized with provided key")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def _generate_key(self):
        """Generate new Fernet key"""
        try:
            from cryptography.fernet import Fernet
            
            key = Fernet.generate_key()
            self._fernet = Fernet(key)
            
            # Save key if key_file specified
            if self.key_file:
                self._save_key(key)
            
            logger.info("Generated new encryption key")
            
        except Exception as e:
            logger.error(f"Failed to generate encryption key: {e}")
            raise
    
    def _load_key(self):
        """Load key from file"""
        try:
            from cryptography.fernet import Fernet
            
            with open(self.key_file, 'rb') as f:
                key = f.read().strip()
            
            self._fernet = Fernet(key)
            logger.info(f"Loaded encryption key from {self.key_file}")
            
        except Exception as e:
            logger.error(f"Failed to load encryption key: {e}")
            # Generate new key if load fails
            self._generate_key()
    
    def _save_key(self, key: bytes):
        """Save key to file"""
        try:
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set restrictive permissions (owner only)
            os.chmod(self.key_file, 0o600)
            
            logger.info(f"Saved encryption key to {self.key_file}")
            
        except Exception as e:
            logger.error(f"Failed to save encryption key: {e}")
    
    def encrypt(self, data: str) -> bytes:
        """
        Encrypt string data
        
        Args:
            data: String to encrypt
        
        Returns:
            Encrypted bytes
        """
        if not self._fernet:
            raise RuntimeError("Encryption not initialized")
        
        return self._fernet.encrypt(data.encode('utf-8'))
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt encrypted data
        
        Args:
            encrypted_data: Encrypted bytes
        
        Returns:
            Decrypted string
        """
        if not self._fernet:
            raise RuntimeError("Encryption not initialized")
        
        return self._fernet.decrypt(encrypted_data).decode('utf-8')
    
    def encrypt_to_string(self, data: str) -> str:
        """
        Encrypt and return as base64 string
        
        Args:
            data: String to encrypt
        
        Returns:
            Base64-encoded encrypted string
        """
        encrypted = self.encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_from_string(self, encrypted_string: str) -> str:
        """
        Decrypt from base64 string
        
        Args:
            encrypted_string: Base64-encoded encrypted string
        
        Returns:
            Decrypted string
        """
        encrypted = base64.b64decode(encrypted_string.encode('utf-8'))
        return self.decrypt(encrypted)
    
    def get_key(self) -> Optional[str]:
        """
        Get current encryption key as string
        
        Returns:
            Base64-encoded key string or None
        """
        if self._fernet:
            # Access internal key (for backup purposes only)
            return self._fernet._signing_key.hex() + self._fernet._encryption_key.hex()
        return None
    
    @staticmethod
    def generate_key_string() -> str:
        """
        Generate a new Fernet key as string
        
        Returns:
            Base64-encoded key string
        """
        from cryptography.fernet import Fernet
        return Fernet.generate_key().decode('utf-8')
    
    def is_initialized(self) -> bool:
        """Check if encryption is properly initialized"""
        return self._fernet is not None


class SimpleEncryption:
    """
    Simple XOR-based encryption for non-critical data.
    
    WARNING: This is NOT cryptographically secure!
    Use only for obfuscation, not real security.
    """
    
    def __init__(self, key: str = None):
        """
        Initialize with key
        
        Args:
            key: Encryption key (generated if not provided)
        """
        self.key = key or os.urandom(32).hex()
    
    def encrypt(self, data: str) -> str:
        """XOR encrypt and return hex string"""
        key_bytes = self.key.encode('utf-8')
        data_bytes = data.encode('utf-8')
        
        encrypted = bytes([
            data_bytes[i] ^ key_bytes[i % len(key_bytes)]
            for i in range(len(data_bytes))
        ])
        
        return encrypted.hex()
    
    def decrypt(self, encrypted_hex: str) -> str:
        """Decrypt from hex string"""
        key_bytes = self.key.encode('utf-8')
        encrypted = bytes.fromhex(encrypted_hex)
        
        decrypted = bytes([
            encrypted[i] ^ key_bytes[i % len(key_bytes)]
            for i in range(len(encrypted))
        ])
        
        return decrypted.decode('utf-8')
