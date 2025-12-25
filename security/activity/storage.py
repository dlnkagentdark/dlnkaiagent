#!/usr/bin/env python3
"""
Activity Storage
จัดเก็บ Activity Logs ใน Database
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager

logger = logging.getLogger('ActivityStorage')


@dataclass
class StoredActivity:
    """โครงสร้างข้อมูลที่เก็บใน Database"""
    id: int
    timestamp: str
    user_id: str
    action: str
    action_type: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    session_id: Optional[str]
    hwid: Optional[str]
    success: bool
    duration_ms: Optional[int]


class ActivityStorage:
    """
    จัดเก็บ Activity Logs ใน SQLite Database
    """
    
    def __init__(
        self,
        db_dir: str = None,
        db_name: str = "activity.db",
        retention_days: int = 90
    ):
        self.db_dir = Path(db_dir) if db_dir else Path.home() / ".dlnk-ide" / "db"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.db_dir / db_name
        self.retention_days = retention_days
        
        self._init_db()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_db(self):
        """สร้างตาราง"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Activity logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    session_id TEXT,
                    hwid TEXT,
                    success INTEGER DEFAULT 1,
                    duration_ms INTEGER
                )
            ''')
            
            # User summary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_summary (
                    user_id TEXT PRIMARY KEY,
                    hwid TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    total_activities INTEGER DEFAULT 0,
                    total_logins INTEGER DEFAULT 0,
                    total_ai_requests INTEGER DEFAULT 0,
                    total_blocked INTEGER DEFAULT 0,
                    total_errors INTEGER DEFAULT 0,
                    risk_score REAL DEFAULT 0.0,
                    is_flagged INTEGER DEFAULT 0,
                    notes TEXT
                )
            ''')
            
            # Session table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    hwid TEXT,
                    ip_address TEXT,
                    started_at TEXT,
                    ended_at TEXT,
                    request_count INTEGER DEFAULT 0,
                    blocked_count INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_user ON activities(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON activities(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(action_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)')
            
            conn.commit()
    
    def store_activity(
        self,
        user_id: str,
        action: str,
        action_type: str,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        session_id: str = None,
        hwid: str = None,
        success: bool = True,
        duration_ms: int = None
    ) -> int:
        """บันทึกกิจกรรม"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activities 
                (user_id, action, action_type, details, ip_address, 
                 session_id, hwid, success, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, action, action_type,
                json.dumps(details) if details else None,
                ip_address, session_id, hwid,
                1 if success else 0, duration_ms
            ))
            
            activity_id = cursor.lastrowid
            
            # Update user summary
            self._update_user_summary(cursor, user_id, action_type, hwid, success)
            
            conn.commit()
            
            return activity_id
    
    def _update_user_summary(
        self,
        cursor,
        user_id: str,
        action_type: str,
        hwid: str,
        success: bool
    ):
        """อัปเดตสรุปผู้ใช้"""
        now = datetime.now().isoformat()
        
        cursor.execute('SELECT user_id FROM user_summary WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            update_fields = ['last_seen = ?', 'total_activities = total_activities + 1']
            params = [now]
            
            if action_type == 'login':
                update_fields.append('total_logins = total_logins + 1')
            elif action_type == 'ai_request':
                update_fields.append('total_ai_requests = total_ai_requests + 1')
            elif action_type == 'security_event':
                update_fields.append('total_blocked = total_blocked + 1')
            elif action_type == 'error':
                update_fields.append('total_errors = total_errors + 1')
            
            params.append(user_id)
            cursor.execute(f'''
                UPDATE user_summary SET {', '.join(update_fields)} WHERE user_id = ?
            ''', params)
        else:
            cursor.execute('''
                INSERT INTO user_summary 
                (user_id, hwid, first_seen, last_seen, total_activities)
                VALUES (?, ?, ?, ?, 1)
            ''', (user_id, hwid, now, now))
    
    def store_session(
        self,
        session_id: str,
        user_id: str,
        hwid: str = None,
        ip_address: str = None
    ):
        """บันทึก session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (session_id, user_id, hwid, ip_address, started_at, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            ''', (session_id, user_id, hwid, ip_address, datetime.now().isoformat()))
            
            conn.commit()
    
    def end_session(self, session_id: str):
        """จบ session"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions SET ended_at = ?, is_active = 0 WHERE session_id = ?
            ''', (datetime.now().isoformat(), session_id))
            
            conn.commit()
    
    def get_activities(
        self,
        user_id: str = None,
        action_type: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredActivity]:
        """ดึงกิจกรรม"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = 'SELECT * FROM activities WHERE 1=1'
            params = []
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            if action_type:
                query += ' AND action_type = ?'
                params.append(action_type)
            
            if start_date:
                query += ' AND timestamp >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND timestamp <= ?'
                params.append(end_date)
            
            query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            activities = []
            for row in rows:
                activities.append(StoredActivity(
                    id=row['id'],
                    timestamp=row['timestamp'],
                    user_id=row['user_id'],
                    action=row['action'],
                    action_type=row['action_type'],
                    details=json.loads(row['details']) if row['details'] else {},
                    ip_address=row['ip_address'],
                    session_id=row['session_id'],
                    hwid=row['hwid'],
                    success=bool(row['success']),
                    duration_ms=row['duration_ms']
                ))
            
            return activities
    
    def get_user_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ดึงสรุปผู้ใช้"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_summary WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return dict(row)
    
    def get_all_users_summary(self) -> List[Dict[str, Any]]:
        """ดึงสรุปผู้ใช้ทั้งหมด"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_summary ORDER BY last_seen DESC')
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """ดึง active sessions"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sessions WHERE is_active = 1')
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """ดึงสถิติ"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total activities
            cursor.execute('SELECT COUNT(*) FROM activities')
            total_activities = cursor.fetchone()[0]
            
            # Total users
            cursor.execute('SELECT COUNT(*) FROM user_summary')
            total_users = cursor.fetchone()[0]
            
            # Active sessions
            cursor.execute('SELECT COUNT(*) FROM sessions WHERE is_active = 1')
            active_sessions = cursor.fetchone()[0]
            
            # Today's activities
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                'SELECT COUNT(*) FROM activities WHERE timestamp >= ?',
                (today,)
            )
            today_activities = cursor.fetchone()[0]
            
            # Flagged users
            cursor.execute('SELECT COUNT(*) FROM user_summary WHERE is_flagged = 1')
            flagged_users = cursor.fetchone()[0]
            
            return {
                "total_activities": total_activities,
                "total_users": total_users,
                "active_sessions": active_sessions,
                "today_activities": today_activities,
                "flagged_users": flagged_users
            }
    
    def cleanup_old_data(self, days: int = None):
        """ลบข้อมูลเก่า"""
        days = days or self.retention_days
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM activities WHERE timestamp < ?', (cutoff,))
            deleted = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Cleaned up {deleted} old activities")
            
            return deleted
    
    def flag_user(self, user_id: str, note: str = None):
        """Flag ผู้ใช้"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            notes = ""
            if note:
                notes = f"[{datetime.now().isoformat()}] {note}"
            
            cursor.execute('''
                UPDATE user_summary 
                SET is_flagged = 1, notes = COALESCE(notes, '') || ?
                WHERE user_id = ?
            ''', (notes + "\n" if notes else "", user_id))
            
            conn.commit()
    
    def unflag_user(self, user_id: str):
        """Unflag ผู้ใช้"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_summary SET is_flagged = 0 WHERE user_id = ?
            ''', (user_id,))
            
            conn.commit()
