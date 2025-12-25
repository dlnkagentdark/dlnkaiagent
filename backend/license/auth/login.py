"""
Login System
ระบบ Login รองรับ Offline Mode
"""

import json
import sqlite3
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

import sys
sys.path.append('..')
from config import get_config
from utils.helpers import hash_password, verify_password, generate_hex_token
from utils.encryption import encryption_manager
from .session import session_manager
from .totp import totp_manager, is_2fa_available

logger = logging.getLogger('dLNk-Login')
config = get_config()


@dataclass
class User:
    """โครงสร้างข้อมูล User"""
    user_id: str
    username: str
    email: str = ""
    role: str = "user"
    license_key: str = ""
    last_login: str = ""
    offline_until: str = ""
    has_2fa: bool = False
    totp_secret: str = ""
    
    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'license_key': self.license_key,
            'last_login': self.last_login,
            'has_2fa': self.has_2fa
        }


@dataclass
class LoginResult:
    """ผลลัพธ์การ Login"""
    success: bool
    user: Optional[User] = None
    session_id: Optional[str] = None
    error: Optional[str] = None
    offline_mode: bool = False
    requires_2fa: bool = False
    requires_password_change: bool = False


class LoginManager:
    """
    จัดการการ Login
    รองรับ Online และ Offline Mode
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.data_dir = Path(self.db_path).parent
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """สร้างตาราง users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                license_key TEXT,
                totp_secret TEXT,
                is_active INTEGER DEFAULT 1,
                must_change_password INTEGER DEFAULT 0,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TEXT,
                created_at TEXT NOT NULL,
                last_login TEXT,
                offline_until TEXT
            )
        ''')
        
        # Offline credentials table (encrypted)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS offline_credentials (
                username TEXT PRIMARY KEY,
                encrypted_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        
        conn.commit()
        conn.close()
    
    def login(
        self,
        username: str,
        password: str,
        license_key: str = None,
        totp_code: str = None,
        ip_address: str = None,
        user_agent: str = None,
        remember: bool = False
    ) -> LoginResult:
        """
        Login ด้วย username และ password
        
        Args:
            username: Username หรือ email
            password: Password
            license_key: License key (optional, ใช้สำหรับ license-based login)
            totp_code: 2FA code (ถ้าเปิดใช้งาน)
            ip_address: IP address
            user_agent: User agent
            remember: บันทึก credentials สำหรับ offline login
        
        Returns:
            LoginResult
        """
        
        # Try online login first
        try:
            result = self._online_login(
                username, password, license_key, totp_code, 
                ip_address, user_agent, remember
            )
            return result
        except Exception as e:
            logger.warning(f"Online login failed: {e}")
            # Try offline login
            return self._offline_login(username, password, license_key)
    
    def _online_login(
        self,
        username: str,
        password: str,
        license_key: str = None,
        totp_code: str = None,
        ip_address: str = None,
        user_agent: str = None,
        remember: bool = False
    ) -> LoginResult:
        """Online login"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find user
        cursor.execute('''
            SELECT user_id, username, email, password_hash, salt, role, license_key,
                   totp_secret, is_active, must_change_password, failed_attempts, locked_until
            FROM users WHERE username = ? OR email = ?
        ''', (username, username))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return LoginResult(success=False, error="User not found")
        
        (user_id, db_username, email, password_hash, salt, role, db_license_key,
         totp_secret, is_active, must_change_password, failed_attempts, locked_until) = row
        
        # Check if locked
        if locked_until:
            lock_time = datetime.fromisoformat(locked_until)
            if datetime.now() < lock_time:
                conn.close()
                return LoginResult(
                    success=False,
                    error=f"Account locked until {locked_until}"
                )
        
        # Check if active
        if not is_active:
            conn.close()
            return LoginResult(success=False, error="Account is disabled")
        
        # Verify password
        if not verify_password(password, salt, password_hash):
            self._increment_failed_attempts(cursor, user_id)
            conn.commit()
            conn.close()
            return LoginResult(success=False, error="Invalid password")
        
        # Check 2FA
        if totp_secret and is_2fa_available():
            if not totp_code:
                conn.close()
                return LoginResult(
                    success=False,
                    requires_2fa=True,
                    error="2FA code required"
                )
            
            if not totp_manager.verify_code(totp_secret, totp_code):
                conn.close()
                return LoginResult(success=False, error="Invalid 2FA code")
        
        # Reset failed attempts
        cursor.execute('''
            UPDATE users SET failed_attempts = 0, locked_until = NULL, last_login = ?
            WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        # Use provided license key or stored one
        final_license_key = license_key or db_license_key
        
        # Update offline_until
        offline_until = (datetime.now() + timedelta(days=config.OFFLINE_GRACE_DAYS)).isoformat()
        cursor.execute('''
            UPDATE users SET offline_until = ? WHERE user_id = ?
        ''', (offline_until, user_id))
        
        conn.commit()
        conn.close()
        
        # Create user object
        user = User(
            user_id=user_id,
            username=db_username,
            email=email,
            role=role,
            license_key=final_license_key,
            last_login=datetime.now().isoformat(),
            offline_until=offline_until,
            has_2fa=bool(totp_secret)
        )
        
        # Create session
        session_id = session_manager.create_session(
            user_id=user_id,
            username=db_username,
            license_key=final_license_key,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Save for offline login if remember is True
        if remember:
            self._save_offline_credentials(user, password)
        
        return LoginResult(
            success=True,
            user=user,
            session_id=session_id,
            requires_password_change=bool(must_change_password)
        )
    
    def _offline_login(
        self,
        username: str,
        password: str,
        license_key: str = None
    ) -> LoginResult:
        """Offline login using saved credentials"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT encrypted_data, expires_at FROM offline_credentials WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return LoginResult(
                success=False,
                error="No saved credentials for offline login"
            )
        
        encrypted_data, expires_at = row
        
        # Check expiration
        if datetime.now() > datetime.fromisoformat(expires_at):
            return LoginResult(
                success=False,
                error="Offline credentials expired. Please connect to internet."
            )
        
        # Decrypt credentials
        decrypted = encryption_manager.decrypt(encrypted_data)
        if not decrypted:
            return LoginResult(
                success=False,
                error="Failed to decrypt offline credentials"
            )
        
        # Verify password
        stored_hash = decrypted.get('password_hash')
        stored_salt = decrypted.get('salt')
        
        if not verify_password(password, stored_salt, stored_hash):
            return LoginResult(success=False, error="Invalid password")
        
        # Create user object
        user = User(
            user_id=decrypted.get('user_id'),
            username=decrypted.get('username'),
            email=decrypted.get('email', ''),
            role=decrypted.get('role', 'user'),
            license_key=license_key or decrypted.get('license_key', ''),
            last_login=datetime.now().isoformat(),
            offline_until=expires_at
        )
        
        # Create offline session
        session_id = session_manager.create_session(
            user_id=user.user_id,
            username=user.username,
            license_key=user.license_key,
            offline_mode=True
        )
        
        logger.info(f"Offline login successful for {username}")
        
        return LoginResult(
            success=True,
            user=user,
            session_id=session_id,
            offline_mode=True
        )
    
    def _save_offline_credentials(self, user: User, password: str):
        """บันทึก credentials สำหรับ offline login"""
        
        salt = generate_hex_token(16)
        password_hash = hash_password(password, salt)
        
        data = {
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'license_key': user.license_key,
            'password_hash': password_hash,
            'salt': salt
        }
        
        encrypted = encryption_manager.encrypt(data)
        expires_at = (datetime.now() + timedelta(days=config.OFFLINE_GRACE_DAYS)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO offline_credentials (username, encrypted_data, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (user.username, encrypted, datetime.now().isoformat(), expires_at))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Saved offline credentials for {user.username}")
    
    def _increment_failed_attempts(self, cursor, user_id: str):
        """เพิ่มจำนวนครั้งที่ login ผิด"""
        cursor.execute('SELECT failed_attempts FROM users WHERE user_id = ?', (user_id,))
        current = cursor.fetchone()[0] or 0
        new_count = current + 1
        
        if new_count >= config.MAX_LOGIN_ATTEMPTS:
            lock_until = datetime.now() + timedelta(minutes=config.LOCKOUT_DURATION_MINUTES)
            cursor.execute('''
                UPDATE users SET failed_attempts = ?, locked_until = ? WHERE user_id = ?
            ''', (new_count, lock_until.isoformat(), user_id))
            logger.warning(f"User {user_id} locked until {lock_until}")
        else:
            cursor.execute('UPDATE users SET failed_attempts = ? WHERE user_id = ?', (new_count, user_id))
    
    def logout(self, session_id: str) -> bool:
        """Logout และยกเลิก session"""
        return session_manager.invalidate_session(session_id)
    
    def logout_all(self, user_id: str) -> int:
        """Logout จากทุกอุปกรณ์"""
        return session_manager.invalidate_user_sessions(user_id)
    
    def validate_session(self, session_id: str) -> Optional[dict]:
        """ตรวจสอบ session"""
        return session_manager.validate_session(session_id)
    
    def create_user(
        self,
        username: str,
        password: str,
        email: str = None,
        role: str = "user",
        license_key: str = None
    ) -> Tuple[bool, str, Optional[User]]:
        """
        สร้าง user ใหม่
        
        Returns:
            Tuple of (success, message, user)
        """
        from utils.helpers import validate_password
        
        # Validate password
        is_valid, error = validate_password(password)
        if not is_valid:
            return False, error, None
        
        salt = generate_hex_token(16)
        password_hash = hash_password(password, salt)
        user_id = generate_hex_token(8)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, salt, role, license_key, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, salt, role, license_key, datetime.now().isoformat()))
            
            conn.commit()
            
            user = User(
                user_id=user_id,
                username=username,
                email=email or "",
                role=role,
                license_key=license_key or ""
            )
            
            logger.info(f"User created: {username}")
            return True, "User created successfully", user
            
        except sqlite3.IntegrityError:
            return False, f"Username '{username}' already exists", None
        finally:
            conn.close()
    
    def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """เปลี่ยน password"""
        from utils.helpers import validate_password
        
        # Validate new password
        is_valid, error = validate_password(new_password)
        if not is_valid:
            return False, error
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verify old password
        cursor.execute('SELECT password_hash, salt FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, "User not found"
        
        if not verify_password(old_password, row[1], row[0]):
            conn.close()
            return False, "Current password is incorrect"
        
        # Update password
        new_salt = generate_hex_token(16)
        new_hash = hash_password(new_password, new_salt)
        
        cursor.execute('''
            UPDATE users SET password_hash = ?, salt = ?, must_change_password = 0 WHERE user_id = ?
        ''', (new_hash, new_salt, user_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Password changed for user {user_id}")
        return True, "Password changed successfully"


# Global instance
login_manager = LoginManager()
