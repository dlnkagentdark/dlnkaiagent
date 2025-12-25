#!/usr/bin/env python3
"""
User Activity Tracker
ติดตามกิจกรรมผู้ใช้แบบ Real-time
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import threading

logger = logging.getLogger('ActivityTracker')


@dataclass
class UserSession:
    """ข้อมูล Session ของผู้ใช้"""
    user_id: str
    session_id: str
    hwid: Optional[str] = None
    ip_address: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    request_count: int = 0
    blocked_count: int = 0
    is_active: bool = True


@dataclass
class UserProfile:
    """โปรไฟล์ผู้ใช้สำหรับ Tracking"""
    user_id: str
    first_seen: str
    last_seen: str
    total_sessions: int = 0
    total_requests: int = 0
    total_blocked: int = 0
    risk_score: float = 0.0
    is_flagged: bool = False
    notes: List[str] = field(default_factory=list)


class ActivityTracker:
    """
    ติดตามกิจกรรมผู้ใช้แบบ Real-time
    """
    
    def __init__(self, max_sessions_per_user: int = 5):
        self.max_sessions_per_user = max_sessions_per_user
        
        # Active sessions: user_id -> list of sessions
        self.active_sessions: Dict[str, List[UserSession]] = defaultdict(list)
        
        # User profiles: user_id -> UserProfile
        self.user_profiles: Dict[str, UserProfile] = {}
        
        # Request tracking: user_id -> list of timestamps
        self.request_history: Dict[str, List[datetime]] = defaultdict(list)
        
        # Lock for thread safety
        self._lock = threading.Lock()
    
    def start_session(
        self,
        user_id: str,
        session_id: str,
        hwid: str = None,
        ip_address: str = None
    ) -> UserSession:
        """เริ่ม session ใหม่"""
        with self._lock:
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                hwid=hwid,
                ip_address=ip_address
            )
            
            # Add to active sessions
            self.active_sessions[user_id].append(session)
            
            # Limit sessions per user
            if len(self.active_sessions[user_id]) > self.max_sessions_per_user:
                # Remove oldest session
                self.active_sessions[user_id].pop(0)
            
            # Update user profile
            self._update_profile(user_id, new_session=True)
            
            logger.info(f"Session started: user={user_id}, session={session_id}")
            
            return session
    
    def end_session(self, user_id: str, session_id: str) -> Optional[UserSession]:
        """จบ session"""
        with self._lock:
            sessions = self.active_sessions.get(user_id, [])
            
            for i, session in enumerate(sessions):
                if session.session_id == session_id:
                    session.is_active = False
                    sessions.pop(i)
                    logger.info(f"Session ended: user={user_id}, session={session_id}")
                    return session
            
            return None
    
    def record_activity(
        self,
        user_id: str,
        session_id: str = None,
        is_blocked: bool = False
    ):
        """บันทึกกิจกรรม"""
        with self._lock:
            now = datetime.now()
            
            # Update request history
            self.request_history[user_id].append(now)
            
            # Clean old history (keep last hour)
            cutoff = now - timedelta(hours=1)
            self.request_history[user_id] = [
                ts for ts in self.request_history[user_id]
                if ts > cutoff
            ]
            
            # Update session
            if session_id:
                for session in self.active_sessions.get(user_id, []):
                    if session.session_id == session_id:
                        session.last_activity = now.isoformat()
                        session.request_count += 1
                        if is_blocked:
                            session.blocked_count += 1
                        break
            
            # Update profile
            self._update_profile(user_id, is_blocked=is_blocked)
    
    def _update_profile(
        self,
        user_id: str,
        new_session: bool = False,
        is_blocked: bool = False
    ):
        """อัปเดตโปรไฟล์ผู้ใช้"""
        now = datetime.now().isoformat()
        
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                first_seen=now,
                last_seen=now
            )
        
        profile = self.user_profiles[user_id]
        profile.last_seen = now
        profile.total_requests += 1
        
        if new_session:
            profile.total_sessions += 1
        
        if is_blocked:
            profile.total_blocked += 1
            # Update risk score
            profile.risk_score = self._calculate_risk_score(profile)
    
    def _calculate_risk_score(self, profile: UserProfile) -> float:
        """คำนวณ Risk Score"""
        if profile.total_requests == 0:
            return 0.0
        
        # Block ratio
        block_ratio = profile.total_blocked / profile.total_requests
        
        # Recent activity (last hour)
        recent_requests = len(self.request_history.get(profile.user_id, []))
        
        # Calculate score (0-10)
        score = 0.0
        
        # High block ratio increases score
        if block_ratio > 0.5:
            score += 5.0
        elif block_ratio > 0.2:
            score += 3.0
        elif block_ratio > 0.1:
            score += 1.0
        
        # High request rate increases score
        if recent_requests > 100:
            score += 3.0
        elif recent_requests > 50:
            score += 1.5
        
        # Multiple blocked requests
        if profile.total_blocked > 10:
            score += 2.0
        elif profile.total_blocked > 5:
            score += 1.0
        
        return min(score, 10.0)
    
    def get_active_sessions(self, user_id: str = None) -> List[UserSession]:
        """ดึง active sessions"""
        with self._lock:
            if user_id:
                return self.active_sessions.get(user_id, []).copy()
            
            all_sessions = []
            for sessions in self.active_sessions.values():
                all_sessions.extend(sessions)
            return all_sessions
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """ดึงโปรไฟล์ผู้ใช้"""
        return self.user_profiles.get(user_id)
    
    def get_request_rate(self, user_id: str, window_minutes: int = 1) -> int:
        """ดึงอัตรา request ต่อนาที"""
        with self._lock:
            now = datetime.now()
            cutoff = now - timedelta(minutes=window_minutes)
            
            history = self.request_history.get(user_id, [])
            return sum(1 for ts in history if ts > cutoff)
    
    def get_high_risk_users(self, threshold: float = 5.0) -> List[UserProfile]:
        """ดึงผู้ใช้ที่มี risk สูง"""
        return [
            profile for profile in self.user_profiles.values()
            if profile.risk_score >= threshold
        ]
    
    def flag_user(self, user_id: str, note: str = None):
        """Flag ผู้ใช้"""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            profile.is_flagged = True
            if note:
                profile.notes.append(f"[{datetime.now().isoformat()}] {note}")
            logger.warning(f"User flagged: {user_id}")
    
    def unflag_user(self, user_id: str):
        """Unflag ผู้ใช้"""
        if user_id in self.user_profiles:
            self.user_profiles[user_id].is_flagged = False
            logger.info(f"User unflagged: {user_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """ดึงสถิติ"""
        with self._lock:
            total_active = sum(
                len(sessions) for sessions in self.active_sessions.values()
            )
            
            return {
                "total_users": len(self.user_profiles),
                "active_sessions": total_active,
                "flagged_users": sum(
                    1 for p in self.user_profiles.values() if p.is_flagged
                ),
                "high_risk_users": len(self.get_high_risk_users()),
            }
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = 30):
        """ลบ sessions ที่ไม่ active"""
        with self._lock:
            cutoff = datetime.now() - timedelta(minutes=timeout_minutes)
            
            for user_id in list(self.active_sessions.keys()):
                self.active_sessions[user_id] = [
                    session for session in self.active_sessions[user_id]
                    if datetime.fromisoformat(session.last_activity) > cutoff
                ]
                
                if not self.active_sessions[user_id]:
                    del self.active_sessions[user_id]
