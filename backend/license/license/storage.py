"""
License Storage
ระบบจัดเก็บ License ใน SQLite Database
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple
from pathlib import Path
import logging

import sys
sys.path.append('..')
from config import get_config
from .generator import LicenseData, LicenseType, LicenseStatus

logger = logging.getLogger('dLNk-LicenseStorage')
config = get_config()


class LicenseStorage:
    """
    จัดการการเก็บ License ใน Database
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """สร้างตารางในฐานข้อมูล"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Licenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                license_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                license_type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                hardware_id TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                max_devices INTEGER DEFAULT 1,
                features TEXT,
                encrypted_data TEXT,
                owner_name TEXT,
                email TEXT
            )
        ''')
        
        # Activations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT NOT NULL,
                hardware_id TEXT NOT NULL,
                device_name TEXT,
                activated_at TEXT NOT NULL,
                last_seen TEXT,
                ip_address TEXT,
                FOREIGN KEY (license_key) REFERENCES licenses(license_key),
                UNIQUE(license_key, hardware_id)
            )
        ''')
        
        # Revoked licenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revoked_licenses (
                license_key TEXT PRIMARY KEY,
                revoked_at TEXT NOT NULL,
                reason TEXT,
                revoked_by TEXT
            )
        ''')
        
        # Activity logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS license_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_licenses_user ON licenses(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_activations_license ON activations(license_key)')
        
        conn.commit()
        conn.close()
        logger.info(f"License database initialized: {self.db_path}")
    
    def store_license(
        self,
        license_key: str,
        license_data: LicenseData,
        encrypted_data: str
    ) -> bool:
        """
        เก็บ License ใหม่
        
        Args:
            license_key: License key
            license_data: ข้อมูล License
            encrypted_data: ข้อมูลที่เข้ารหัสแล้ว
        
        Returns:
            True ถ้าสำเร็จ
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO licenses (
                    license_key, license_id, user_id, license_type, status,
                    hardware_id, created_at, expires_at, max_devices, features,
                    encrypted_data, owner_name, email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                license_key,
                license_data.license_id,
                license_data.user_id,
                license_data.license_type,
                LicenseStatus.ACTIVE.value,
                license_data.hardware_id,
                license_data.created_at,
                license_data.expires_at,
                license_data.max_devices,
                json.dumps(license_data.features),
                encrypted_data,
                license_data.owner_name,
                license_data.email
            ))
            
            self._log_action(cursor, license_key, "created", 
                           f"License created for user {license_data.user_id}")
            
            conn.commit()
            logger.info(f"License stored: {license_key}")
            return True
            
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to store license: {e}")
            return False
        finally:
            conn.close()
    
    def get_license(self, license_key: str) -> Optional[Dict]:
        """ดึงข้อมูล License"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM licenses WHERE license_key = ?', (license_key,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def get_license_data(self, license_key: str) -> Optional[str]:
        """ดึง encrypted data ของ License"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT encrypted_data FROM licenses WHERE license_key = ?', (license_key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def get_licenses_by_user(self, user_id: str) -> List[Dict]:
        """ดึง License ทั้งหมดของ user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM licenses WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def get_all_licenses(self, status: str = None) -> List[Dict]:
        """ดึง License ทั้งหมด"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM licenses WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM licenses ORDER BY created_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_dict(row) for row in rows]
    
    def update_license_status(self, license_key: str, status: LicenseStatus) -> bool:
        """อัพเดทสถานะ License"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE licenses SET status = ? WHERE license_key = ?
        ''', (status.value, license_key))
        
        affected = cursor.rowcount
        
        if affected > 0:
            self._log_action(cursor, license_key, "status_changed", f"Status changed to {status.value}")
        
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def update_hardware_id(self, license_key: str, hardware_id: str) -> bool:
        """อัพเดท Hardware ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE licenses SET hardware_id = ? WHERE license_key = ?
        ''', (hardware_id, license_key))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def extend_license(self, license_key: str, days: int) -> bool:
        """ขยายอายุ License"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT expires_at FROM licenses WHERE license_key = ?', (license_key,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        from datetime import timedelta
        current_expiry = datetime.fromisoformat(row[0])
        new_expiry = current_expiry + timedelta(days=days)
        
        cursor.execute('''
            UPDATE licenses SET expires_at = ?, status = ? WHERE license_key = ?
        ''', (new_expiry.isoformat(), LicenseStatus.ACTIVE.value, license_key))
        
        self._log_action(cursor, license_key, "extended", f"Extended by {days} days")
        
        conn.commit()
        conn.close()
        
        logger.info(f"License extended: {license_key} by {days} days")
        return True
    
    def revoke_license(self, license_key: str, reason: str = "", revoked_by: str = "") -> bool:
        """เพิกถอน License"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update status
        cursor.execute('''
            UPDATE licenses SET status = ? WHERE license_key = ?
        ''', (LicenseStatus.REVOKED.value, license_key))
        
        if cursor.rowcount == 0:
            conn.close()
            return False
        
        # Record revocation
        cursor.execute('''
            INSERT OR REPLACE INTO revoked_licenses (license_key, revoked_at, reason, revoked_by)
            VALUES (?, ?, ?, ?)
        ''', (license_key, datetime.now().isoformat(), reason, revoked_by))
        
        self._log_action(cursor, license_key, "revoked", f"Revoked: {reason}")
        
        conn.commit()
        conn.close()
        
        logger.info(f"License revoked: {license_key}")
        return True
    
    def is_revoked(self, license_key: str) -> bool:
        """ตรวจสอบว่า License ถูกเพิกถอนหรือไม่"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM revoked_licenses WHERE license_key = ?', (license_key,))
        row = cursor.fetchone()
        conn.close()
        
        return row is not None
    
    def record_activation(
        self,
        license_key: str,
        hardware_id: str,
        device_name: str = "",
        ip_address: str = ""
    ) -> bool:
        """บันทึกการ activate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO activations (license_key, hardware_id, device_name, activated_at, last_seen, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(license_key, hardware_id) DO UPDATE SET
                    last_seen = excluded.last_seen,
                    ip_address = excluded.ip_address
            ''', (license_key, hardware_id, device_name, now, now, ip_address))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to record activation: {e}")
            return False
        finally:
            conn.close()
    
    def get_activation_count(self, license_key: str) -> int:
        """นับจำนวนการ activate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM activations WHERE license_key = ?', (license_key,))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_activations(self, license_key: str) -> List[Dict]:
        """ดึงรายการ activations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hardware_id, device_name, activated_at, last_seen, ip_address
            FROM activations WHERE license_key = ?
        ''', (license_key,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'hardware_id': row[0],
                'device_name': row[1],
                'activated_at': row[2],
                'last_seen': row[3],
                'ip_address': row[4]
            }
            for row in rows
        ]
    
    def get_statistics(self) -> Dict:
        """ดึงสถิติ License"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {
            'total_licenses': 0,
            'active_licenses': 0,
            'expired_licenses': 0,
            'revoked_licenses': 0,
            'total_activations': 0,
            'by_type': {}
        }
        
        cursor.execute('SELECT COUNT(*) FROM licenses')
        stats['total_licenses'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licenses WHERE status = ?', (LicenseStatus.ACTIVE.value,))
        stats['active_licenses'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licenses WHERE status = ?', (LicenseStatus.EXPIRED.value,))
        stats['expired_licenses'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licenses WHERE status = ?', (LicenseStatus.REVOKED.value,))
        stats['revoked_licenses'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM activations')
        stats['total_activations'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT license_type, COUNT(*) FROM licenses GROUP BY license_type')
        for row in cursor.fetchall():
            stats['by_type'][row[0]] = row[1]
        
        conn.close()
        return stats
    
    def _log_action(self, cursor, license_key: str, action: str, details: str, ip: str = None):
        """บันทึก log"""
        cursor.execute('''
            INSERT INTO license_logs (license_key, action, details, ip_address, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (license_key, action, details, ip, datetime.now().isoformat()))
    
    def _row_to_dict(self, row) -> Dict:
        """แปลง row เป็น dictionary"""
        return {
            'license_key': row[0],
            'license_id': row[1],
            'user_id': row[2],
            'license_type': row[3],
            'status': row[4],
            'hardware_id': row[5],
            'created_at': row[6],
            'expires_at': row[7],
            'max_devices': row[8],
            'features': json.loads(row[9]) if row[9] else [],
            'encrypted_data': row[10],
            'owner_name': row[11],
            'email': row[12]
        }


# Global instance
license_storage = LicenseStorage()
