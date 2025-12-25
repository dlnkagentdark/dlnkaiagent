#!/usr/bin/env python3
"""
Anomaly Detector
ตรวจจับพฤติกรรมผิดปกติของผู้ใช้
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum

logger = logging.getLogger('AnomalyDetector')


class AnomalyType(Enum):
    """ประเภทความผิดปกติ"""
    EXCESSIVE_REQUESTS = "excessive_requests"
    BRUTE_FORCE_LOGIN = "brute_force_login"
    REPEATED_ATTACKS = "repeated_attacks"
    UNUSUAL_PATTERN = "unusual_pattern"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"


@dataclass
class AnomalyResult:
    """ผลการตรวจจับความผิดปกติ"""
    is_anomaly: bool
    anomaly_type: Optional[str] = None
    score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    recommended_action: Optional[str] = None


class AnomalyDetector:
    """
    Detect anomalous user behavior
    """
    
    def __init__(
        self,
        alert_manager=None,
        max_requests_per_minute: int = 60,
        max_failed_logins: int = 5,
        max_blocked_prompts: int = 3,
        window_minutes: int = 5
    ):
        self.alert_manager = alert_manager
        
        # Thresholds
        self.max_requests_per_minute = max_requests_per_minute
        self.max_failed_logins = max_failed_logins
        self.max_blocked_prompts = max_blocked_prompts
        self.window_minutes = window_minutes
        
        # Track user activities
        self.request_counts: Dict[str, List[datetime]] = defaultdict(list)
        self.failed_logins: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_prompts: Dict[str, List[datetime]] = defaultdict(list)
        
        # Anomaly history
        self.anomaly_history: Dict[str, List[AnomalyResult]] = defaultdict(list)
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "anomalies_detected": 0,
            "rate_limit_violations": 0,
            "brute_force_attempts": 0,
            "repeated_attacks": 0,
        }
    
    def _clean_old_entries(
        self,
        entries: List[datetime],
        window_minutes: int
    ) -> List[datetime]:
        """ลบ entries เก่า"""
        cutoff = datetime.now() - timedelta(minutes=window_minutes)
        return [ts for ts in entries if ts > cutoff]
    
    def check_request_rate(self, user_id: str) -> AnomalyResult:
        """ตรวจสอบอัตรา request"""
        now = datetime.now()
        
        # Clean old entries
        self.request_counts[user_id] = self._clean_old_entries(
            self.request_counts[user_id], 1
        )
        
        # Add current request
        self.request_counts[user_id].append(now)
        
        # Check rate
        count = len(self.request_counts[user_id])
        
        if count > self.max_requests_per_minute:
            score = count / self.max_requests_per_minute
            result = AnomalyResult(
                is_anomaly=True,
                anomaly_type=AnomalyType.EXCESSIVE_REQUESTS.value,
                score=score,
                details={
                    'requests_per_minute': count,
                    'threshold': self.max_requests_per_minute
                },
                recommended_action="rate_limit"
            )
            
            self._handle_anomaly(user_id, result)
            self.stats["rate_limit_violations"] += 1
            
            return result
        
        return AnomalyResult(is_anomaly=False)
    
    def check_failed_logins(self, user_id: str) -> AnomalyResult:
        """ตรวจสอบ brute force login"""
        now = datetime.now()
        
        # Clean old entries
        self.failed_logins[user_id] = self._clean_old_entries(
            self.failed_logins[user_id], self.window_minutes
        )
        
        # Add current failure
        self.failed_logins[user_id].append(now)
        
        # Check count
        count = len(self.failed_logins[user_id])
        
        if count >= self.max_failed_logins:
            score = count / self.max_failed_logins
            result = AnomalyResult(
                is_anomaly=True,
                anomaly_type=AnomalyType.BRUTE_FORCE_LOGIN.value,
                score=score,
                details={
                    'failed_attempts': count,
                    'window_minutes': self.window_minutes,
                    'threshold': self.max_failed_logins
                },
                recommended_action="block_login"
            )
            
            self._handle_anomaly(user_id, result)
            self.stats["brute_force_attempts"] += 1
            
            return result
        
        return AnomalyResult(is_anomaly=False)
    
    def check_blocked_prompts(self, user_id: str) -> AnomalyResult:
        """ตรวจสอบ repeated blocked prompts"""
        now = datetime.now()
        
        # Clean old entries
        self.blocked_prompts[user_id] = self._clean_old_entries(
            self.blocked_prompts[user_id], self.window_minutes
        )
        
        # Add current block
        self.blocked_prompts[user_id].append(now)
        
        # Check count
        count = len(self.blocked_prompts[user_id])
        
        if count >= self.max_blocked_prompts:
            score = count / self.max_blocked_prompts
            result = AnomalyResult(
                is_anomaly=True,
                anomaly_type=AnomalyType.REPEATED_ATTACKS.value,
                score=score,
                details={
                    'blocked_count': count,
                    'window_minutes': self.window_minutes,
                    'threshold': self.max_blocked_prompts
                },
                recommended_action="flag_user"
            )
            
            self._handle_anomaly(user_id, result)
            self.stats["repeated_attacks"] += 1
            
            return result
        
        return AnomalyResult(is_anomaly=False)
    
    def check_all(self, user_id: str, context: Dict[str, Any] = None) -> AnomalyResult:
        """ตรวจสอบทุกประเภท"""
        self.stats["total_checks"] += 1
        
        # Check request rate
        rate_result = self.check_request_rate(user_id)
        if rate_result.is_anomaly:
            return rate_result
        
        # Check context for specific checks
        context = context or {}
        
        if context.get("failed_login"):
            login_result = self.check_failed_logins(user_id)
            if login_result.is_anomaly:
                return login_result
        
        if context.get("blocked_prompt"):
            blocked_result = self.check_blocked_prompts(user_id)
            if blocked_result.is_anomaly:
                return blocked_result
        
        return AnomalyResult(is_anomaly=False)
    
    def _handle_anomaly(self, user_id: str, result: AnomalyResult):
        """จัดการเมื่อพบความผิดปกติ"""
        self.stats["anomalies_detected"] += 1
        
        # Store in history
        self.anomaly_history[user_id].append(result)
        
        # Keep only last 100 entries per user
        if len(self.anomaly_history[user_id]) > 100:
            self.anomaly_history[user_id] = self.anomaly_history[user_id][-100:]
        
        # Log
        logger.warning(
            f"Anomaly detected: {result.anomaly_type} "
            f"for user {user_id}, score: {result.score:.2f}"
        )
        
        # Alert
        if self.alert_manager:
            severity = 2 if result.score < 2 else 3
            self.alert_manager.send_alert(
                title=f"⚠️ Anomaly Detected: {result.anomaly_type}",
                message=(
                    f"User: {user_id}\n"
                    f"Score: {result.score:.2f}\n"
                    f"Details: {result.details}\n"
                    f"Recommended: {result.recommended_action}"
                ),
                severity=severity
            )
    
    def get_user_anomaly_history(self, user_id: str) -> List[AnomalyResult]:
        """ดึงประวัติความผิดปกติของ user"""
        return self.anomaly_history.get(user_id, [])
    
    def get_user_risk_score(self, user_id: str) -> float:
        """คำนวณ risk score ของ user"""
        history = self.anomaly_history.get(user_id, [])
        
        if not history:
            return 0.0
        
        # Calculate based on recent anomalies
        recent = history[-10:]  # Last 10 anomalies
        
        total_score = sum(a.score for a in recent)
        
        # Normalize to 0-10
        return min(total_score, 10.0)
    
    def is_user_blocked(self, user_id: str) -> bool:
        """ตรวจสอบว่า user ถูก block หรือไม่"""
        risk_score = self.get_user_risk_score(user_id)
        return risk_score >= 8.0
    
    def reset_user(self, user_id: str):
        """Reset ข้อมูลของ user"""
        self.request_counts.pop(user_id, None)
        self.failed_logins.pop(user_id, None)
        self.blocked_prompts.pop(user_id, None)
        self.anomaly_history.pop(user_id, None)
        logger.info(f"Reset anomaly data for user: {user_id}")
    
    def get_stats(self) -> Dict[str, int]:
        """ดึงสถิติ"""
        return self.stats.copy()
    
    def get_high_risk_users(self, threshold: float = 5.0) -> List[str]:
        """ดึง users ที่มี risk สูง"""
        high_risk = []
        for user_id in self.anomaly_history.keys():
            if self.get_user_risk_score(user_id) >= threshold:
                high_risk.append(user_id)
        return high_risk
