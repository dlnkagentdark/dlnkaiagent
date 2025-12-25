#!/usr/bin/env python3
"""
Log Encryption
เข้ารหัส Log Files
"""

import os
import gzip
import base64
import hashlib
import secrets
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterator
from dataclasses import dataclass
import json

logger = logging.getLogger('LogEncryption')


@dataclass
class EncryptedLogEntry:
    """โครงสร้างข้อมูล Log Entry ที่เข้ารหัส"""
    timestamp: str
    encrypted_data: str
    salt: str
    entry_type: str = "log"


class LogEncryption:
    """
    Encrypt and decrypt log entries
    """
    
    def __init__(
        self,
        key: bytes = None,
        key_file: str = None
    ):
        self.key_file = Path(key_file) if key_file else Path.home() / ".dlnk-ide" / ".log_key"
        self.key = key or self._load_or_generate_key()
        
        # Try to use cryptography library
        self._fernet = None
        try:
            from cryptography.fernet import Fernet
            fernet_key = base64.urlsafe_b64encode(self.key[:32])
            self._fernet = Fernet(fernet_key)
        except ImportError:
            pass
    
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
            return key
    
    def encrypt_entry(
        self,
        data: str,
        entry_type: str = "log"
    ) -> EncryptedLogEntry:
        """
        Encrypt a log entry
        
        Args:
            data: Log data to encrypt
            entry_type: Type of log entry
        
        Returns:
            EncryptedLogEntry object
        """
        salt = secrets.token_bytes(16)
        
        if self._fernet:
            encrypted = self._fernet.encrypt(data.encode())
            encrypted_data = base64.b64encode(encrypted).decode()
        else:
            encrypted_data = self._fallback_encrypt(data, salt)
        
        return EncryptedLogEntry(
            timestamp=datetime.now().isoformat(),
            encrypted_data=encrypted_data,
            salt=base64.b64encode(salt).decode(),
            entry_type=entry_type
        )
    
    def decrypt_entry(self, entry: EncryptedLogEntry) -> Optional[str]:
        """
        Decrypt a log entry
        
        Args:
            entry: EncryptedLogEntry object
        
        Returns:
            Decrypted log data or None
        """
        salt = base64.b64decode(entry.salt)
        
        try:
            if self._fernet:
                encrypted = base64.b64decode(entry.encrypted_data)
                decrypted = self._fernet.decrypt(encrypted)
                return decrypted.decode()
            else:
                return self._fallback_decrypt(entry.encrypted_data, salt)
        except Exception as e:
            logger.error(f"Log decryption failed: {e}")
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
    
    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt a dictionary (for JSON logs)"""
        json_data = json.dumps(data, ensure_ascii=False)
        entry = self.encrypt_entry(json_data, "dict")
        
        return {
            '_encrypted': True,
            'timestamp': entry.timestamp,
            'data': entry.encrypted_data,
            'salt': entry.salt
        }
    
    def decrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt a dictionary"""
        if not data.get('_encrypted'):
            return data
        
        entry = EncryptedLogEntry(
            timestamp=data.get('timestamp', ''),
            encrypted_data=data['data'],
            salt=data['salt'],
            entry_type='dict'
        )
        
        decrypted = self.decrypt_entry(entry)
        if decrypted:
            return json.loads(decrypted)
        return {}


class EncryptedLogFile:
    """
    Manage encrypted log files
    """
    
    def __init__(
        self,
        file_path: str,
        encryption: LogEncryption = None,
        compress: bool = True,
        max_size_mb: int = 100
    ):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.encryption = encryption or LogEncryption()
        self.compress = compress
        self.max_size_mb = max_size_mb
        
        # Buffer for batch writing
        self._buffer: List[str] = []
        self._buffer_size = 0
        self._max_buffer_size = 1024 * 1024  # 1MB
    
    def write(self, data: str, entry_type: str = "log"):
        """
        Write encrypted log entry
        
        Args:
            data: Log data
            entry_type: Type of entry
        """
        entry = self.encryption.encrypt_entry(data, entry_type)
        
        line = json.dumps({
            'timestamp': entry.timestamp,
            'type': entry.entry_type,
            'data': entry.encrypted_data,
            'salt': entry.salt
        }, ensure_ascii=False)
        
        self._buffer.append(line)
        self._buffer_size += len(line)
        
        if self._buffer_size >= self._max_buffer_size:
            self.flush()
    
    def write_dict(self, data: Dict[str, Any]):
        """Write encrypted dictionary"""
        self.write(json.dumps(data, ensure_ascii=False), "dict")
    
    def flush(self):
        """Flush buffer to file"""
        if not self._buffer:
            return
        
        # Check file size and rotate if needed
        if self.file_path.exists():
            size_mb = self.file_path.stat().st_size / (1024 * 1024)
            if size_mb >= self.max_size_mb:
                self._rotate()
        
        # Write buffer
        mode = 'ab' if self.compress else 'a'
        
        if self.compress:
            with gzip.open(str(self.file_path) + '.gz', mode) as f:
                for line in self._buffer:
                    f.write((line + '\n').encode())
        else:
            with open(self.file_path, 'a', encoding='utf-8') as f:
                for line in self._buffer:
                    f.write(line + '\n')
        
        self._buffer.clear()
        self._buffer_size = 0
    
    def _rotate(self):
        """Rotate log file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.compress:
            old_path = str(self.file_path) + '.gz'
            new_path = str(self.file_path) + f'.{timestamp}.gz'
        else:
            old_path = str(self.file_path)
            new_path = str(self.file_path) + f'.{timestamp}'
        
        if Path(old_path).exists():
            os.rename(old_path, new_path)
            logger.info(f"Log rotated: {new_path}")
    
    def read(self, limit: int = None) -> Iterator[Dict[str, Any]]:
        """
        Read and decrypt log entries
        
        Args:
            limit: Maximum entries to read
        
        Yields:
            Decrypted log entries
        """
        count = 0
        
        if self.compress:
            file_path = str(self.file_path) + '.gz'
            if not Path(file_path).exists():
                return
            
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    if limit and count >= limit:
                        break
                    
                    entry = self._decrypt_line(line)
                    if entry:
                        yield entry
                        count += 1
        else:
            if not self.file_path.exists():
                return
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if limit and count >= limit:
                        break
                    
                    entry = self._decrypt_line(line)
                    if entry:
                        yield entry
                        count += 1
    
    def _decrypt_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Decrypt a single line"""
        try:
            data = json.loads(line.strip())
            
            entry = EncryptedLogEntry(
                timestamp=data['timestamp'],
                encrypted_data=data['data'],
                salt=data['salt'],
                entry_type=data.get('type', 'log')
            )
            
            decrypted = self.encryption.decrypt_entry(entry)
            if decrypted:
                result = {
                    'timestamp': entry.timestamp,
                    'type': entry.entry_type,
                }
                
                if entry.entry_type == 'dict':
                    result['data'] = json.loads(decrypted)
                else:
                    result['data'] = decrypted
                
                return result
            
        except Exception as e:
            logger.debug(f"Failed to decrypt line: {e}")
        
        return None
    
    def search(
        self,
        keyword: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search decrypted logs for keyword
        
        Args:
            keyword: Keyword to search
            limit: Maximum results
        
        Returns:
            List of matching entries
        """
        results = []
        
        for entry in self.read():
            if limit and len(results) >= limit:
                break
            
            data_str = str(entry.get('data', ''))
            if keyword.lower() in data_str.lower():
                results.append(entry)
        
        return results
    
    def close(self):
        """Close and flush"""
        self.flush()


class EncryptedLogHandler(logging.Handler):
    """
    Logging handler that encrypts log entries
    """
    
    def __init__(
        self,
        file_path: str,
        encryption: LogEncryption = None,
        level: int = logging.INFO
    ):
        super().__init__(level)
        self.log_file = EncryptedLogFile(file_path, encryption)
    
    def emit(self, record: logging.LogRecord):
        """Emit encrypted log record"""
        try:
            msg = self.format(record)
            
            entry = {
                'level': record.levelname,
                'logger': record.name,
                'message': msg,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            self.log_file.write_dict(entry)
            
        except Exception:
            self.handleError(record)
    
    def close(self):
        """Close handler"""
        self.log_file.close()
        super().close()
