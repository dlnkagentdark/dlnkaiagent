#!/usr/bin/env python3
"""
dLNk AI Bridge - Auto-Failover System
======================================
ระบบ Failover อัตโนมัติสำหรับ AI Providers

Features:
- ตรวจจับ Provider ล้มเหลว (timeout, error codes)
- สลับไปยัง Provider ถัดไปอัตโนมัติ
- บันทึก Provider health status
- Retry logic พร้อม exponential backoff

Author: dLNk IDE Project (AI-01 The Architect)
Date: December 25, 2025
"""

import time
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """สถานะของ AI Provider"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """ข้อมูลสุขภาพของ Provider"""
    name: str
    status: ProviderStatus = ProviderStatus.UNKNOWN
    last_check: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    average_latency_ms: float = 0.0
    error_message: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """คำนวณอัตราความสำเร็จ"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


@dataclass
class FailoverConfig:
    """การตั้งค่า Failover"""
    max_retries: int = 3
    initial_timeout: float = 30.0
    max_timeout: float = 120.0
    backoff_multiplier: float = 2.0
    failure_threshold: int = 3  # จำนวน failures ก่อนถือว่า unhealthy
    recovery_threshold: int = 2  # จำนวน successes ก่อนถือว่า recovered
    health_check_interval: int = 60  # วินาที
    cooldown_period: int = 300  # วินาทีก่อน retry provider ที่ล้มเหลว


class AutoFailover:
    """
    ระบบ Auto-Failover สำหรับ AI Providers
    
    ใช้งาน:
    ```python
    failover = AutoFailover()
    failover.register_provider("jetski", jetski_client, priority=1)
    failover.register_provider("groq", groq_client, priority=2)
    failover.register_provider("ollama", ollama_client, priority=3)
    
    result = failover.execute(prompt="Hello", model="default")
    ```
    """
    
    def __init__(self, config: Optional[FailoverConfig] = None):
        self.config = config or FailoverConfig()
        self.providers: Dict[str, Dict[str, Any]] = {}
        self.provider_health: Dict[str, ProviderHealth] = {}
        self.provider_order: List[str] = []
        self._lock = threading.Lock()
        self._current_provider: Optional[str] = None
        
    def register_provider(
        self,
        name: str,
        client: Any,
        priority: int = 100,
        health_check_fn: Optional[Callable] = None
    ) -> None:
        """
        ลงทะเบียน AI Provider
        
        Args:
            name: ชื่อ provider (e.g., "jetski", "groq", "ollama")
            client: Client object สำหรับเรียก API
            priority: ลำดับความสำคัญ (1 = สูงสุด)
            health_check_fn: Function สำหรับตรวจสอบสุขภาพ
        """
        with self._lock:
            self.providers[name] = {
                "client": client,
                "priority": priority,
                "health_check_fn": health_check_fn,
                "enabled": True
            }
            self.provider_health[name] = ProviderHealth(name=name)
            
            # เรียงลำดับตาม priority
            self.provider_order = sorted(
                self.providers.keys(),
                key=lambda x: self.providers[x]["priority"]
            )
            
            logger.info(f"✅ Registered provider: {name} (priority: {priority})")
    
    def unregister_provider(self, name: str) -> bool:
        """ยกเลิกการลงทะเบียน Provider"""
        with self._lock:
            if name in self.providers:
                del self.providers[name]
                del self.provider_health[name]
                self.provider_order = [p for p in self.provider_order if p != name]
                logger.info(f"❌ Unregistered provider: {name}")
                return True
            return False
    
    def enable_provider(self, name: str) -> bool:
        """เปิดใช้งาน Provider"""
        with self._lock:
            if name in self.providers:
                self.providers[name]["enabled"] = True
                logger.info(f"✅ Enabled provider: {name}")
                return True
            return False
    
    def disable_provider(self, name: str) -> bool:
        """ปิดใช้งาน Provider"""
        with self._lock:
            if name in self.providers:
                self.providers[name]["enabled"] = False
                logger.info(f"⏸️ Disabled provider: {name}")
                return True
            return False
    
    def get_available_providers(self) -> List[str]:
        """ดึงรายการ Provider ที่พร้อมใช้งาน"""
        available = []
        now = datetime.now()
        
        for name in self.provider_order:
            provider = self.providers.get(name)
            health = self.provider_health.get(name)
            
            if not provider or not provider["enabled"]:
                continue
            
            # ตรวจสอบ cooldown period
            if health.status == ProviderStatus.UNHEALTHY:
                if health.last_failure:
                    cooldown_end = health.last_failure + timedelta(seconds=self.config.cooldown_period)
                    if now < cooldown_end:
                        continue
            
            available.append(name)
        
        return available
    
    def _select_provider(self) -> Optional[str]:
        """เลือก Provider ที่ดีที่สุด"""
        available = self.get_available_providers()
        
        if not available:
            logger.error("❌ No available providers!")
            return None
        
        # เลือก provider แรกที่ healthy
        for name in available:
            health = self.provider_health.get(name)
            if health and health.status in [ProviderStatus.HEALTHY, ProviderStatus.UNKNOWN]:
                return name
        
        # ถ้าไม่มี healthy ให้เลือก degraded
        for name in available:
            health = self.provider_health.get(name)
            if health and health.status == ProviderStatus.DEGRADED:
                return name
        
        # ถ้าไม่มีเลย ให้เลือกตัวแรก
        return available[0] if available else None
    
    def _record_success(self, name: str, latency_ms: float) -> None:
        """บันทึกความสำเร็จ"""
        with self._lock:
            health = self.provider_health.get(name)
            if health:
                health.last_success = datetime.now()
                health.last_check = datetime.now()
                health.consecutive_failures = 0
                health.total_requests += 1
                health.successful_requests += 1
                
                # อัพเดท average latency
                if health.average_latency_ms == 0:
                    health.average_latency_ms = latency_ms
                else:
                    health.average_latency_ms = (health.average_latency_ms + latency_ms) / 2
                
                # อัพเดทสถานะ
                if health.status != ProviderStatus.HEALTHY:
                    if health.successful_requests >= self.config.recovery_threshold:
                        health.status = ProviderStatus.HEALTHY
                        logger.info(f"✅ Provider {name} recovered to HEALTHY")
                
                health.error_message = None
    
    def _record_failure(self, name: str, error: str) -> None:
        """บันทึกความล้มเหลว"""
        with self._lock:
            health = self.provider_health.get(name)
            if health:
                health.last_failure = datetime.now()
                health.last_check = datetime.now()
                health.consecutive_failures += 1
                health.total_requests += 1
                health.error_message = error
                
                # อัพเดทสถานะ
                if health.consecutive_failures >= self.config.failure_threshold:
                    health.status = ProviderStatus.UNHEALTHY
                    logger.warning(f"⚠️ Provider {name} marked as UNHEALTHY")
                elif health.consecutive_failures >= 1:
                    health.status = ProviderStatus.DEGRADED
                    logger.warning(f"⚠️ Provider {name} marked as DEGRADED")
    
    def execute(
        self,
        request_fn: Callable[[Any, Dict[str, Any]], Any],
        request_params: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        ดำเนินการ request พร้อม auto-failover
        
        Args:
            request_fn: Function สำหรับเรียก API (รับ client และ params)
            request_params: Parameters สำหรับ request
            **kwargs: Additional arguments
            
        Returns:
            Dict containing response or error
        """
        attempted_providers = []
        last_error = None
        
        for attempt in range(self.config.max_retries):
            provider_name = self._select_provider()
            
            if not provider_name:
                return {
                    "success": False,
                    "error": "No available providers",
                    "attempted_providers": attempted_providers
                }
            
            if provider_name in attempted_providers:
                # ถ้าลองครบทุก provider แล้ว ให้หยุด
                available = self.get_available_providers()
                remaining = [p for p in available if p not in attempted_providers]
                if not remaining:
                    break
                provider_name = remaining[0]
            
            attempted_providers.append(provider_name)
            provider = self.providers.get(provider_name)
            
            if not provider:
                continue
            
            client = provider["client"]
            
            # คำนวณ timeout พร้อม exponential backoff
            timeout = min(
                self.config.initial_timeout * (self.config.backoff_multiplier ** attempt),
                self.config.max_timeout
            )
            
            logger.info(f"🔄 Attempting request with provider: {provider_name} (attempt {attempt + 1})")
            
            start_time = time.time()
            
            try:
                # เรียก request function
                result = request_fn(client, request_params)
                
                latency_ms = (time.time() - start_time) * 1000
                self._record_success(provider_name, latency_ms)
                
                logger.info(f"✅ Request successful with {provider_name} ({latency_ms:.2f}ms)")
                
                return {
                    "success": True,
                    "provider": provider_name,
                    "result": result,
                    "latency_ms": latency_ms,
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                last_error = str(e)
                self._record_failure(provider_name, last_error)
                logger.error(f"❌ Request failed with {provider_name}: {last_error}")
                
                # รอก่อน retry
                if attempt < self.config.max_retries - 1:
                    wait_time = min(2 ** attempt, 10)
                    logger.info(f"⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        return {
            "success": False,
            "error": last_error or "All providers failed",
            "attempted_providers": attempted_providers,
            "attempts": len(attempted_providers)
        }
    
    def check_health(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        ตรวจสอบสุขภาพของ Provider
        
        Args:
            name: ชื่อ provider (ถ้าไม่ระบุจะตรวจทั้งหมด)
            
        Returns:
            Dict containing health status
        """
        if name:
            providers_to_check = [name] if name in self.providers else []
        else:
            providers_to_check = list(self.providers.keys())
        
        results = {}
        
        for provider_name in providers_to_check:
            provider = self.providers.get(provider_name)
            health = self.provider_health.get(provider_name)
            
            if not provider or not health:
                continue
            
            health_check_fn = provider.get("health_check_fn")
            
            if health_check_fn:
                try:
                    start_time = time.time()
                    is_healthy = health_check_fn(provider["client"])
                    latency_ms = (time.time() - start_time) * 1000
                    
                    if is_healthy:
                        self._record_success(provider_name, latency_ms)
                    else:
                        self._record_failure(provider_name, "Health check returned False")
                        
                except Exception as e:
                    self._record_failure(provider_name, str(e))
            
            results[provider_name] = {
                "status": health.status.value,
                "last_check": health.last_check.isoformat() if health.last_check else None,
                "last_success": health.last_success.isoformat() if health.last_success else None,
                "last_failure": health.last_failure.isoformat() if health.last_failure else None,
                "consecutive_failures": health.consecutive_failures,
                "success_rate": f"{health.success_rate:.2f}%",
                "average_latency_ms": f"{health.average_latency_ms:.2f}",
                "error_message": health.error_message,
                "enabled": provider["enabled"]
            }
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """ดึงสถิติรวมของระบบ Failover"""
        total_requests = 0
        total_successes = 0
        provider_stats = []
        
        for name, health in self.provider_health.items():
            total_requests += health.total_requests
            total_successes += health.successful_requests
            
            provider_stats.append({
                "name": name,
                "status": health.status.value,
                "requests": health.total_requests,
                "successes": health.successful_requests,
                "success_rate": f"{health.success_rate:.2f}%",
                "avg_latency": f"{health.average_latency_ms:.2f}ms"
            })
        
        overall_success_rate = (total_successes / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_providers": len(self.providers),
            "available_providers": len(self.get_available_providers()),
            "total_requests": total_requests,
            "total_successes": total_successes,
            "overall_success_rate": f"{overall_success_rate:.2f}%",
            "providers": provider_stats
        }


# ==================== Singleton Instance ====================

_failover_instance: Optional[AutoFailover] = None


def get_failover() -> AutoFailover:
    """ดึง Singleton instance ของ AutoFailover"""
    global _failover_instance
    if _failover_instance is None:
        _failover_instance = AutoFailover()
    return _failover_instance


# ==================== Test ====================

if __name__ == "__main__":
    # ทดสอบ AutoFailover
    print("=" * 60)
    print("🧪 Testing AutoFailover System")
    print("=" * 60)
    
    failover = AutoFailover()
    
    # Mock providers
    class MockProvider:
        def __init__(self, name: str, should_fail: bool = False):
            self.name = name
            self.should_fail = should_fail
            
        def complete(self, prompt: str) -> str:
            if self.should_fail:
                raise Exception(f"{self.name} failed!")
            return f"Response from {self.name}: {prompt}"
    
    # Register providers
    failover.register_provider("jetski", MockProvider("Jetski"), priority=1)
    failover.register_provider("groq", MockProvider("Groq"), priority=2)
    failover.register_provider("ollama", MockProvider("Ollama"), priority=3)
    
    # Test request function
    def make_request(client, params):
        return client.complete(params.get("prompt", ""))
    
    # Test successful request
    print("\n📤 Test 1: Normal request")
    result = failover.execute(make_request, {"prompt": "Hello World"})
    print(f"Result: {result}")
    
    # Test with failing primary
    print("\n📤 Test 2: Primary provider fails")
    failover.providers["jetski"]["client"] = MockProvider("Jetski", should_fail=True)
    result = failover.execute(make_request, {"prompt": "Test failover"})
    print(f"Result: {result}")
    
    # Check health
    print("\n📊 Health Status:")
    health = failover.check_health()
    for name, status in health.items():
        print(f"  {name}: {status['status']} (success rate: {status['success_rate']})")
    
    # Get stats
    print("\n📈 Overall Stats:")
    stats = failover.get_stats()
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Success rate: {stats['overall_success_rate']}")
    
    print("\n✅ AutoFailover test completed!")
