#!/usr/bin/env python3
"""
Rate Limiter
จำกัดอัตราการใช้งาน
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import threading

logger = logging.getLogger('RateLimiter')


@dataclass
class RateLimitConfig:
    """การตั้งค่า Rate Limit"""
    requests_per_minute: int = 60
    requests_per_hour: int = 500
    requests_per_day: int = 5000
    burst_limit: int = 10  # Max requests in 1 second
    cooldown_seconds: int = 60  # Cooldown after limit exceeded


@dataclass
class RateLimitStatus:
    """สถานะ Rate Limit"""
    allowed: bool
    remaining_minute: int
    remaining_hour: int
    remaining_day: int
    reset_time: Optional[str] = None
    message: Optional[str] = None


class RateLimiter:
    """
    Rate Limiter with multiple windows
    """
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        
        # Request tracking
        self.minute_counts: Dict[str, list] = defaultdict(list)
        self.hour_counts: Dict[str, list] = defaultdict(list)
        self.day_counts: Dict[str, list] = defaultdict(list)
        self.burst_counts: Dict[str, list] = defaultdict(list)
        
        # Blocked users
        self.blocked_until: Dict[str, datetime] = {}
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "allowed_requests": 0,
            "blocked_requests": 0,
            "minute_limit_hits": 0,
            "hour_limit_hits": 0,
            "day_limit_hits": 0,
            "burst_limit_hits": 0,
        }
    
    def _clean_old_entries(
        self,
        entries: list,
        window_seconds: int
    ) -> list:
        """ลบ entries เก่า"""
        cutoff = time.time() - window_seconds
        return [ts for ts in entries if ts > cutoff]
    
    def check(self, user_id: str) -> RateLimitStatus:
        """
        ตรวจสอบ rate limit
        
        Args:
            user_id: รหัสผู้ใช้
        
        Returns:
            RateLimitStatus
        """
        with self._lock:
            self.stats["total_requests"] += 1
            now = time.time()
            
            # Check if user is blocked
            if user_id in self.blocked_until:
                if datetime.now() < self.blocked_until[user_id]:
                    self.stats["blocked_requests"] += 1
                    return RateLimitStatus(
                        allowed=False,
                        remaining_minute=0,
                        remaining_hour=0,
                        remaining_day=0,
                        reset_time=self.blocked_until[user_id].isoformat(),
                        message="User is temporarily blocked"
                    )
                else:
                    del self.blocked_until[user_id]
            
            # Clean old entries
            self.burst_counts[user_id] = self._clean_old_entries(
                self.burst_counts[user_id], 1
            )
            self.minute_counts[user_id] = self._clean_old_entries(
                self.minute_counts[user_id], 60
            )
            self.hour_counts[user_id] = self._clean_old_entries(
                self.hour_counts[user_id], 3600
            )
            self.day_counts[user_id] = self._clean_old_entries(
                self.day_counts[user_id], 86400
            )
            
            # Check burst limit
            if len(self.burst_counts[user_id]) >= self.config.burst_limit:
                self.stats["burst_limit_hits"] += 1
                self.stats["blocked_requests"] += 1
                return RateLimitStatus(
                    allowed=False,
                    remaining_minute=0,
                    remaining_hour=0,
                    remaining_day=0,
                    message="Burst limit exceeded"
                )
            
            # Check minute limit
            if len(self.minute_counts[user_id]) >= self.config.requests_per_minute:
                self.stats["minute_limit_hits"] += 1
                self.stats["blocked_requests"] += 1
                self._apply_cooldown(user_id)
                return RateLimitStatus(
                    allowed=False,
                    remaining_minute=0,
                    remaining_hour=self.config.requests_per_hour - len(self.hour_counts[user_id]),
                    remaining_day=self.config.requests_per_day - len(self.day_counts[user_id]),
                    message="Minute limit exceeded"
                )
            
            # Check hour limit
            if len(self.hour_counts[user_id]) >= self.config.requests_per_hour:
                self.stats["hour_limit_hits"] += 1
                self.stats["blocked_requests"] += 1
                self._apply_cooldown(user_id, minutes=5)
                return RateLimitStatus(
                    allowed=False,
                    remaining_minute=0,
                    remaining_hour=0,
                    remaining_day=self.config.requests_per_day - len(self.day_counts[user_id]),
                    message="Hour limit exceeded"
                )
            
            # Check day limit
            if len(self.day_counts[user_id]) >= self.config.requests_per_day:
                self.stats["day_limit_hits"] += 1
                self.stats["blocked_requests"] += 1
                self._apply_cooldown(user_id, minutes=60)
                return RateLimitStatus(
                    allowed=False,
                    remaining_minute=0,
                    remaining_hour=0,
                    remaining_day=0,
                    message="Day limit exceeded"
                )
            
            # Add request to all windows
            self.burst_counts[user_id].append(now)
            self.minute_counts[user_id].append(now)
            self.hour_counts[user_id].append(now)
            self.day_counts[user_id].append(now)
            
            self.stats["allowed_requests"] += 1
            
            return RateLimitStatus(
                allowed=True,
                remaining_minute=self.config.requests_per_minute - len(self.minute_counts[user_id]),
                remaining_hour=self.config.requests_per_hour - len(self.hour_counts[user_id]),
                remaining_day=self.config.requests_per_day - len(self.day_counts[user_id])
            )
    
    def _apply_cooldown(self, user_id: str, minutes: int = None):
        """Apply cooldown to user"""
        minutes = minutes or (self.config.cooldown_seconds // 60)
        self.blocked_until[user_id] = datetime.now() + timedelta(minutes=minutes)
        logger.warning(f"User {user_id} blocked for {minutes} minutes")
    
    def is_allowed(self, user_id: str) -> bool:
        """Quick check if request is allowed"""
        return self.check(user_id).allowed
    
    def get_remaining(self, user_id: str) -> Dict[str, int]:
        """Get remaining requests"""
        with self._lock:
            return {
                "minute": self.config.requests_per_minute - len(self.minute_counts.get(user_id, [])),
                "hour": self.config.requests_per_hour - len(self.hour_counts.get(user_id, [])),
                "day": self.config.requests_per_day - len(self.day_counts.get(user_id, []))
            }
    
    def reset_user(self, user_id: str):
        """Reset user's rate limit"""
        with self._lock:
            self.burst_counts.pop(user_id, None)
            self.minute_counts.pop(user_id, None)
            self.hour_counts.pop(user_id, None)
            self.day_counts.pop(user_id, None)
            self.blocked_until.pop(user_id, None)
            logger.info(f"Rate limit reset for user: {user_id}")
    
    def block_user(self, user_id: str, minutes: int = 60):
        """Manually block user"""
        with self._lock:
            self.blocked_until[user_id] = datetime.now() + timedelta(minutes=minutes)
            logger.warning(f"User {user_id} manually blocked for {minutes} minutes")
    
    def unblock_user(self, user_id: str):
        """Unblock user"""
        with self._lock:
            self.blocked_until.pop(user_id, None)
            logger.info(f"User {user_id} unblocked")
    
    def get_blocked_users(self) -> Dict[str, str]:
        """Get all blocked users"""
        with self._lock:
            now = datetime.now()
            return {
                user_id: until.isoformat()
                for user_id, until in self.blocked_until.items()
                if until > now
            }
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics"""
        return self.stats.copy()


class TokenBucketRateLimiter:
    """
    Token Bucket Rate Limiter
    More flexible rate limiting algorithm
    """
    
    def __init__(
        self,
        capacity: int = 100,
        refill_rate: float = 10.0,  # tokens per second
        initial_tokens: int = None
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate
        
        # User buckets
        self.buckets: Dict[str, Dict[str, float]] = {}
        
        self._lock = threading.Lock()
    
    def _get_bucket(self, user_id: str) -> Dict[str, float]:
        """Get or create bucket for user"""
        if user_id not in self.buckets:
            self.buckets[user_id] = {
                "tokens": float(self.capacity),
                "last_update": time.time()
            }
        return self.buckets[user_id]
    
    def _refill(self, bucket: Dict[str, float]):
        """Refill bucket based on time elapsed"""
        now = time.time()
        elapsed = now - bucket["last_update"]
        
        new_tokens = bucket["tokens"] + (elapsed * self.refill_rate)
        bucket["tokens"] = min(new_tokens, float(self.capacity))
        bucket["last_update"] = now
    
    def consume(self, user_id: str, tokens: int = 1) -> Tuple[bool, float]:
        """
        Try to consume tokens
        
        Returns:
            Tuple[bool, float]: (allowed, remaining_tokens)
        """
        with self._lock:
            bucket = self._get_bucket(user_id)
            self._refill(bucket)
            
            if bucket["tokens"] >= tokens:
                bucket["tokens"] -= tokens
                return True, bucket["tokens"]
            else:
                return False, bucket["tokens"]
    
    def get_tokens(self, user_id: str) -> float:
        """Get current tokens for user"""
        with self._lock:
            bucket = self._get_bucket(user_id)
            self._refill(bucket)
            return bucket["tokens"]
    
    def reset_user(self, user_id: str):
        """Reset user's bucket"""
        with self._lock:
            self.buckets.pop(user_id, None)
