#!/usr/bin/env python3
"""
dLNk License System
ระบบจัดการ License Key และ User Authentication แบบครบวงจร
รวมทั้งระบบเข้ารหัสแบบเดิมและระบบฐานข้อมูลใหม่
"""

import os
import json
import sqlite3
import hashlib
import secrets
import datetime
import base64
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Cryptography imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    os.system("pip3 install cryptography -q")
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-License')

# ==================== ENCRYPTION SYSTEM (Original) ====================

# MASTER SECRET KEY
MASTER_SECRET = b"dLNk-AI-TOP-SECRET-MASTER-KEY-2025"
SALT = b"dlnk-static-salt"

def get_fernet():
    """Derive the Fernet key from the Master Secret."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(MASTER_SECRET))
    return Fernet(key)


def generate_encrypted_license(days_valid=30, owner="Unknown", features=None):
    """
    Generates an encrypted license key string.
    """
    f = get_fernet()
    
    if features is None:
        features = ["dark_mode", "ai_chat", "code_assist"]
    
    expiry_date = (datetime.datetime.now() + datetime.timedelta(days=days_valid)).strftime("%Y-%m-%d")
    
    data = {
        "owner": owner,
        "expiry": expiry_date,
        "features": features,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    json_data = json.dumps(data).encode('utf-8')
    token = f.encrypt(json_data)
    
    return token.decode('utf-8')


def validate_encrypted_license(license_key_str):
    """
    Validates an encrypted license key.
    Returns: (is_valid, message, data_dict)
    """
    f = get_fernet()
    
    try:
        decrypted_data = f.decrypt(license_key_str.encode('utf-8'))
        data = json.loads(decrypted_data)
        
        expiry_str = data.get("expiry")
        if not expiry_str:
            return False, "Invalid License Format: No expiry date", {}
            
        expiry_date = datetime.datetime.strptime(expiry_str, "%Y-%m-%d")
        if datetime.datetime.now() > expiry_date:
            return False, f"License Expired on {expiry_str}", data
            
        return True, "License Valid", data
        
    except Exception as e:
        return False, f"Invalid License Key: {str(e)}", {}


# ==================== DATABASE SYSTEM (New) ====================

class LicenseType(Enum):
    """License Types"""
    TRIAL = "trial"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class LicenseStatus(Enum):
    """License Status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"


@dataclass
class License:
    """License Data Structure"""
    key: str
    user_id: str
    license_type: LicenseType
    status: LicenseStatus
    hwid: str
    created_at: str
    expires_at: str
    max_devices: int = 1
    features: List[str] = None
    encrypted_key: str = None  # Encrypted version for verification
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
            
    def is_valid(self) -> bool:
        """Check if license is valid"""
        if self.status != LicenseStatus.ACTIVE:
            return False
        if datetime.datetime.fromisoformat(self.expires_at) < datetime.datetime.now():
            return False
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "key": self.key,
            "user_id": self.user_id,
            "license_type": self.license_type.value,
            "status": self.status.value,
            "hwid": self.hwid,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "max_devices": self.max_devices,
            "features": self.features
        }


@dataclass
class User:
    """User Data Structure"""
    user_id: str
    username: str
    email: str
    role: str  # 'user', 'admin', 'superadmin'
    created_at: str
    last_login: str = None
    telegram_id: str = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "telegram_id": self.telegram_id
        }


class DLNKLicenseSystem:
    """
    dLNk License System
    ระบบจัดการ License แบบครบวงจร
    """
    
    def __init__(self, db_path: str = "dlnk_licenses.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create licenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                key TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                license_type TEXT NOT NULL,
                status TEXT NOT NULL,
                hwid TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                max_devices INTEGER DEFAULT 1,
                features TEXT,
                encrypted_key TEXT
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT,
                role TEXT DEFAULT 'user',
                created_at TEXT NOT NULL,
                last_login TEXT,
                telegram_id TEXT
            )
        ''')
        
        # Create activations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                hwid TEXT NOT NULL,
                device_name TEXT,
                activated_at TEXT NOT NULL,
                last_seen TEXT,
                ip_address TEXT
            )
        ''')
        
        # Create activity_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                license_key TEXT,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Create admin user if not exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            admin_id = secrets.token_hex(8)
            admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, role, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_id, "admin", "admin@dlnk.local", admin_pass, "admin", 
                  datetime.datetime.now().isoformat()))
            logger.info("Default admin user created (username: admin, password: admin123)")
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
        
    def generate_license_key(self, prefix: str = "DLNK") -> str:
        """Generate a new license key"""
        segments = [secrets.token_hex(2).upper() for _ in range(4)]
        return f"{prefix}-{'-'.join(segments)}"
        
    def create_license(
        self,
        user_id: str,
        license_type: LicenseType = LicenseType.BASIC,
        duration_days: int = 30,
        max_devices: int = 1,
        features: List[str] = None,
        owner_name: str = "User"
    ) -> License:
        """Create a new license"""
        key = self.generate_license_key()
        created_at = datetime.datetime.now().isoformat()
        expires_at = (datetime.datetime.now() + datetime.timedelta(days=duration_days)).isoformat()
        
        if features is None:
            features = self._get_default_features(license_type)
            
        # Generate encrypted key for verification
        encrypted_key = generate_encrypted_license(
            days_valid=duration_days,
            owner=owner_name,
            features=features
        )
            
        license_obj = License(
            key=key,
            user_id=user_id,
            license_type=license_type,
            status=LicenseStatus.ACTIVE,
            hwid="",
            created_at=created_at,
            expires_at=expires_at,
            max_devices=max_devices,
            features=features,
            encrypted_key=encrypted_key
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO licenses (key, user_id, license_type, status, hwid, created_at, expires_at, max_devices, features, encrypted_key)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            license_obj.key,
            license_obj.user_id,
            license_obj.license_type.value,
            license_obj.status.value,
            license_obj.hwid,
            license_obj.created_at,
            license_obj.expires_at,
            license_obj.max_devices,
            json.dumps(license_obj.features),
            license_obj.encrypted_key
        ))
        
        # Log activity
        self._log_activity(cursor, user_id, key, "license_created", 
                          f"Created {license_type.value} license for {duration_days} days")
        
        conn.commit()
        conn.close()
        
        logger.info(f"License created: {key} for user {user_id}")
        return license_obj
        
    def _get_default_features(self, license_type: LicenseType) -> List[str]:
        """Get default features for license type"""
        features_map = {
            LicenseType.TRIAL: ["ai_chat", "basic_code_assist"],
            LicenseType.BASIC: ["ai_chat", "code_assist", "dark_mode"],
            LicenseType.PRO: ["ai_chat", "code_assist", "dark_mode", "advanced_ai", "priority_support"],
            LicenseType.ENTERPRISE: ["ai_chat", "code_assist", "dark_mode", "advanced_ai", "priority_support", "custom_branding", "api_access"],
            LicenseType.ADMIN: ["all_features", "admin_panel", "user_management", "license_management"]
        }
        return features_map.get(license_type, [])
        
    def _log_activity(self, cursor, user_id: str, license_key: str, action: str, details: str, ip: str = None):
        """Log activity"""
        cursor.execute('''
            INSERT INTO activity_logs (user_id, license_key, action, details, ip_address, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, license_key, action, details, ip, datetime.datetime.now().isoformat()))
        
    def verify_license(self, key: str, hwid: str = None, ip: str = None) -> Tuple[bool, str, Optional[License]]:
        """
        Verify a license key (supports both simple key and encrypted key)
        Returns: (is_valid, message, license_object)
        """
        # First try to verify as encrypted key
        is_encrypted_valid, enc_msg, enc_data = validate_encrypted_license(key)
        if is_encrypted_valid:
            # Create a temporary license object from encrypted data
            temp_license = License(
                key=key[:20] + "...",  # Truncated for display
                user_id="encrypted",
                license_type=LicenseType.BASIC,
                status=LicenseStatus.ACTIVE,
                hwid=hwid or "",
                created_at=enc_data.get("created_at", ""),
                expires_at=enc_data.get("expiry", "") + "T23:59:59",
                features=enc_data.get("features", [])
            )
            return True, "Encrypted license valid", temp_license
        
        # Try to verify as database key
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM licenses WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, "License key not found", None
            
        license_obj = License(
            key=row[0],
            user_id=row[1],
            license_type=LicenseType(row[2]),
            status=LicenseStatus(row[3]),
            hwid=row[4],
            created_at=row[5],
            expires_at=row[6],
            max_devices=row[7],
            features=json.loads(row[8]) if row[8] else [],
            encrypted_key=row[9] if len(row) > 9 else None
        )
        
        # Check status
        if license_obj.status != LicenseStatus.ACTIVE:
            self._log_activity(cursor, license_obj.user_id, key, "verify_failed", 
                              f"License is {license_obj.status.value}", ip)
            conn.commit()
            conn.close()
            return False, f"License is {license_obj.status.value}", license_obj
            
        # Check expiration
        if datetime.datetime.fromisoformat(license_obj.expires_at) < datetime.datetime.now():
            cursor.execute('UPDATE licenses SET status = ? WHERE key = ?', 
                          (LicenseStatus.EXPIRED.value, key))
            self._log_activity(cursor, license_obj.user_id, key, "license_expired", 
                              "License has expired", ip)
            conn.commit()
            conn.close()
            return False, "License has expired", license_obj
            
        # Check HWID binding
        if hwid:
            if license_obj.hwid and license_obj.hwid != hwid:
                cursor.execute('SELECT COUNT(*) FROM activations WHERE license_key = ?', (key,))
                activation_count = cursor.fetchone()[0]
                
                if activation_count >= license_obj.max_devices:
                    self._log_activity(cursor, license_obj.user_id, key, "device_limit", 
                                      f"Max devices exceeded ({activation_count}/{license_obj.max_devices})", ip)
                    conn.commit()
                    conn.close()
                    return False, "Maximum devices exceeded", license_obj
                    
            self._record_activation(cursor, key, hwid, ip)
            
            if not license_obj.hwid:
                cursor.execute('UPDATE licenses SET hwid = ? WHERE key = ?', (hwid, key))
                
        self._log_activity(cursor, license_obj.user_id, key, "verify_success", 
                          "License verified successfully", ip)
        conn.commit()
        conn.close()
        
        return True, "License is valid", license_obj
        
    def _record_activation(self, cursor, key: str, hwid: str, ip: str = None):
        """Record device activation"""
        now = datetime.datetime.now().isoformat()
        
        cursor.execute('''
            SELECT id FROM activations WHERE license_key = ? AND hwid = ?
        ''', (key, hwid))
        
        if cursor.fetchone():
            cursor.execute('''
                UPDATE activations SET last_seen = ?, ip_address = ?
                WHERE license_key = ? AND hwid = ?
            ''', (now, ip, key, hwid))
        else:
            cursor.execute('''
                INSERT INTO activations (license_key, hwid, activated_at, last_seen, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (key, hwid, now, now, ip))
            
    def create_user(
        self,
        username: str,
        email: str = None,
        password: str = None,
        role: str = "user",
        telegram_id: str = None
    ) -> User:
        """Create a new user"""
        user_id = secrets.token_hex(8)
        created_at = datetime.datetime.now().isoformat()
        
        password_hash = None
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            created_at=created_at,
            telegram_id=telegram_id
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, role, created_at, telegram_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, role, created_at, telegram_id))
            
            self._log_activity(cursor, user_id, None, "user_created", 
                              f"User {username} created with role {role}")
            
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Username '{username}' already exists")
        
        conn.close()
        
        logger.info(f"User created: {username} ({user_id})")
        return user
        
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[User]]:
        """Authenticate user with username and password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False, None
            
        # Update last login
        cursor.execute('UPDATE users SET last_login = ? WHERE user_id = ?',
                      (datetime.datetime.now().isoformat(), row[0]))
        conn.commit()
        conn.close()
        
        user = User(
            user_id=row[0],
            username=row[1],
            email=row[2],
            role=row[4],
            created_at=row[5],
            last_login=row[6],
            telegram_id=row[7]
        )
        
        return True, user
        
    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Get user by Telegram ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return User(
            user_id=row[0],
            username=row[1],
            email=row[2],
            role=row[4],
            created_at=row[5],
            last_login=row[6],
            telegram_id=row[7]
        )
        
    def get_all_licenses(self) -> List[License]:
        """Get all licenses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM licenses ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        licenses = []
        for row in rows:
            licenses.append(License(
                key=row[0],
                user_id=row[1],
                license_type=LicenseType(row[2]),
                status=LicenseStatus(row[3]),
                hwid=row[4],
                created_at=row[5],
                expires_at=row[6],
                max_devices=row[7],
                features=json.loads(row[8]) if row[8] else [],
                encrypted_key=row[9] if len(row) > 9 else None
            ))
            
        return licenses
        
    def get_all_users(self) -> List[User]:
        """Get all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append(User(
                user_id=row[0],
                username=row[1],
                email=row[2],
                role=row[4],
                created_at=row[5],
                last_login=row[6],
                telegram_id=row[7]
            ))
            
        return users
        
    def revoke_license(self, key: str) -> bool:
        """Revoke a license"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT user_id FROM licenses WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
            
        cursor.execute('UPDATE licenses SET status = ? WHERE key = ?',
                      (LicenseStatus.REVOKED.value, key))
        
        self._log_activity(cursor, row[0], key, "license_revoked", "License revoked by admin")
        
        conn.commit()
        conn.close()
        
        logger.info(f"License revoked: {key}")
        return True
        
    def extend_license(self, key: str, days: int) -> bool:
        """Extend license expiration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT expires_at, user_id FROM licenses WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
            
        current_expiry = datetime.datetime.fromisoformat(row[0])
        new_expiry = current_expiry + datetime.timedelta(days=days)
        
        cursor.execute('UPDATE licenses SET expires_at = ?, status = ? WHERE key = ?',
                      (new_expiry.isoformat(), LicenseStatus.ACTIVE.value, key))
        
        self._log_activity(cursor, row[1], key, "license_extended", 
                          f"Extended by {days} days to {new_expiry.date()}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"License extended: {key} by {days} days")
        return True
        
    def get_license_stats(self) -> Dict:
        """Get license statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            "total_licenses": 0,
            "active_licenses": 0,
            "expired_licenses": 0,
            "revoked_licenses": 0,
            "total_users": 0,
            "total_activations": 0,
            "by_type": {},
            "recent_activity": []
        }
        
        cursor.execute('SELECT COUNT(*) FROM licenses')
        stats["total_licenses"] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licenses WHERE status = ?', (LicenseStatus.ACTIVE.value,))
        stats["active_licenses"] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licenses WHERE status = ?', (LicenseStatus.EXPIRED.value,))
        stats["expired_licenses"] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licenses WHERE status = ?', (LicenseStatus.REVOKED.value,))
        stats["revoked_licenses"] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users')
        stats["total_users"] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM activations')
        stats["total_activations"] = cursor.fetchone()[0]
        
        cursor.execute('SELECT license_type, COUNT(*) FROM licenses GROUP BY license_type')
        for row in cursor.fetchall():
            stats["by_type"][row[0]] = row[1]
            
        # Recent activity
        cursor.execute('''
            SELECT action, details, timestamp FROM activity_logs 
            ORDER BY timestamp DESC LIMIT 10
        ''')
        for row in cursor.fetchall():
            stats["recent_activity"].append({
                "action": row[0],
                "details": row[1],
                "timestamp": row[2]
            })
            
        conn.close()
        return stats
        
    def link_telegram(self, user_id: str, telegram_id: str) -> bool:
        """Link Telegram account to user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET telegram_id = ? WHERE user_id = ?',
                      (telegram_id, user_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0


# CLI Interface
def main():
    """CLI for License System"""
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk License System')
    parser.add_argument('command', choices=[
        'create-user', 'create-license', 'verify', 'list-licenses', 
        'list-users', 'stats', 'revoke', 'extend', 'generate-encrypted'
    ])
    parser.add_argument('--username', help='Username')
    parser.add_argument('--email', help='Email')
    parser.add_argument('--password', help='Password')
    parser.add_argument('--role', default='user', help='User role')
    parser.add_argument('--key', help='License key')
    parser.add_argument('--hwid', help='Hardware ID')
    parser.add_argument('--type', default='basic', help='License type')
    parser.add_argument('--days', type=int, default=30, help='Duration in days')
    parser.add_argument('--user-id', help='User ID')
    parser.add_argument('--owner', default='User', help='Owner name')
    parser.add_argument('--db', default='dlnk_licenses.db', help='Database path')
    
    args = parser.parse_args()
    
    system = DLNKLicenseSystem(args.db)
    
    if args.command == 'create-user':
        if not args.username:
            print("Error: --username required")
            return
        try:
            user = system.create_user(args.username, args.email, args.password, args.role)
            print(f"User created: {user.user_id}")
            print(f"Username: {user.username}")
            print(f"Role: {user.role}")
        except ValueError as e:
            print(f"Error: {e}")
        
    elif args.command == 'create-license':
        user_id = args.user_id or "default"
        license_type = LicenseType(args.type)
        license_obj = system.create_license(user_id, license_type, args.days, owner_name=args.owner)
        print(f"License created!")
        print(f"Key: {license_obj.key}")
        print(f"Type: {license_obj.license_type.value}")
        print(f"Expires: {license_obj.expires_at}")
        print(f"Features: {', '.join(license_obj.features)}")
        
    elif args.command == 'verify':
        if not args.key:
            print("Error: --key required")
            return
        valid, message, license_obj = system.verify_license(args.key, args.hwid)
        print(f"Valid: {valid}")
        print(f"Message: {message}")
        if license_obj:
            print(f"Type: {license_obj.license_type.value}")
            print(f"Features: {', '.join(license_obj.features)}")
        
    elif args.command == 'list-licenses':
        licenses = system.get_all_licenses()
        print(f"\n{'Key':<25} {'Type':<12} {'Status':<10} {'Expires':<20}")
        print("-" * 70)
        for lic in licenses:
            print(f"{lic.key:<25} {lic.license_type.value:<12} {lic.status.value:<10} {lic.expires_at[:19]}")
            
    elif args.command == 'list-users':
        users = system.get_all_users()
        print(f"\n{'Username':<20} {'Role':<12} {'Email':<30}")
        print("-" * 65)
        for user in users:
            print(f"{user.username:<20} {user.role:<12} {user.email or 'N/A':<30}")
            
    elif args.command == 'stats':
        stats = system.get_license_stats()
        print("\n=== License Statistics ===")
        print(f"Total Licenses: {stats['total_licenses']}")
        print(f"Active: {stats['active_licenses']}")
        print(f"Expired: {stats['expired_licenses']}")
        print(f"Revoked: {stats['revoked_licenses']}")
        print(f"Total Users: {stats['total_users']}")
        print(f"Total Activations: {stats['total_activations']}")
        print("\nBy Type:")
        for type_name, count in stats['by_type'].items():
            print(f"  {type_name}: {count}")
        
    elif args.command == 'revoke':
        if not args.key:
            print("Error: --key required")
            return
        if system.revoke_license(args.key):
            print("License revoked successfully")
        else:
            print("License not found")
            
    elif args.command == 'extend':
        if not args.key:
            print("Error: --key required")
            return
        if system.extend_license(args.key, args.days):
            print(f"License extended by {args.days} days")
        else:
            print("License not found")
            
    elif args.command == 'generate-encrypted':
        key = generate_encrypted_license(args.days, args.owner)
        print(f"Encrypted License Key:")
        print(key)


if __name__ == "__main__":
    main()
