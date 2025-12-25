#!/usr/bin/env python3
"""
dLNk Admin Console - Authentication Module
"""

import os
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

# Optional TOTP support
try:
    import pyotp
    TOTP_AVAILABLE = True
except ImportError:
    TOTP_AVAILABLE = False


class AdminAuth:
    """Admin Authentication Handler"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".dlnk-ide"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.config_dir / "admin_session.json"
        self.current_session = None
        self._load_session()
    
    def _load_session(self):
        """Load existing session from file"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session = json.load(f)
                    # Check if session is still valid
                    if session.get('expires_at'):
                        expires = datetime.fromisoformat(session['expires_at'])
                        if datetime.now() < expires:
                            self.current_session = session
        except Exception:
            pass
    
    def _save_session(self):
        """Save session to file"""
        try:
            if self.current_session:
                with open(self.session_file, 'w') as f:
                    json.dump(self.current_session, f)
            elif self.session_file.exists():
                self.session_file.unlink()
        except Exception:
            pass
    
    def login(self, admin_key: str, totp_code: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate with admin key and optional TOTP
        Returns: (success, message, admin_data)
        """
        # Validate admin key format
        if not admin_key:
            return False, "Admin Key is required", None
        
        # Check for valid admin key patterns
        valid_prefixes = ['DLNK-ADMIN-', 'DLNK-SUPER-', 'DLNK-DEV-']
        is_valid_format = any(admin_key.startswith(prefix) for prefix in valid_prefixes)
        
        if not is_valid_format:
            return False, "Invalid Admin Key format", None
        
        # Determine role based on key prefix
        if admin_key.startswith('DLNK-SUPER-'):
            role = 'superadmin'
        elif admin_key.startswith('DLNK-DEV-'):
            role = 'developer'
        else:
            role = 'admin'
        
        # Verify TOTP if provided and available
        if TOTP_AVAILABLE and totp_code:
            # In production, verify against stored TOTP secret
            # For now, we'll accept any 6-digit code
            if not (totp_code.isdigit() and len(totp_code) == 6):
                return False, "Invalid 2FA code format", None
        
        # Create session
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        admin_data = {
            'session_id': session_id,
            'admin_key': admin_key[:20] + '***',  # Mask key for security
            'role': role,
            'username': f"Admin-{admin_key[11:15]}",
            'logged_in_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'has_2fa': bool(totp_code),
        }
        
        self.current_session = admin_data
        self._save_session()
        
        return True, "Login successful", admin_data
    
    def logout(self):
        """Logout and clear session"""
        self.current_session = None
        self._save_session()
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        if not self.current_session:
            return False
        
        # Check expiry
        if self.current_session.get('expires_at'):
            expires = datetime.fromisoformat(self.current_session['expires_at'])
            if datetime.now() >= expires:
                self.logout()
                return False
        
        return True
    
    def get_session(self) -> Optional[Dict]:
        """Get current session data"""
        if self.is_authenticated():
            return self.current_session
        return None
    
    def get_role(self) -> str:
        """Get current user role"""
        if self.current_session:
            return self.current_session.get('role', 'guest')
        return 'guest'
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        role = self.get_role()
        
        permissions = {
            'superadmin': ['all', 'create_license', 'revoke_license', 'manage_users', 'view_logs', 'manage_settings', 'manage_tokens'],
            'admin': ['create_license', 'revoke_license', 'view_logs', 'manage_tokens'],
            'developer': ['view_logs', 'manage_tokens'],
            'guest': [],
        }
        
        user_permissions = permissions.get(role, [])
        return 'all' in user_permissions or permission in user_permissions
    
    def refresh_session(self) -> bool:
        """Refresh session expiry"""
        if self.is_authenticated():
            self.current_session['expires_at'] = (datetime.now() + timedelta(hours=24)).isoformat()
            self._save_session()
            return True
        return False
