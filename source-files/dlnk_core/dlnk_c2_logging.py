#!/usr/bin/env python3
"""
dLNk C2 Logging System v1.0
ระบบเก็บประวัติคำสั่งและกิจกรรมทั้งหมด
- บันทึกทุก Prompt ที่ส่งมา
- ตรวจจับพฤติกรรมผิดปกติ
- แจ้งเตือน Admin ผ่าน Telegram
- รายงานสถิติ
"""

import os
import json
import sqlite3
import hashlib
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging
import asyncio
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-C2Logging')


class C2LoggingConfig:
    """การตั้งค่าระบบ Logging"""
    
    # Database
    DB_PATH = str(Path.home() / ".dlnk-ide" / "c2_logs.db")
    
    # Log retention
    RETENTION_DAYS = 90
    
    # Anomaly detection
    MAX_REQUESTS_PER_MINUTE = 30
    MAX_REQUESTS_PER_HOUR = 500
    SUSPICIOUS_KEYWORDS = [
        'bypass', 'crack', 'hack', 'exploit', 'inject',
        'admin', 'password', 'token', 'secret', 'key'
    ]
    
    # Alert thresholds
    ALERT_ON_BLOCKED = True
    ALERT_ON_SUSPICIOUS = True
    ALERT_ON_RATE_LIMIT = True
    
    # Telegram notification (optional)
    TELEGRAM_BOT_TOKEN = os.environ.get('DLNK_TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_ADMIN_CHAT_ID = os.environ.get('DLNK_TELEGRAM_ADMIN_ID', '')


class C2LogDatabase:
    """Database สำหรับ C2 Logs"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or C2LoggingConfig.DB_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """สร้างตาราง"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS c2_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT NOT NULL,
                hwid TEXT,
                ip_address TEXT,
                session_id TEXT,
                action TEXT NOT NULL,
                prompt_hash TEXT,
                prompt_preview TEXT,
                prompt_length INTEGER,
                response_length INTEGER,
                status TEXT,
                blocked_reason TEXT,
                processing_time_ms INTEGER,
                metadata TEXT
            )
        ''')
        
        # User activity summary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id TEXT PRIMARY KEY,
                hwid TEXT,
                first_seen TEXT,
                last_seen TEXT,
                total_requests INTEGER DEFAULT 0,
                blocked_requests INTEGER DEFAULT 0,
                suspicious_requests INTEGER DEFAULT 0,
                total_tokens_used INTEGER DEFAULT 0,
                risk_score REAL DEFAULT 0.0,
                is_flagged INTEGER DEFAULT 0,
                notes TEXT
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                user_id TEXT,
                message TEXT NOT NULL,
                details TEXT,
                acknowledged INTEGER DEFAULT 0,
                acknowledged_by TEXT,
                acknowledged_at TEXT
            )
        ''')
        
        # Rate limiting table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_id TEXT NOT NULL,
                window_start TEXT NOT NULL,
                window_type TEXT NOT NULL,
                request_count INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, window_start, window_type)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_user ON c2_logs(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON c2_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_status ON c2_logs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged)')
        
        conn.commit()
        conn.close()
    
    def log_request(self, user_id: str, action: str, prompt: str = None,
                    response_length: int = 0, status: str = "success",
                    blocked_reason: str = None, processing_time_ms: int = 0,
                    hwid: str = None, ip_address: str = None, 
                    session_id: str = None, metadata: Dict = None) -> int:
        """บันทึก request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:32] if prompt else None
        prompt_preview = (prompt[:200] + "...") if prompt and len(prompt) > 200 else prompt
        prompt_length = len(prompt) if prompt else 0
        
        cursor.execute('''
            INSERT INTO c2_logs 
            (user_id, hwid, ip_address, session_id, action, prompt_hash, 
             prompt_preview, prompt_length, response_length, status, 
             blocked_reason, processing_time_ms, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, hwid, ip_address, session_id, action, prompt_hash,
              prompt_preview, prompt_length, response_length, status,
              blocked_reason, processing_time_ms, 
              json.dumps(metadata) if metadata else None))
        
        log_id = cursor.lastrowid
        
        # Update user activity
        self._update_user_activity(cursor, user_id, hwid, status)
        
        conn.commit()
        conn.close()
        
        return log_id
    
    def _update_user_activity(self, cursor, user_id: str, hwid: str, status: str):
        """อัปเดตสถิติผู้ใช้"""
        now = datetime.now().isoformat()
        
        cursor.execute('SELECT user_id FROM user_activity WHERE user_id = ?', (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            update_fields = ['last_seen = ?', 'total_requests = total_requests + 1']
            params = [now]
            
            if status == "blocked":
                update_fields.append('blocked_requests = blocked_requests + 1')
            elif status == "suspicious":
                update_fields.append('suspicious_requests = suspicious_requests + 1')
            
            params.append(user_id)
            cursor.execute(f'''
                UPDATE user_activity SET {', '.join(update_fields)} WHERE user_id = ?
            ''', params)
        else:
            cursor.execute('''
                INSERT INTO user_activity (user_id, hwid, first_seen, last_seen, total_requests)
                VALUES (?, ?, ?, ?, 1)
            ''', (user_id, hwid, now, now))
    
    def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """ตรวจสอบ rate limit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        minute_window = now.strftime("%Y-%m-%d %H:%M")
        hour_window = now.strftime("%Y-%m-%d %H")
        
        # Check minute limit
        cursor.execute('''
            SELECT request_count FROM rate_limits 
            WHERE user_id = ? AND window_start = ? AND window_type = 'minute'
        ''', (user_id, minute_window))
        
        row = cursor.fetchone()
        minute_count = row[0] if row else 0
        
        if minute_count >= C2LoggingConfig.MAX_REQUESTS_PER_MINUTE:
            conn.close()
            return False, f"Rate limit exceeded: {minute_count}/{C2LoggingConfig.MAX_REQUESTS_PER_MINUTE} per minute"
        
        # Check hour limit
        cursor.execute('''
            SELECT request_count FROM rate_limits 
            WHERE user_id = ? AND window_start = ? AND window_type = 'hour'
        ''', (user_id, hour_window))
        
        row = cursor.fetchone()
        hour_count = row[0] if row else 0
        
        if hour_count >= C2LoggingConfig.MAX_REQUESTS_PER_HOUR:
            conn.close()
            return False, f"Rate limit exceeded: {hour_count}/{C2LoggingConfig.MAX_REQUESTS_PER_HOUR} per hour"
        
        # Update counters
        cursor.execute('''
            INSERT INTO rate_limits (user_id, window_start, window_type, request_count)
            VALUES (?, ?, 'minute', 1)
            ON CONFLICT(user_id, window_start, window_type) 
            DO UPDATE SET request_count = request_count + 1
        ''', (user_id, minute_window))
        
        cursor.execute('''
            INSERT INTO rate_limits (user_id, window_start, window_type, request_count)
            VALUES (?, ?, 'hour', 1)
            ON CONFLICT(user_id, window_start, window_type) 
            DO UPDATE SET request_count = request_count + 1
        ''', (user_id, hour_window))
        
        conn.commit()
        conn.close()
        
        return True, ""
    
    def create_alert(self, alert_type: str, severity: str, message: str,
                     user_id: str = None, details: str = None) -> int:
        """สร้าง alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (alert_type, severity, user_id, message, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (alert_type, severity, user_id, message, details))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.warning(f"Alert created: [{severity}] {alert_type} - {message}")
        
        return alert_id
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """ดึงสถิติผู้ใช้"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_activity WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        columns = [desc[0] for desc in cursor.description]
        result = dict(zip(columns, row))
        
        conn.close()
        return result
    
    def get_recent_logs(self, limit: int = 100, user_id: str = None,
                        status: str = None) -> List[Dict]:
        """ดึง logs ล่าสุด"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM c2_logs'
        params = []
        conditions = []
        
        if user_id:
            conditions.append('user_id = ?')
            params.append(user_id)
        
        if status:
            conditions.append('status = ?')
            params.append(status)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return results
    
    def get_alerts(self, unacknowledged_only: bool = True, limit: int = 50) -> List[Dict]:
        """ดึง alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM alerts'
        if unacknowledged_only:
            query += ' WHERE acknowledged = 0'
        query += ' ORDER BY timestamp DESC LIMIT ?'
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return results
    
    def get_dashboard_stats(self) -> Dict:
        """ดึงสถิติสำหรับ Dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total requests today
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute('''
            SELECT COUNT(*) FROM c2_logs WHERE timestamp LIKE ?
        ''', (f"{today}%",))
        stats['requests_today'] = cursor.fetchone()[0]
        
        # Blocked requests today
        cursor.execute('''
            SELECT COUNT(*) FROM c2_logs WHERE timestamp LIKE ? AND status = 'blocked'
        ''', (f"{today}%",))
        stats['blocked_today'] = cursor.fetchone()[0]
        
        # Active users today
        cursor.execute('''
            SELECT COUNT(DISTINCT user_id) FROM c2_logs WHERE timestamp LIKE ?
        ''', (f"{today}%",))
        stats['active_users_today'] = cursor.fetchone()[0]
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM user_activity')
        stats['total_users'] = cursor.fetchone()[0]
        
        # Unacknowledged alerts
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE acknowledged = 0')
        stats['pending_alerts'] = cursor.fetchone()[0]
        
        # Top users by requests
        cursor.execute('''
            SELECT user_id, COUNT(*) as count FROM c2_logs 
            WHERE timestamp LIKE ? 
            GROUP BY user_id ORDER BY count DESC LIMIT 5
        ''', (f"{today}%",))
        stats['top_users'] = [{"user_id": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        return stats
    
    def cleanup_old_logs(self, days: int = None):
        """ลบ logs เก่า"""
        days = days or C2LoggingConfig.RETENTION_DAYS
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM c2_logs WHERE timestamp < ?', (cutoff,))
        deleted_logs = cursor.rowcount
        
        cursor.execute('DELETE FROM rate_limits WHERE window_start < ?', (cutoff[:10],))
        deleted_rate = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleanup: Deleted {deleted_logs} logs and {deleted_rate} rate limit records")
        return deleted_logs


class C2LoggingMiddleware:
    """Middleware สำหรับ AI Bridge"""
    
    def __init__(self):
        self.db = C2LogDatabase()
        self.telegram_notifier = None
        
        if C2LoggingConfig.TELEGRAM_BOT_TOKEN and C2LoggingConfig.TELEGRAM_ADMIN_CHAT_ID:
            self.telegram_notifier = TelegramNotifier(
                C2LoggingConfig.TELEGRAM_BOT_TOKEN,
                C2LoggingConfig.TELEGRAM_ADMIN_CHAT_ID
            )
    
    async def log_and_check(self, user_id: str, prompt: str, 
                            hwid: str = None, ip: str = None) -> Tuple[bool, str]:
        """Log request และตรวจสอบ"""
        
        # Check rate limit
        allowed, reason = self.db.check_rate_limit(user_id)
        if not allowed:
            self.db.log_request(
                user_id=user_id,
                action="chat",
                prompt=prompt,
                status="rate_limited",
                blocked_reason=reason,
                hwid=hwid,
                ip_address=ip
            )
            
            if C2LoggingConfig.ALERT_ON_RATE_LIMIT:
                self.db.create_alert(
                    "RATE_LIMIT",
                    "warning",
                    f"User {user_id} exceeded rate limit",
                    user_id,
                    reason
                )
                
                if self.telegram_notifier:
                    await self.telegram_notifier.send_alert(
                        f"⚠️ Rate Limit: {user_id}\n{reason}"
                    )
            
            return False, "Rate limit exceeded. Please slow down."
        
        return True, ""
    
    def log_response(self, user_id: str, prompt: str, response_length: int,
                     status: str, processing_time_ms: int,
                     blocked_reason: str = None, hwid: str = None, ip: str = None):
        """Log response"""
        self.db.log_request(
            user_id=user_id,
            action="chat",
            prompt=prompt,
            response_length=response_length,
            status=status,
            blocked_reason=blocked_reason,
            processing_time_ms=processing_time_ms,
            hwid=hwid,
            ip_address=ip
        )


class TelegramNotifier:
    """ส่งแจ้งเตือนผ่าน Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    async def send_alert(self, message: str):
        """ส่งข้อความแจ้งเตือน"""
        try:
            import aiohttp
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": f"🚨 dLNk Alert\n\n{message}",
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to send Telegram alert: {await resp.text()}")
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")


# ===== INTEGRATION =====

def integrate_with_ai_bridge(ai_bridge_instance, prompt_filter=None):
    """
    รวม C2 Logging เข้ากับ AI Bridge
    
    Usage:
        from dlnk_c2_logging import integrate_with_ai_bridge
        integrate_with_ai_bridge(bridge, prompt_filter)
    """
    middleware = C2LoggingMiddleware()
    
    original_process = ai_bridge_instance.process_message
    
    async def logged_process(message: str, user_id: str = "anonymous", **kwargs):
        import time
        start_time = time.time()
        
        hwid = kwargs.get('hwid')
        ip = kwargs.get('ip')
        
        # Check rate limit
        allowed, reason = await middleware.log_and_check(user_id, message, hwid, ip)
        if not allowed:
            return {
                "role": "assistant",
                "content": reason,
                "rate_limited": True
            }
        
        # Process
        result = await original_process(message, user_id=user_id, **kwargs)
        
        # Log response
        processing_time = int((time.time() - start_time) * 1000)
        status = "blocked" if result.get('filtered') else "success"
        
        middleware.log_response(
            user_id=user_id,
            prompt=message,
            response_length=len(result.get('content', '')),
            status=status,
            processing_time_ms=processing_time,
            blocked_reason=result.get('blocked_reason'),
            hwid=hwid,
            ip=ip
        )
        
        return result
    
    ai_bridge_instance.process_message = logged_process
    logger.info("C2 Logging integrated with AI Bridge")


# ===== CLI =====

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk C2 Logging System')
    parser.add_argument('command', choices=['stats', 'logs', 'alerts', 'cleanup', 'test'])
    parser.add_argument('--user', help='Filter by user ID')
    parser.add_argument('--limit', type=int, default=20, help='Limit results')
    parser.add_argument('--days', type=int, default=90, help='Days for cleanup')
    
    args = parser.parse_args()
    
    db = C2LogDatabase()
    
    if args.command == 'stats':
        stats = db.get_dashboard_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.command == 'logs':
        logs = db.get_recent_logs(limit=args.limit, user_id=args.user)
        for log in logs:
            print(f"[{log['timestamp']}] {log['user_id']}: {log['status']} - {log['prompt_preview'][:50]}...")
    
    elif args.command == 'alerts':
        alerts = db.get_alerts(limit=args.limit)
        for alert in alerts:
            print(f"[{alert['severity']}] {alert['alert_type']}: {alert['message']}")
    
    elif args.command == 'cleanup':
        deleted = db.cleanup_old_logs(args.days)
        print(f"Deleted {deleted} old log entries")
    
    elif args.command == 'test':
        # Test logging
        log_id = db.log_request(
            user_id="test_user",
            action="chat",
            prompt="This is a test prompt",
            response_length=100,
            status="success",
            processing_time_ms=150
        )
        print(f"Test log created with ID: {log_id}")
        
        # Test rate limit
        for i in range(5):
            allowed, reason = db.check_rate_limit("test_user")
            print(f"Rate limit check {i+1}: {'Allowed' if allowed else 'Blocked'} - {reason}")
        
        # Test stats
        stats = db.get_dashboard_stats()
        print(f"\nDashboard stats: {json.dumps(stats, indent=2)}")
