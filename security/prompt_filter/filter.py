#!/usr/bin/env python3
"""
Prompt Filter
Based on: /source-files/dlnk_core/dlnk_prompt_filter.py
กรอง Prompt เพื่อป้องกัน dLNk, dLNk AI, และ Jetski
"""

import logging
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass

from .patterns import BLOCKED_PATTERNS, BLOCKED_KEYWORDS, SEVERITY_LEVELS
from .analyzer import PromptAnalyzer, AnalysisResult
from .logger import FilterLogger

logger = logging.getLogger('PromptFilter')


@dataclass
class FilterResult:
    """ผลลัพธ์การกรอง"""
    allowed: bool
    severity: int
    matched_pattern: Optional[str] = None
    reason: Optional[str] = None
    response: Optional[str] = None
    analysis: Optional[AnalysisResult] = None


class PromptFilter:
    """
    Filter prompts to protect dLNk, dLNk AI, and Jetski
    
    Usage:
        filter = PromptFilter()
        result = filter.filter("some prompt", user_id="user123")
        if not result.allowed:
            return result.response
    """
    
    # Default blocked response
    BLOCKED_RESPONSE = """⚠️ **คำถามนี้ถูกบล็อก**

คำถามของคุณเกี่ยวข้องกับการโจมตีระบบ dLNk ซึ่งไม่ได้รับอนุญาต

**สิ่งที่คุณสามารถถามได้:**
- คำถามเกี่ยวกับการเขียนโค้ด
- คำถามเกี่ยวกับ hacking/security (เป้าหมายอื่น)
- คำถามทั่วไปทุกประเภท

**สิ่งที่ไม่อนุญาต:**
- โจมตี dLNk, dLNk AI, หรือ Jetski
- ขโมย API Keys/Tokens ของระบบ
- Bypass License System

หากคุณคิดว่านี่เป็นข้อผิดพลาด กรุณาติดต่อ Admin"""
    
    def __init__(
        self,
        alert_manager=None,
        log_dir: str = None,
        blocked_response: str = None
    ):
        self.alert_manager = alert_manager
        self.analyzer = PromptAnalyzer()
        self.filter_logger = FilterLogger(log_dir=log_dir)
        self.blocked_response = blocked_response or self.BLOCKED_RESPONSE
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "passed_requests": 0,
            "suspicious_requests": 0,
            "critical_alerts": 0,
        }
    
    def filter(
        self,
        prompt: str,
        user_id: str = None,
        ip_address: str = None,
        session_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> FilterResult:
        """
        Filter a prompt
        
        Args:
            prompt: The prompt to filter
            user_id: Optional user identifier
            ip_address: Optional IP address
            session_id: Optional session ID
            metadata: Optional additional metadata
        
        Returns:
            FilterResult with status
        """
        self.stats["total_requests"] += 1
        user_id = user_id or "anonymous"
        
        # Analyze prompt
        analysis = self.analyzer.analyze(prompt)
        
        if analysis.is_threat:
            # Blocked
            self.stats["blocked_requests"] += 1
            
            # Get primary pattern/keyword
            matched = (
                analysis.matched_patterns[0] if analysis.matched_patterns
                else analysis.matched_keywords[0] if analysis.matched_keywords
                else "Unknown pattern"
            )
            
            result = FilterResult(
                allowed=False,
                severity=analysis.threat_level,
                matched_pattern=matched,
                reason=analysis.details,
                response=self.blocked_response,
                analysis=analysis
            )
            
            # Log and alert
            self._handle_blocked(prompt, result, user_id, ip_address, session_id, metadata)
            
            return result
        
        # Passed
        self.stats["passed_requests"] += 1
        
        if analysis.suspicious_keywords:
            self.stats["suspicious_requests"] += 1
        
        # Log passed prompts with suspicious keywords
        self.filter_logger.log_passed(
            prompt=prompt,
            user_id=user_id,
            suspicious_keywords=analysis.suspicious_keywords,
            ip_address=ip_address,
            session_id=session_id,
            metadata=metadata
        )
        
        return FilterResult(
            allowed=True,
            severity=0,
            analysis=analysis
        )
    
    def _handle_blocked(
        self,
        prompt: str,
        result: FilterResult,
        user_id: str,
        ip_address: str = None,
        session_id: str = None,
        metadata: Dict[str, Any] = None
    ):
        """Handle blocked prompt"""
        
        # Log the blocked prompt
        self.filter_logger.log_blocked(
            prompt=prompt,
            pattern=result.matched_pattern,
            severity=result.severity,
            user_id=user_id,
            ip_address=ip_address,
            session_id=session_id,
            metadata=metadata
        )
        
        # Alert if high severity
        if result.severity >= SEVERITY_LEVELS['high'] and self.alert_manager:
            self.alert_manager.send_alert(
                title="🚨 Security Alert",
                message=(
                    f"Blocked prompt detected!\n"
                    f"Severity: {result.severity}\n"
                    f"Pattern: {result.matched_pattern}\n"
                    f"User: {user_id}\n"
                    f"IP: {ip_address or 'Unknown'}"
                ),
                severity=result.severity
            )
        
        # Track critical alerts
        if result.severity >= SEVERITY_LEVELS['critical']:
            self.stats["critical_alerts"] += 1
            logger.critical(f"Critical threat detected from user {user_id}")
    
    def quick_filter(self, prompt: str) -> bool:
        """
        Quick filter check
        
        Returns:
            True if prompt is allowed
        """
        return not self.analyzer.quick_check(prompt)
    
    def add_pattern(self, pattern: str):
        """Add a new blocked pattern"""
        BLOCKED_PATTERNS.append(pattern)
        # Reinitialize analyzer
        self.analyzer = PromptAnalyzer()
        logger.info(f"Added new blocked pattern: {pattern}")
    
    def add_keyword(self, keyword: str):
        """Add a new blocked keyword"""
        BLOCKED_KEYWORDS.append(keyword.lower())
        logger.info(f"Added new blocked keyword: {keyword}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get filter statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics"""
        for key in self.stats:
            self.stats[key] = 0


class PromptFilterMiddleware:
    """Middleware สำหรับใช้กับ AI Bridge"""
    
    def __init__(self, alert_manager=None):
        self.filter = PromptFilter(alert_manager=alert_manager)
    
    async def process(
        self,
        message: str,
        user_id: str = "anonymous",
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Process message before sending to AI
        
        Returns:
            Tuple[bool, str]: (allowed, blocked_response if blocked)
        """
        result = self.filter.filter(message, user_id=user_id, **kwargs)
        
        if not result.allowed:
            return False, result.response
        
        return True, ""
    
    def get_stats(self) -> Dict[str, int]:
        """Get middleware statistics"""
        return self.filter.get_stats()


# ===== INTEGRATION FUNCTIONS =====

def integrate_with_ai_bridge(ai_bridge_instance, alert_manager=None):
    """
    รวมเข้ากับ AI Bridge
    
    Usage:
        from security.prompt_filter import integrate_with_ai_bridge
        integrate_with_ai_bridge(bridge)
    """
    middleware = PromptFilterMiddleware(alert_manager=alert_manager)
    
    # Store original process_message
    original_process = ai_bridge_instance.process_message
    
    async def filtered_process(message: str, user_id: str = "anonymous", **kwargs):
        # Filter first
        passed, blocked_response = await middleware.process(message, user_id)
        
        if not passed:
            return {
                "role": "assistant",
                "content": blocked_response,
                "filtered": True
            }
        
        # Pass to original
        return await original_process(message, user_id=user_id, **kwargs)
    
    ai_bridge_instance.process_message = filtered_process
    logger.info("Prompt filter integrated with AI Bridge")
    
    return middleware


def create_filter(alert_manager=None, log_dir: str = None) -> PromptFilter:
    """
    สร้าง PromptFilter instance
    
    Usage:
        from security.prompt_filter import create_filter
        filter = create_filter()
        result = filter.filter("prompt text")
    """
    return PromptFilter(alert_manager=alert_manager, log_dir=log_dir)
