#!/usr/bin/env python3
"""
Brute Force Detection
ตรวจจับการโจมตีแบบ Brute Force
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import threading
import hashlib

logger = logging.getLogger('BruteForceDetector')


@dataclass
class BruteForceConfig:
    """การตั้งค่า Brute Force Detection"""
    max_attempts: int = 5
    window_minutes: int = 5
    lockout_minutes: int = 15
    progressive_lockout: bool = True  # Increase lockout on repeated violations
    max_lockout_minutes: int = 60


@dataclass
class BruteForceAttempt:
    """ข้อมูลการพยายาม"""
    timestamp: str
    user_id: str
    target: str  # What was being accessed (login, api, etc.)
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class BruteForceStatus:
    """สถานะ Brute Force"""
    is_blocked: bool
    attempts: int
    remaining_attempts: int
    lockout_until: Optional[str] = None
    message: Optional[str] = None


class BruteForceDetector:
    """
    Detect and prevent brute force attacks
    """
    
    def __init__(
        self,
        config: BruteForceConfig = None,
        alert_manager=None
    ):
        self.config = config or BruteForceConfig()
        self.alert_manager = alert_manager
        
        # Track attempts: key -> list of timestamps
        self.attempts: Dict[str, List[datetime]] = defaultdict(list)
        
        # Lockouts: key -> (lockout_until, violation_count)
        self.lockouts: Dict[str, Tuple[datetime, int]] = {}
        
        # History for reporting
        self.attempt_history: List[BruteForceAttempt] = []
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "total_attempts": 0,
            "blocked_attempts": 0,
            "lockouts_applied": 0,
            "unique_attackers": 0,
        }
    
    def _make_key(self, user_id: str, target: str, ip_address: str = None) -> str:
        """สร้าง key สำหรับ tracking"""
        # Combine user_id and IP for more accurate tracking
        key_parts = [user_id, target]
        if ip_address:
            key_parts.append(ip_address)
        return hashlib.sha256(":".join(key_parts).encode()).hexdigest()[:16]
    
    def _clean_old_attempts(self, key: str):
        """ลบ attempts เก่า"""
        cutoff = datetime.now() - timedelta(minutes=self.config.window_minutes)
        self.attempts[key] = [ts for ts in self.attempts[key] if ts > cutoff]
    
    def record_attempt(
        self,
        user_id: str,
        target: str,
        success: bool,
        ip_address: str = None,
        details: Dict[str, Any] = None
    ) -> BruteForceStatus:
        """
        บันทึกการพยายาม
        
        Args:
            user_id: รหัสผู้ใช้
            target: เป้าหมาย (login, api, license, etc.)
            success: สำเร็จหรือไม่
            ip_address: IP address
            details: รายละเอียดเพิ่มเติม
        
        Returns:
            BruteForceStatus
        """
        with self._lock:
            key = self._make_key(user_id, target, ip_address)
            now = datetime.now()
            
            self.stats["total_attempts"] += 1
            
            # Check if currently locked out
            if key in self.lockouts:
                lockout_until, _ = self.lockouts[key]
                if now < lockout_until:
                    self.stats["blocked_attempts"] += 1
                    return BruteForceStatus(
                        is_blocked=True,
                        attempts=len(self.attempts.get(key, [])),
                        remaining_attempts=0,
                        lockout_until=lockout_until.isoformat(),
                        message=f"Account locked until {lockout_until.strftime('%H:%M:%S')}"
                    )
                else:
                    # Lockout expired
                    del self.lockouts[key]
            
            # If successful, reset attempts
            if success:
                self.attempts.pop(key, None)
                return BruteForceStatus(
                    is_blocked=False,
                    attempts=0,
                    remaining_attempts=self.config.max_attempts
                )
            
            # Record failed attempt
            self._clean_old_attempts(key)
            self.attempts[key].append(now)
            
            # Store in history
            self.attempt_history.append(BruteForceAttempt(
                timestamp=now.isoformat(),
                user_id=user_id,
                target=target,
                ip_address=ip_address,
                details=details
            ))
            
            # Keep history manageable
            if len(self.attempt_history) > 10000:
                self.attempt_history = self.attempt_history[-5000:]
            
            attempt_count = len(self.attempts[key])
            remaining = self.config.max_attempts - attempt_count
            
            # Check if threshold exceeded
            if attempt_count >= self.config.max_attempts:
                self._apply_lockout(key, user_id, target, ip_address)
                
                return BruteForceStatus(
                    is_blocked=True,
                    attempts=attempt_count,
                    remaining_attempts=0,
                    lockout_until=self.lockouts[key][0].isoformat(),
                    message="Too many failed attempts. Account locked."
                )
            
            return BruteForceStatus(
                is_blocked=False,
                attempts=attempt_count,
                remaining_attempts=remaining,
                message=f"{remaining} attempts remaining"
            )
    
    def _apply_lockout(
        self,
        key: str,
        user_id: str,
        target: str,
        ip_address: str = None
    ):
        """Apply lockout"""
        # Get previous violation count
        _, prev_violations = self.lockouts.get(key, (None, 0))
        violations = prev_violations + 1
        
        # Calculate lockout duration
        if self.config.progressive_lockout:
            lockout_minutes = min(
                self.config.lockout_minutes * (2 ** (violations - 1)),
                self.config.max_lockout_minutes
            )
        else:
            lockout_minutes = self.config.lockout_minutes
        
        lockout_until = datetime.now() + timedelta(minutes=lockout_minutes)
        self.lockouts[key] = (lockout_until, violations)
        
        self.stats["lockouts_applied"] += 1
        
        logger.warning(
            f"Brute force lockout applied: user={user_id}, target={target}, "
            f"ip={ip_address}, duration={lockout_minutes}min"
        )
        
        # Alert
        if self.alert_manager:
            self.alert_manager.send_alert(
                title="🔒 Brute Force Detected",
                message=(
                    f"User: {user_id}\n"
                    f"Target: {target}\n"
                    f"IP: {ip_address or 'Unknown'}\n"
                    f"Lockout: {lockout_minutes} minutes\n"
                    f"Violations: {violations}"
                ),
                severity=3
            )
    
    def check_status(
        self,
        user_id: str,
        target: str,
        ip_address: str = None
    ) -> BruteForceStatus:
        """ตรวจสอบสถานะ"""
        with self._lock:
            key = self._make_key(user_id, target, ip_address)
            now = datetime.now()
            
            # Check lockout
            if key in self.lockouts:
                lockout_until, _ = self.lockouts[key]
                if now < lockout_until:
                    return BruteForceStatus(
                        is_blocked=True,
                        attempts=len(self.attempts.get(key, [])),
                        remaining_attempts=0,
                        lockout_until=lockout_until.isoformat()
                    )
            
            # Get current attempts
            self._clean_old_attempts(key)
            attempt_count = len(self.attempts.get(key, []))
            
            return BruteForceStatus(
                is_blocked=False,
                attempts=attempt_count,
                remaining_attempts=self.config.max_attempts - attempt_count
            )
    
    def is_blocked(
        self,
        user_id: str,
        target: str,
        ip_address: str = None
    ) -> bool:
        """Quick check if blocked"""
        return self.check_status(user_id, target, ip_address).is_blocked
    
    def reset_user(
        self,
        user_id: str,
        target: str = None,
        ip_address: str = None
    ):
        """Reset user's attempts and lockout"""
        with self._lock:
            if target:
                key = self._make_key(user_id, target, ip_address)
                self.attempts.pop(key, None)
                self.lockouts.pop(key, None)
            else:
                # Reset all targets for user
                keys_to_remove = [
                    k for k in list(self.attempts.keys()) + list(self.lockouts.keys())
                    if user_id in str(k)
                ]
                for key in keys_to_remove:
                    self.attempts.pop(key, None)
                    self.lockouts.pop(key, None)
            
            logger.info(f"Brute force reset for user: {user_id}")
    
    def get_recent_attempts(
        self,
        user_id: str = None,
        target: str = None,
        limit: int = 100
    ) -> List[BruteForceAttempt]:
        """ดึง attempts ล่าสุด"""
        attempts = self.attempt_history
        
        if user_id:
            attempts = [a for a in attempts if a.user_id == user_id]
        
        if target:
            attempts = [a for a in attempts if a.target == target]
        
        return attempts[-limit:]
    
    def get_active_lockouts(self) -> Dict[str, Dict[str, Any]]:
        """ดึง lockouts ที่ยัง active"""
        with self._lock:
            now = datetime.now()
            active = {}
            
            for key, (until, violations) in self.lockouts.items():
                if until > now:
                    active[key] = {
                        "lockout_until": until.isoformat(),
                        "violations": violations,
                        "remaining_minutes": (until - now).seconds // 60
                    }
            
            return active
    
    def get_stats(self) -> Dict[str, int]:
        """ดึงสถิติ"""
        stats = self.stats.copy()
        stats["active_lockouts"] = len([
            1 for until, _ in self.lockouts.values()
            if until > datetime.now()
        ])
        return stats
