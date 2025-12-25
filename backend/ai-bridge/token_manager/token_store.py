"""
dLNk AI Bridge - Token Storage
==============================
Secure storage for OAuth tokens with encryption.

Based on: /source-files/dlnk_core/token_harvester.py

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .encryption import TokenEncryption

logger = logging.getLogger('TokenStore')


class TokenStore:
    """
    Secure token storage with encryption
    
    Features:
    - Encrypted storage on disk
    - Token expiry tracking
    - Multiple token types support
    - Import/export functionality
    """
    
    def __init__(
        self,
        storage_path: Path = None,
        encryption_key: str = None
    ):
        """
        Initialize token store
        
        Args:
            storage_path: Directory for token storage
            encryption_key: Fernet encryption key
        """
        self.storage_path = storage_path or Path.home() / ".dlnk" / "tokens"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        key_file = self.storage_path / ".encryption_key"
        self.encryption = TokenEncryption(
            key=encryption_key,
            key_file=key_file
        )
        
        # Token data
        self._tokens: Dict[str, Dict[str, Any]] = {}
        
        # Load existing tokens
        self._load()
    
    def _get_token_file(self) -> Path:
        """Get path to encrypted token file"""
        return self.storage_path / "tokens.enc"
    
    def _load(self):
        """Load tokens from encrypted storage"""
        token_file = self._get_token_file()
        
        if not token_file.exists():
            logger.info("No existing token file found")
            return
        
        try:
            with open(token_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted = self.encryption.decrypt(encrypted_data)
            self._tokens = json.loads(decrypted)
            
            logger.info(f"Loaded {len(self._tokens)} tokens from storage")
            
        except Exception as e:
            logger.warning(f"Failed to load tokens: {e}")
            self._tokens = {}
    
    def _save(self):
        """Save tokens to encrypted storage"""
        token_file = self._get_token_file()
        
        try:
            data = json.dumps(self._tokens, indent=2)
            encrypted = self.encryption.encrypt(data)
            
            with open(token_file, 'wb') as f:
                f.write(encrypted)
            
            logger.debug("Tokens saved to storage")
            
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")
    
    def set_token(
        self,
        token_type: str,
        token: str,
        expires_in: int = 3600,
        metadata: Dict = None
    ):
        """
        Store a token
        
        Args:
            token_type: Type of token (e.g., 'access', 'refresh', 'api_key')
            token: Token value
            expires_in: Seconds until expiry
            metadata: Additional metadata
        """
        self._tokens[token_type] = {
            'token': token,
            'expires_at': time.time() + expires_in,
            'created_at': time.time(),
            'metadata': metadata or {}
        }
        
        self._save()
        logger.info(f"Stored {token_type} token (expires in {expires_in}s)")
    
    def get_token(self, token_type: str) -> Optional[str]:
        """
        Get a token if valid
        
        Args:
            token_type: Type of token to retrieve
        
        Returns:
            Token string or None if not found/expired
        """
        token_data = self._tokens.get(token_type)
        
        if not token_data:
            return None
        
        # Check expiry
        if time.time() >= token_data.get('expires_at', 0):
            logger.warning(f"{token_type} token has expired")
            return None
        
        return token_data.get('token')
    
    def get_token_data(self, token_type: str) -> Optional[Dict]:
        """
        Get full token data including metadata
        
        Args:
            token_type: Type of token
        
        Returns:
            Token data dict or None
        """
        return self._tokens.get(token_type)
    
    def is_valid(self, token_type: str) -> bool:
        """
        Check if a token is valid (exists and not expired)
        
        Args:
            token_type: Type of token
        
        Returns:
            True if valid
        """
        token_data = self._tokens.get(token_type)
        
        if not token_data:
            return False
        
        return time.time() < token_data.get('expires_at', 0)
    
    def get_expiry(self, token_type: str) -> Optional[float]:
        """
        Get token expiry timestamp
        
        Args:
            token_type: Type of token
        
        Returns:
            Expiry timestamp or None
        """
        token_data = self._tokens.get(token_type)
        return token_data.get('expires_at') if token_data else None
    
    def time_until_expiry(self, token_type: str) -> float:
        """
        Get seconds until token expires
        
        Args:
            token_type: Type of token
        
        Returns:
            Seconds until expiry (negative if expired)
        """
        expiry = self.get_expiry(token_type)
        if expiry is None:
            return -1
        return expiry - time.time()
    
    def delete_token(self, token_type: str):
        """
        Delete a token
        
        Args:
            token_type: Type of token to delete
        """
        if token_type in self._tokens:
            del self._tokens[token_type]
            self._save()
            logger.info(f"Deleted {token_type} token")
    
    def clear_all(self):
        """Delete all tokens"""
        self._tokens = {}
        self._save()
        logger.info("Cleared all tokens")
    
    def list_tokens(self) -> Dict[str, Dict]:
        """
        List all stored tokens (without actual token values)
        
        Returns:
            Dict of token types with metadata
        """
        result = {}
        
        for token_type, data in self._tokens.items():
            result[token_type] = {
                'valid': self.is_valid(token_type),
                'expires_at': data.get('expires_at'),
                'created_at': data.get('created_at'),
                'time_until_expiry': self.time_until_expiry(token_type),
                'metadata': data.get('metadata', {})
            }
        
        return result
    
    def import_from_file(self, filepath: str) -> bool:
        """
        Import tokens from JSON file
        
        Supports multiple formats:
        - Direct: {"access_token": "...", "refresh_token": "..."}
        - Nested: {"tokens": {"access_token": "...", ...}}
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            True if import successful
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Handle nested format
            if 'tokens' in data:
                data = data['tokens']
            
            # Import known token types
            if 'access_token' in data:
                self.set_token('access', data['access_token'])
            
            if 'refresh_token' in data:
                self.set_token('refresh', data['refresh_token'], expires_in=30*24*3600)
            
            if 'client_secret' in data:
                self.set_token('client_secret', data['client_secret'], expires_in=365*24*3600)
            
            if 'api_key' in data:
                self.set_token('api_key', data['api_key'], expires_in=365*24*3600)
            
            logger.info(f"Imported tokens from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import tokens: {e}")
            return False
    
    def export_to_file(self, filepath: str, include_secrets: bool = False) -> bool:
        """
        Export tokens to JSON file
        
        Args:
            filepath: Output file path
            include_secrets: Whether to include actual token values
        
        Returns:
            True if export successful
        """
        try:
            if include_secrets:
                export_data = {
                    'access_token': self.get_token('access'),
                    'refresh_token': self.get_token('refresh'),
                    'exported_at': datetime.now().isoformat()
                }
            else:
                export_data = {
                    'tokens': self.list_tokens(),
                    'exported_at': datetime.now().isoformat()
                }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported tokens to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export tokens: {e}")
            return False
