#!/usr/bin/env python3
"""
dLNk Token Harvester Integration
=================================
Module สำหรับเชื่อมต่อ AI Bridge กับ Token Harvester

Features:
- ดึง token จาก Token Harvester API
- รายงาน token ที่ quota หมด
- Token caching และ refresh
- Statistics tracking

Author: dLNk IDE Project (AI-01 The Architect)
Date: December 25, 2025
"""

import os
import time
import logging
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenData:
    """โครงสร้างข้อมูล Token"""
    account_id: str
    email: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None
    fetched_at: float = field(default_factory=time.time)
    
    @property
    def is_expired(self) -> bool:
        """ตรวจสอบว่า token หมดอายุหรือไม่"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


@dataclass
class TokenStats:
    """สถิติการใช้งาน Token"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    tokens_exhausted: int = 0
    tokens_refreshed: int = 0
    last_request: Optional[datetime] = None


class TokenIntegration:
    """
    Token Harvester Integration Client
    
    ใช้งาน:
    ```python
    integration = TokenIntegration(harvester_url="http://localhost:8888")
    
    # ดึง token
    token = integration.get_valid_token()
    
    # รายงาน quota หมด
    integration.report_exhausted_token(token['account_id'])
    ```
    """
    
    def __init__(
        self,
        harvester_url: str = "http://localhost:8888",
        cache_ttl: int = 300,  # 5 นาที
        max_retries: int = 3
    ):
        self.harvester_url = harvester_url.rstrip('/')
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries
        
        self._cache: Dict[str, TokenData] = {}
        self._cache_lock = threading.Lock()
        self._stats = TokenStats()
        self._last_token_id: Optional[str] = None
        
    def get_valid_token(self) -> Optional[Dict[str, Any]]:
        """
        ดึง token ที่พร้อมใช้งาน
        
        Returns:
            Dict containing token data or None if no token available
        """
        self._stats.total_requests += 1
        self._stats.last_request = datetime.now()
        
        # ลองใช้ cached token ก่อน
        cached = self._get_cached_token()
        if cached and not cached.is_expired:
            self._stats.successful_requests += 1
            return {
                "account_id": cached.account_id,
                "email": cached.email,
                "token": cached.access_token,
                "refresh_token": cached.refresh_token
            }
        
        # ดึง token ใหม่จาก harvester
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    f"{self.harvester_url}/api/get_token",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success") and data.get("token"):
                        token_data = TokenData(
                            account_id=data.get("account_id", "unknown"),
                            email=data.get("email", "unknown"),
                            access_token=data.get("token"),
                            refresh_token=data.get("refresh_token"),
                            expires_at=data.get("expires_at")
                        )
                        
                        # Cache token
                        self._cache_token(token_data)
                        self._last_token_id = token_data.account_id
                        self._stats.successful_requests += 1
                        
                        logger.info(f"✅ Got token from {token_data.email}")
                        
                        return {
                            "account_id": token_data.account_id,
                            "email": token_data.email,
                            "token": token_data.access_token,
                            "refresh_token": token_data.refresh_token
                        }
                    else:
                        logger.warning(f"⚠️ No token available: {data.get('message')}")
                        
                elif response.status_code == 503:
                    logger.warning("⚠️ Token Harvester: All tokens exhausted")
                    
                else:
                    logger.error(f"❌ Token Harvester error: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                logger.error(f"❌ Cannot connect to Token Harvester at {self.harvester_url}")
                
            except Exception as e:
                logger.error(f"❌ Error getting token: {e}")
            
            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(1)
        
        self._stats.failed_requests += 1
        return None
    
    def report_exhausted_token(self, account_id: str) -> bool:
        """
        รายงานว่า token quota หมด
        
        Args:
            account_id: ID ของ account ที่ quota หมด
            
        Returns:
            True if reported successfully
        """
        try:
            response = requests.post(
                f"{self.harvester_url}/api/mark_exhausted",
                json={"account_id": account_id},
                timeout=10
            )
            
            if response.status_code == 200:
                self._stats.tokens_exhausted += 1
                
                # Remove from cache
                with self._cache_lock:
                    if account_id in self._cache:
                        del self._cache[account_id]
                
                logger.info(f"✅ Reported exhausted token: {account_id}")
                return True
            else:
                logger.error(f"❌ Failed to report exhausted token: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error reporting exhausted token: {e}")
            return False
    
    def refresh_token(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        ขอ refresh token
        
        Args:
            account_id: ID ของ account ที่ต้องการ refresh
            
        Returns:
            New token data or None
        """
        try:
            response = requests.post(
                f"{self.harvester_url}/api/refresh_token",
                json={"account_id": account_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    self._stats.tokens_refreshed += 1
                    
                    # Update cache
                    token_data = TokenData(
                        account_id=account_id,
                        email=data.get("email", "unknown"),
                        access_token=data.get("token"),
                        refresh_token=data.get("refresh_token"),
                        expires_at=data.get("expires_at")
                    )
                    self._cache_token(token_data)
                    
                    logger.info(f"✅ Refreshed token: {account_id}")
                    
                    return {
                        "account_id": token_data.account_id,
                        "email": token_data.email,
                        "token": token_data.access_token
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error refreshing token: {e}")
            return None
    
    def get_pool_status(self) -> Dict[str, Any]:
        """ดึงสถานะของ Token Pool"""
        try:
            response = requests.get(
                f"{self.harvester_url}/api/status",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """ดึงสถิติการใช้งาน"""
        return {
            "total_requests": self._stats.total_requests,
            "successful_requests": self._stats.successful_requests,
            "failed_requests": self._stats.failed_requests,
            "success_rate": f"{(self._stats.successful_requests / max(1, self._stats.total_requests)) * 100:.2f}%",
            "tokens_exhausted": self._stats.tokens_exhausted,
            "tokens_refreshed": self._stats.tokens_refreshed,
            "last_request": self._stats.last_request.isoformat() if self._stats.last_request else None,
            "cached_tokens": len(self._cache),
            "harvester_url": self.harvester_url
        }
    
    def _cache_token(self, token: TokenData) -> None:
        """Cache token"""
        with self._cache_lock:
            self._cache[token.account_id] = token
    
    def _get_cached_token(self) -> Optional[TokenData]:
        """ดึง cached token ที่ยังใช้ได้"""
        with self._cache_lock:
            # ลองใช้ token ล่าสุดก่อน
            if self._last_token_id and self._last_token_id in self._cache:
                token = self._cache[self._last_token_id]
                if not token.is_expired:
                    return token
            
            # หา token อื่นที่ยังใช้ได้
            for token in self._cache.values():
                if not token.is_expired:
                    return token
            
            return None
    
    def health_check(self) -> bool:
        """ตรวจสอบว่า Token Harvester พร้อมใช้งาน"""
        try:
            response = requests.get(
                f"{self.harvester_url}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


# ==================== Singleton Instance ====================

_integration_instance: Optional[TokenIntegration] = None


def get_token_integration(harvester_url: Optional[str] = None) -> TokenIntegration:
    """ดึง Singleton instance ของ TokenIntegration"""
    global _integration_instance
    
    if _integration_instance is None:
        url = harvester_url or os.environ.get("TOKEN_HARVESTER_URL", "http://localhost:8888")
        _integration_instance = TokenIntegration(harvester_url=url)
    
    return _integration_instance


# ==================== Mock Token Harvester for Testing ====================

class MockTokenHarvester:
    """Mock Token Harvester สำหรับทดสอบ"""
    
    def __init__(self):
        self.tokens = {
            "acc001": {
                "email": "test1@gmail.com",
                "access_token": "mock_token_001",
                "refresh_token": "mock_refresh_001",
                "quota_exhausted": False
            },
            "acc002": {
                "email": "test2@gmail.com",
                "access_token": "mock_token_002",
                "refresh_token": "mock_refresh_002",
                "quota_exhausted": False
            },
            "acc003": {
                "email": "test3@gmail.com",
                "access_token": "mock_token_003",
                "refresh_token": "mock_refresh_003",
                "quota_exhausted": False
            }
        }
        self.current_index = 0
    
    def get_token(self) -> Optional[Dict[str, Any]]:
        """ดึง token ถัดไป"""
        available = [
            (k, v) for k, v in self.tokens.items()
            if not v.get("quota_exhausted")
        ]
        
        if not available:
            # Reset all
            for token in self.tokens.values():
                token["quota_exhausted"] = False
            available = list(self.tokens.items())
        
        self.current_index = self.current_index % len(available)
        account_id, token_data = available[self.current_index]
        self.current_index += 1
        
        return {
            "success": True,
            "account_id": account_id,
            "email": token_data["email"],
            "token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "expires_at": time.time() + 3600
        }
    
    def mark_exhausted(self, account_id: str) -> bool:
        """ทำเครื่องหมาย quota หมด"""
        if account_id in self.tokens:
            self.tokens[account_id]["quota_exhausted"] = True
            return True
        return False


# ==================== Test ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing Token Integration")
    print("=" * 60)
    
    # ใช้ Mock Harvester
    mock_harvester = MockTokenHarvester()
    
    # สร้าง integration (จะไม่สามารถเชื่อมต่อได้จริง)
    integration = TokenIntegration(harvester_url="http://localhost:8888")
    
    # Test get_stats
    print("\n📊 Test 1: Get stats")
    stats = integration.get_stats()
    print(f"Stats: {stats}")
    
    # Test health_check (จะ fail เพราะไม่มี server จริง)
    print("\n📤 Test 2: Health check")
    is_healthy = integration.health_check()
    print(f"Healthy: {is_healthy}")
    
    # Test with mock data
    print("\n📤 Test 3: Mock token rotation")
    for i in range(5):
        token = mock_harvester.get_token()
        print(f"  Token {i+1}: {token['email']} - {token['account_id']}")
    
    # Test exhaustion
    print("\n📤 Test 4: Mark token exhausted")
    mock_harvester.mark_exhausted("acc001")
    for i in range(3):
        token = mock_harvester.get_token()
        print(f"  Token {i+1}: {token['email']} (acc001 should be skipped)")
    
    print("\n✅ Token Integration test completed!")
