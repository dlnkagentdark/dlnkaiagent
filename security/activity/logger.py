#!/usr/bin/env python3
"""
Activity Logger
บันทึกทุกการใช้งาน AI และกิจกรรมของผู้ใช้
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger('ActivityLogger')


class ActivityType(Enum):
    """ประเภทกิจกรรม"""
    LOGIN = "login"
    LOGOUT = "logout"
    AI_REQUEST = "ai_request"
    AI_RESPONSE = "ai_response"
    LICENSE_CHECK = "license_check"
    LICENSE_ACTIVATE = "license_activate"
    ADMIN_ACTION = "admin_action"
    SECURITY_EVENT = "security_event"
    ERROR = "error"
    SYSTEM = "system"


@dataclass
class ActivityLog:
    """โครงสร้างข้อมูล Activity Log"""
    timestamp: str
    user_id: str
    action: str
    action_type: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    hwid: Optional[str] = None
    success: bool = True
    duration_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ActivityLogger:
    """
    Log all user activities
    """
    
    def __init__(
        self,
        log_dir: str = None,
        encrypt: bool = False,
        max_log_size_mb: int = 100
    ):
        self.log_dir = Path(log_dir) if log_dir else Path.home() / ".dlnk-ide" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.encrypt = encrypt
        self.max_log_size_mb = max_log_size_mb
        
        # Log files
        self.activity_log = self.log_dir / "activity.log"
        self.activity_json = self.log_dir / "activity.json"
        
        # Encryption handler (lazy load)
        self._encryption = None
        
        # Statistics
        self.stats = {
            "total_activities": 0,
            "logins": 0,
            "logouts": 0,
            "ai_requests": 0,
            "errors": 0,
            "security_events": 0,
        }
    
    @property
    def encryption(self):
        """Lazy load encryption"""
        if self._encryption is None and self.encrypt:
            try:
                from ..encryption.log_encryption import LogEncryption
                self._encryption = LogEncryption()
            except ImportError:
                logger.warning("Encryption module not available")
                self.encrypt = False
        return self._encryption
    
    def log(
        self,
        user_id: str,
        action: str,
        action_type: ActivityType = ActivityType.SYSTEM,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        session_id: str = None,
        hwid: str = None,
        success: bool = True,
        duration_ms: int = None,
        metadata: Dict[str, Any] = None
    ) -> ActivityLog:
        """
        บันทึกกิจกรรม
        
        Args:
            user_id: รหัสผู้ใช้
            action: คำอธิบายกิจกรรม
            action_type: ประเภทกิจกรรม
            details: รายละเอียดเพิ่มเติม
            ip_address: IP address
            session_id: Session ID
            hwid: Hardware ID
            success: สำเร็จหรือไม่
            duration_ms: ระยะเวลา (ms)
            metadata: ข้อมูลเพิ่มเติม
        
        Returns:
            ActivityLog object
        """
        entry = ActivityLog(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            action=action,
            action_type=action_type.value,
            details=details or {},
            ip_address=ip_address,
            session_id=session_id,
            hwid=hwid,
            success=success,
            duration_ms=duration_ms,
            metadata=metadata
        )
        
        self._write_log(entry)
        self._update_stats(action_type, success)
        
        return entry
    
    def log_login(
        self,
        user_id: str,
        ip_address: str = None,
        hwid: str = None,
        success: bool = True,
        details: Dict[str, Any] = None
    ) -> ActivityLog:
        """บันทึก Login"""
        return self.log(
            user_id=user_id,
            action="User login" if success else "Login failed",
            action_type=ActivityType.LOGIN,
            details=details or {},
            ip_address=ip_address,
            hwid=hwid,
            success=success
        )
    
    def log_logout(
        self,
        user_id: str,
        session_id: str = None,
        duration_ms: int = None
    ) -> ActivityLog:
        """บันทึก Logout"""
        return self.log(
            user_id=user_id,
            action="User logout",
            action_type=ActivityType.LOGOUT,
            session_id=session_id,
            duration_ms=duration_ms
        )
    
    def log_ai_request(
        self,
        user_id: str,
        prompt_hash: str,
        prompt_length: int,
        model: str = None,
        session_id: str = None,
        ip_address: str = None
    ) -> ActivityLog:
        """บันทึก AI Request"""
        return self.log(
            user_id=user_id,
            action="AI request",
            action_type=ActivityType.AI_REQUEST,
            details={
                "prompt_hash": prompt_hash,
                "prompt_length": prompt_length,
                "model": model
            },
            session_id=session_id,
            ip_address=ip_address
        )
    
    def log_ai_response(
        self,
        user_id: str,
        response_length: int,
        tokens_used: int = None,
        duration_ms: int = None,
        success: bool = True,
        error: str = None
    ) -> ActivityLog:
        """บันทึก AI Response"""
        details = {
            "response_length": response_length,
            "tokens_used": tokens_used
        }
        if error:
            details["error"] = error
        
        return self.log(
            user_id=user_id,
            action="AI response" if success else "AI error",
            action_type=ActivityType.AI_RESPONSE,
            details=details,
            success=success,
            duration_ms=duration_ms
        )
    
    def log_security_event(
        self,
        user_id: str,
        event: str,
        severity: int,
        details: Dict[str, Any] = None,
        ip_address: str = None
    ) -> ActivityLog:
        """บันทึก Security Event"""
        return self.log(
            user_id=user_id,
            action=f"Security event: {event}",
            action_type=ActivityType.SECURITY_EVENT,
            details={
                "event": event,
                "severity": severity,
                **(details or {})
            },
            ip_address=ip_address,
            success=False
        )
    
    def log_error(
        self,
        user_id: str,
        error: str,
        error_type: str = None,
        stack_trace: str = None
    ) -> ActivityLog:
        """บันทึก Error"""
        return self.log(
            user_id=user_id,
            action=f"Error: {error[:100]}",
            action_type=ActivityType.ERROR,
            details={
                "error": error,
                "error_type": error_type,
                "stack_trace": stack_trace
            },
            success=False
        )
    
    def _write_log(self, entry: ActivityLog):
        """เขียน log ลงไฟล์"""
        self.stats["total_activities"] += 1
        
        entry_dict = asdict(entry)
        
        # Encrypt if enabled
        if self.encrypt and self.encryption:
            try:
                entry_dict = self.encryption.encrypt_dict(entry_dict)
            except Exception as e:
                logger.error(f"Encryption failed: {e}")
        
        # Write to JSON file
        try:
            with open(self.activity_json, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry_dict, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write JSON log: {e}")
        
        # Write to text log
        try:
            log_line = (
                f"[{entry.timestamp}] [{entry.action_type}] "
                f"user={entry.user_id} action={entry.action} "
                f"success={entry.success}"
            )
            with open(self.activity_log, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            logger.error(f"Failed to write text log: {e}")
    
    def _update_stats(self, action_type: ActivityType, success: bool):
        """อัปเดตสถิติ"""
        if action_type == ActivityType.LOGIN:
            self.stats["logins"] += 1
        elif action_type == ActivityType.LOGOUT:
            self.stats["logouts"] += 1
        elif action_type == ActivityType.AI_REQUEST:
            self.stats["ai_requests"] += 1
        elif action_type == ActivityType.ERROR:
            self.stats["errors"] += 1
        elif action_type == ActivityType.SECURITY_EVENT:
            self.stats["security_events"] += 1
    
    def get_stats(self) -> Dict[str, int]:
        """ดึงสถิติ"""
        return self.stats.copy()
    
    def get_recent_activities(
        self,
        limit: int = 100,
        user_id: str = None,
        action_type: ActivityType = None
    ) -> List[ActivityLog]:
        """ดึงกิจกรรมล่าสุด"""
        activities = []
        
        try:
            if not self.activity_json.exists():
                return activities
            
            with open(self.activity_json, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        
                        # Decrypt if needed
                        if self.encrypt and self.encryption:
                            try:
                                data = self.encryption.decrypt_dict(data)
                            except:
                                pass
                        
                        # Filter
                        if user_id and data.get("user_id") != user_id:
                            continue
                        if action_type and data.get("action_type") != action_type.value:
                            continue
                        
                        activities.append(ActivityLog(**data))
                    except (json.JSONDecodeError, TypeError):
                        continue
            
            return activities[-limit:]
        except Exception as e:
            logger.error(f"Failed to read activities: {e}")
            return []
    
    def get_user_activity_summary(self, user_id: str) -> Dict[str, Any]:
        """ดึงสรุปกิจกรรมของ user"""
        activities = self.get_recent_activities(limit=1000, user_id=user_id)
        
        if not activities:
            return {"user_id": user_id, "total_activities": 0}
        
        return {
            "user_id": user_id,
            "total_activities": len(activities),
            "first_activity": activities[0].timestamp if activities else None,
            "last_activity": activities[-1].timestamp if activities else None,
            "logins": sum(1 for a in activities if a.action_type == "login"),
            "ai_requests": sum(1 for a in activities if a.action_type == "ai_request"),
            "errors": sum(1 for a in activities if a.action_type == "error"),
            "security_events": sum(1 for a in activities if a.action_type == "security_event"),
        }
