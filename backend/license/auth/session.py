"""
Session Management
ระบบจัดการ Session สำหรับ Authentication
"""

import sqlite3
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
import logging

import sys
sys.path.append('..')
from config import get_config

logger = logging.getLogger('dLNk-Session')
config = get_config()


class SessionManager:
    """
    จัดการ Session สำหรับ User Authentication
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """สร้างตาราง sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                license_key TEXT,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                last_activity TEXT,
                is_valid INTEGER DEFAULT 1,
                offline_mode INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_valid ON sessions(is_valid)')
        
        conn.commit()
        conn.close()
    
    def create_session(
        self,
        user_id: str,
        username: str,
        license_key: str = None,
        ip_address: str = None,
        user_agent: str = None,
        offline_mode: bool = False,
        lifetime_hours: int = None
    ) -> str:
        """
        สร้าง Session ใหม่
        
        Args:
            user_id: User ID
            username: Username
            license_key: License key (optional)
            ip_address: IP address
            user_agent: User agent string
            offline_mode: เป็น offline session หรือไม่
            lifetime_hours: อายุ session (ชั่วโมง)
        
        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        lifetime = lifetime_hours or config.SESSION_LIFETIME_HOURS
        
        now = datetime.now()
        expires_at = now + timedelta(hours=lifetime)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (
                session_id, user_id, username, license_key, ip_address, user_agent,
                created_at, expires_at, last_activity, is_valid, offline_mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        ''', (
            session_id, user_id, username, license_key, ip_address, user_agent,
            now.isoformat(), expires_at.isoformat(), now.isoformat(), int(offline_mode)
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Session created for user {username}: {session_id[:16]}...")
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """
        ตรวจสอบ Session
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data หรือ None ถ้าไม่ valid
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, username, license_key, expires_at, is_valid, offline_mode
            FROM sessions WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        user_id, username, license_key, expires_at, is_valid, offline_mode = row
        
        # Check if valid
        if not is_valid:
            conn.close()
            return None
        
        # Check expiration
        if datetime.now() > datetime.fromisoformat(expires_at):
            self.invalidate_session(session_id)
            conn.close()
            return None
        
        # Update last activity
        cursor.execute('''
            UPDATE sessions SET last_activity = ? WHERE session_id = ?
        ''', (datetime.now().isoformat(), session_id))
        conn.commit()
        conn.close()
        
        return {
            'session_id': session_id,
            'user_id': user_id,
            'username': username,
            'license_key': license_key,
            'offline_mode': bool(offline_mode)
        }
    
    def invalidate_session(self, session_id: str) -> bool:
        """ยกเลิก Session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions SET is_valid = 0 WHERE session_id = ?
        ''', (session_id,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if affected > 0:
            logger.info(f"Session invalidated: {session_id[:16]}...")
        
        return affected > 0
    
    def invalidate_user_sessions(self, user_id: str) -> int:
        """ยกเลิก Session ทั้งหมดของ user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions SET is_valid = 0 WHERE user_id = ? AND is_valid = 1
        ''', (user_id,))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        logger.info(f"Invalidated {affected} sessions for user {user_id}")
        return affected
    
    def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """ดึงรายการ sessions ของ user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('''
                SELECT session_id, ip_address, user_agent, created_at, last_activity
                FROM sessions WHERE user_id = ? AND is_valid = 1
                ORDER BY last_activity DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT session_id, ip_address, user_agent, created_at, last_activity, is_valid
                FROM sessions WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            session = {
                'session_id': row[0][:16] + '...',  # Truncate for security
                'ip_address': row[1],
                'user_agent': row[2],
                'created_at': row[3],
                'last_activity': row[4]
            }
            if not active_only:
                session['is_valid'] = bool(row[5])
            sessions.append(session)
        
        return sessions
    
    def extend_session(self, session_id: str, hours: int = None) -> bool:
        """ขยายอายุ Session"""
        hours = hours or config.SESSION_LIFETIME_HOURS
        new_expiry = datetime.now() + timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sessions SET expires_at = ? WHERE session_id = ? AND is_valid = 1
        ''', (new_expiry.isoformat(), session_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def cleanup_expired_sessions(self) -> int:
        """ลบ sessions ที่หมดอายุ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM sessions WHERE expires_at < ? OR is_valid = 0
        ''', (datetime.now().isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired sessions")
        
        return deleted
    
    def get_session_count(self, active_only: bool = True) -> int:
        """นับจำนวน sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('SELECT COUNT(*) FROM sessions WHERE is_valid = 1')
        else:
            cursor.execute('SELECT COUNT(*) FROM sessions')
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count


# Global instance
session_manager = SessionManager()
