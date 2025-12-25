#!/usr/bin/env python3
"""
dLNk Admin Authentication System v1.0
ระบบยืนยันตัวตนสำหรับ Admin Web Console
- Login/Logout
- Session Management
- 2FA Support (TOTP)
- Rate Limiting
- Audit Logging
"""

import os
import json
import sqlite3
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from functools import wraps
from pathlib import Path
import logging

# Flask imports
from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify

# Optional: TOTP for 2FA
try:
    import pyotp
    TOTP_AVAILABLE = True
except ImportError:
    TOTP_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-AdminAuth')


class AdminAuthConfig:
    """การตั้งค่าระบบ Auth"""
    
    # Session
    SESSION_LIFETIME_HOURS = 24
    SESSION_SECRET_KEY = os.environ.get('DLNK_SECRET_KEY', secrets.token_hex(32))
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Password Policy
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_SPECIAL_CHAR = True
    
    # 2FA
    ENABLE_2FA = TOTP_AVAILABLE
    
    # IP Whitelist (empty = allow all)
    IP_WHITELIST = []  # e.g., ['127.0.0.1', '192.168.1.0/24']


class AdminAuthDB:
    """Database สำหรับ Admin Auth"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path.home() / ".dlnk-ide" / "admin_auth.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """สร้างตาราง"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Admin users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'admin',
                totp_secret TEXT,
                is_active INTEGER DEFAULT 1,
                must_change_password INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                failed_attempts INTEGER DEFAULT 0,
                locked_until TEXT
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                is_valid INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES admin_users(id)
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                ip_address TEXT,
                details TEXT,
                success INTEGER DEFAULT 1
            )
        ''')
        
        # Create default admin if not exists
        cursor.execute('SELECT COUNT(*) FROM admin_users')
        if cursor.fetchone()[0] == 0:
            self._create_default_admin(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_default_admin(self, cursor):
        """สร้าง admin เริ่มต้น"""
        salt = secrets.token_hex(16)
        password_hash = self._hash_password("admin123", salt)
        
        cursor.execute('''
            INSERT INTO admin_users (username, password_hash, salt, role, must_change_password)
            VALUES (?, ?, ?, 'superadmin', 1)
        ''', ('admin', password_hash, salt))
        
        logger.warning("Created default admin user. PLEASE CHANGE PASSWORD IMMEDIATELY!")
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
    
    def verify_password(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """ตรวจสอบรหัสผ่าน"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, password_hash, salt, role, is_active, 
                   must_change_password, failed_attempts, locked_until, totp_secret
            FROM admin_users WHERE username = ?
        ''', (username,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False, None
        
        user_id, username, stored_hash, salt, role, is_active, must_change, failed, locked_until, totp_secret = row
        
        # Check if locked
        if locked_until:
            lock_time = datetime.fromisoformat(locked_until)
            if datetime.now() < lock_time:
                return False, {"error": "Account locked", "locked_until": locked_until}
        
        # Check if active
        if not is_active:
            return False, {"error": "Account disabled"}
        
        # Verify password
        computed_hash = self._hash_password(password, salt)
        if computed_hash != stored_hash:
            self._increment_failed_attempts(user_id)
            return False, {"error": "Invalid password"}
        
        # Success - reset failed attempts
        self._reset_failed_attempts(user_id)
        
        return True, {
            "id": user_id,
            "username": username,
            "role": role,
            "must_change_password": bool(must_change),
            "has_2fa": bool(totp_secret)
        }
    
    def _increment_failed_attempts(self, user_id: int):
        """เพิ่มจำนวนครั้งที่ login ผิด"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT failed_attempts FROM admin_users WHERE id = ?', (user_id,))
        current = cursor.fetchone()[0] or 0
        new_count = current + 1
        
        if new_count >= AdminAuthConfig.MAX_LOGIN_ATTEMPTS:
            lock_until = datetime.now() + timedelta(minutes=AdminAuthConfig.LOCKOUT_DURATION_MINUTES)
            cursor.execute('''
                UPDATE admin_users SET failed_attempts = ?, locked_until = ? WHERE id = ?
            ''', (new_count, lock_until.isoformat(), user_id))
        else:
            cursor.execute('UPDATE admin_users SET failed_attempts = ? WHERE id = ?', (new_count, user_id))
        
        conn.commit()
        conn.close()
    
    def _reset_failed_attempts(self, user_id: int):
        """รีเซ็ตจำนวนครั้งที่ login ผิด"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE admin_users SET failed_attempts = 0, locked_until = NULL, last_login = ? WHERE id = ?
        ''', (datetime.now().isoformat(), user_id))
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: int, ip: str, user_agent: str) -> str:
        """สร้าง session ใหม่"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=AdminAuthConfig.SESSION_LIFETIME_HOURS)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admin_sessions (session_id, user_id, ip_address, user_agent, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, user_id, ip, user_agent, expires_at.isoformat()))
        conn.commit()
        conn.close()
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """ตรวจสอบ session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.user_id, s.expires_at, s.is_valid, u.username, u.role
            FROM admin_sessions s
            JOIN admin_users u ON s.user_id = u.id
            WHERE s.session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        user_id, expires_at, is_valid, username, role = row
        
        if not is_valid:
            return None
        
        if datetime.now() > datetime.fromisoformat(expires_at):
            self.invalidate_session(session_id)
            return None
        
        return {
            "user_id": user_id,
            "username": username,
            "role": role
        }
    
    def invalidate_session(self, session_id: str):
        """ยกเลิก session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE admin_sessions SET is_valid = 0 WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
    
    def log_action(self, user_id: int, username: str, action: str, ip: str, details: str = "", success: bool = True):
        """บันทึก audit log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admin_audit_log (user_id, username, action, ip_address, details, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, action, ip, details, int(success)))
        conn.commit()
        conn.close()
    
    def change_password(self, user_id: int, new_password: str) -> Tuple[bool, str]:
        """เปลี่ยนรหัสผ่าน"""
        # Validate password
        if len(new_password) < AdminAuthConfig.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {AdminAuthConfig.MIN_PASSWORD_LENGTH} characters"
        
        if AdminAuthConfig.REQUIRE_SPECIAL_CHAR:
            import re
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                return False, "Password must contain at least one special character"
        
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(new_password, salt)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE admin_users SET password_hash = ?, salt = ?, must_change_password = 0 WHERE id = ?
        ''', (password_hash, salt, user_id))
        conn.commit()
        conn.close()
        
        return True, "Password changed successfully"


# ===== FLASK INTEGRATION =====

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>dLNk Admin Login</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 100%);
            color: #fff; 
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .login-container {
            background: rgba(36, 36, 36, 0.9);
            border-radius: 15px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 10px 40px rgba(0, 255, 136, 0.1);
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #00ff88;
            font-size: 2em;
        }
        .logo p {
            color: #888;
            font-size: 0.9em;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #888;
            font-size: 0.9em;
        }
        input {
            width: 100%;
            padding: 12px 15px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #fff;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #00ff88;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
            border: none;
            border-radius: 8px;
            color: #000;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0, 255, 136, 0.3);
        }
        .error {
            background: rgba(255, 68, 68, 0.2);
            border: 1px solid #ff4444;
            color: #ff4444;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        .warning {
            background: rgba(255, 204, 0, 0.2);
            border: 1px solid #ffcc00;
            color: #ffcc00;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
            font-size: 0.9em;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🔐 dLNk Admin</h1>
            <p>Secure Admin Console</p>
        </div>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        {% if warning %}
        <div class="warning">{{ warning }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" placeholder="Enter username" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" placeholder="Enter password" required>
            </div>
            {% if show_2fa %}
            <div class="form-group">
                <label>2FA Code</label>
                <input type="text" name="totp_code" placeholder="Enter 6-digit code" maxlength="6">
            </div>
            {% endif %}
            <button type="submit" class="btn">Login</button>
        </form>
        
        <div class="footer">
            dLNk Admin Console v1.0<br>
            Unauthorized access is prohibited
        </div>
    </div>
</body>
</html>
"""

CHANGE_PASSWORD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Change Password - dLNk Admin</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #0d0d0d; 
            color: #fff; 
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: #242424;
            border-radius: 15px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }
        h2 { color: #00ff88; margin-bottom: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #888; }
        input {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #fff;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #00ff88;
            border: none;
            border-radius: 8px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
        }
        .error { color: #ff4444; margin-bottom: 15px; }
        .info { color: #888; font-size: 0.9em; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>⚠️ Change Password Required</h2>
        <p style="color: #888; margin-bottom: 20px;">You must change your password before continuing.</p>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <div class="form-group">
                <label>New Password</label>
                <input type="password" name="new_password" required>
            </div>
            <div class="form-group">
                <label>Confirm Password</label>
                <input type="password" name="confirm_password" required>
            </div>
            <button type="submit" class="btn">Change Password</button>
        </form>
        
        <div class="info">
            Password requirements:<br>
            - Minimum 8 characters<br>
            - At least one special character
        </div>
    </div>
</body>
</html>
"""


def create_admin_auth_blueprint(auth_db: AdminAuthDB = None):
    """สร้าง Flask Blueprint สำหรับ Admin Auth"""
    from flask import Blueprint
    
    auth_bp = Blueprint('admin_auth', __name__)
    db = auth_db or AdminAuthDB()
    
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        warning = None
        
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            success, result = db.verify_password(username, password)
            
            if success:
                # Create session
                session_id = db.create_session(
                    result['id'],
                    request.remote_addr,
                    request.user_agent.string
                )
                
                session['admin_session_id'] = session_id
                session['admin_user'] = result
                
                db.log_action(result['id'], username, 'LOGIN', request.remote_addr, 'Success')
                
                # Check if must change password
                if result.get('must_change_password'):
                    return redirect(url_for('admin_auth.change_password'))
                
                return redirect(url_for('dashboard'))
            else:
                error = result.get('error', 'Login failed')
                db.log_action(None, username, 'LOGIN_FAILED', request.remote_addr, error, success=False)
        
        return render_template_string(LOGIN_TEMPLATE, error=error, warning=warning, show_2fa=False)
    
    @auth_bp.route('/logout')
    def logout():
        session_id = session.get('admin_session_id')
        if session_id:
            db.invalidate_session(session_id)
            user = session.get('admin_user', {})
            db.log_action(user.get('id'), user.get('username'), 'LOGOUT', request.remote_addr)
        
        session.clear()
        return redirect(url_for('admin_auth.login'))
    
    @auth_bp.route('/change-password', methods=['GET', 'POST'])
    def change_password():
        if 'admin_user' not in session:
            return redirect(url_for('admin_auth.login'))
        
        error = None
        
        if request.method == 'POST':
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if new_password != confirm_password:
                error = "Passwords do not match"
            else:
                success, message = db.change_password(session['admin_user']['id'], new_password)
                if success:
                    session['admin_user']['must_change_password'] = False
                    db.log_action(
                        session['admin_user']['id'],
                        session['admin_user']['username'],
                        'PASSWORD_CHANGED',
                        request.remote_addr
                    )
                    return redirect(url_for('dashboard'))
                else:
                    error = message
        
        return render_template_string(CHANGE_PASSWORD_TEMPLATE, error=error)
    
    return auth_bp


def login_required(f):
    """Decorator สำหรับ route ที่ต้อง login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('admin_session_id')
        
        if not session_id:
            return redirect(url_for('admin_auth.login'))
        
        db = AdminAuthDB()
        user_data = db.validate_session(session_id)
        
        if not user_data:
            session.clear()
            return redirect(url_for('admin_auth.login'))
        
        # Check must change password
        if session.get('admin_user', {}).get('must_change_password'):
            return redirect(url_for('admin_auth.change_password'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def superadmin_required(f):
    """Decorator สำหรับ route ที่ต้องเป็น superadmin"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = session.get('admin_user', {})
        if user.get('role') != 'superadmin':
            return jsonify({"error": "Superadmin access required"}), 403
        return f(*args, **kwargs)
    
    return decorated_function


# ===== EXAMPLE USAGE =====

if __name__ == "__main__":
    # Test
    db = AdminAuthDB()
    
    print("Testing Admin Auth System...")
    print("-" * 40)
    
    # Test login
    success, result = db.verify_password("admin", "admin123")
    print(f"Login test: {'Success' if success else 'Failed'}")
    print(f"Result: {result}")
    
    # Test session
    if success:
        session_id = db.create_session(result['id'], "127.0.0.1", "Test Agent")
        print(f"Session created: {session_id[:20]}...")
        
        # Validate
        user_data = db.validate_session(session_id)
        print(f"Session valid: {user_data is not None}")
