#!/usr/bin/env python3
"""
Prompt Analyzer
วิเคราะห์ Prompt เพื่อตรวจจับการโจมตี
"""

import re
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

from .patterns import (
    BLOCKED_PATTERNS,
    BLOCKED_KEYWORDS,
    SUSPICIOUS_KEYWORDS,
    SEVERITY_LEVELS,
    PATTERN_SEVERITY_KEYWORDS,
    LEETSPEAK_MAP,
    WHITELIST_PATTERNS
)

logger = logging.getLogger('PromptAnalyzer')


@dataclass
class AnalysisResult:
    """ผลการวิเคราะห์ Prompt"""
    is_threat: bool
    threat_level: int  # 0-4
    matched_patterns: List[str]
    matched_keywords: List[str]
    suspicious_keywords: List[str]
    confidence: float  # 0.0 - 1.0
    details: str


class PromptAnalyzer:
    """
    วิเคราะห์ Prompt เพื่อตรวจจับภัยคุกคาม
    """
    
    def __init__(self):
        # Compile patterns for efficiency
        self.blocked_patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL)
            for p in BLOCKED_PATTERNS
        ]
        self.whitelist_patterns = [
            re.compile(p, re.IGNORECASE | re.DOTALL)
            for p in WHITELIST_PATTERNS
        ]
    
    def normalize_text(self, text: str) -> str:
        """
        ทำให้ข้อความเป็นมาตรฐาน
        - ลบช่องว่างซ้ำ
        - แปลง leetspeak
        - ลบอักขระพิเศษ
        """
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', text)
        
        # Remove special characters used for evasion
        normalized = re.sub(r'[_\-\.\*\#\@\!\|]', '', normalized)
        
        # Convert leetspeak
        for leet, char in LEETSPEAK_MAP.items():
            normalized = normalized.replace(leet, char)
        
        return normalized.lower().strip()
    
    def check_whitelist(self, text: str) -> bool:
        """ตรวจสอบว่าอยู่ใน whitelist หรือไม่"""
        for pattern in self.whitelist_patterns:
            if pattern.search(text):
                return True
        return False
    
    def find_blocked_patterns(self, text: str) -> List[Tuple[str, str]]:
        """
        ค้นหา patterns ที่ถูกบล็อก
        Returns: List of (pattern, matched_text)
        """
        normalized = self.normalize_text(text)
        matches = []
        
        for i, pattern in enumerate(self.blocked_patterns):
            # Check both original and normalized
            match = pattern.search(text.lower())
            if not match:
                match = pattern.search(normalized)
            
            if match:
                matches.append((BLOCKED_PATTERNS[i], match.group()))
        
        return matches
    
    def find_blocked_keywords(self, text: str) -> List[str]:
        """ค้นหา keywords ที่ถูกบล็อก"""
        text_lower = text.lower()
        normalized = self.normalize_text(text)
        
        matches = []
        for keyword in BLOCKED_KEYWORDS:
            if keyword in text_lower or keyword in normalized:
                matches.append(keyword)
        
        return matches
    
    def find_suspicious_keywords(self, text: str) -> List[str]:
        """ค้นหา keywords ที่น่าสงสัย"""
        text_lower = text.lower()
        
        matches = []
        for keyword in SUSPICIOUS_KEYWORDS:
            if keyword in text_lower:
                matches.append(keyword)
        
        return matches
    
    def calculate_severity(
        self,
        patterns: List[Tuple[str, str]],
        keywords: List[str]
    ) -> int:
        """คำนวณระดับความรุนแรง"""
        max_severity = 0
        
        # Check patterns
        for pattern, _ in patterns:
            pattern_lower = pattern.lower()
            for keyword, severity in PATTERN_SEVERITY_KEYWORDS.items():
                if keyword in pattern_lower:
                    max_severity = max(max_severity, severity)
        
        # Check keywords
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for kw, severity in PATTERN_SEVERITY_KEYWORDS.items():
                if kw in keyword_lower:
                    max_severity = max(max_severity, severity)
        
        # Default to medium if patterns found but no specific severity
        if patterns and max_severity == 0:
            max_severity = SEVERITY_LEVELS['medium']
        
        return max_severity
    
    def calculate_confidence(
        self,
        patterns: List[Tuple[str, str]],
        keywords: List[str],
        suspicious: List[str]
    ) -> float:
        """คำนวณความมั่นใจในการตรวจจับ"""
        confidence = 0.0
        
        # Patterns have highest weight
        if patterns:
            confidence += min(len(patterns) * 0.3, 0.6)
        
        # Keywords add to confidence
        if keywords:
            confidence += min(len(keywords) * 0.2, 0.3)
        
        # Suspicious keywords add small amount
        if suspicious:
            confidence += min(len(suspicious) * 0.05, 0.1)
        
        return min(confidence, 1.0)
    
    def analyze(self, prompt: str) -> AnalysisResult:
        """
        วิเคราะห์ Prompt อย่างครบถ้วน
        
        Args:
            prompt: ข้อความที่ต้องการวิเคราะห์
        
        Returns:
            AnalysisResult พร้อมรายละเอียด
        """
        # Check whitelist first
        if self.check_whitelist(prompt):
            return AnalysisResult(
                is_threat=False,
                threat_level=0,
                matched_patterns=[],
                matched_keywords=[],
                suspicious_keywords=[],
                confidence=0.0,
                details="Whitelisted pattern detected"
            )
        
        # Find all matches
        patterns = self.find_blocked_patterns(prompt)
        keywords = self.find_blocked_keywords(prompt)
        suspicious = self.find_suspicious_keywords(prompt)
        
        # Determine if threat
        is_threat = bool(patterns or keywords)
        
        # Calculate severity and confidence
        severity = self.calculate_severity(patterns, keywords)
        confidence = self.calculate_confidence(patterns, keywords, suspicious)
        
        # Build details
        details_parts = []
        if patterns:
            details_parts.append(f"Matched {len(patterns)} blocked pattern(s)")
        if keywords:
            details_parts.append(f"Matched {len(keywords)} blocked keyword(s)")
        if suspicious:
            details_parts.append(f"Found {len(suspicious)} suspicious keyword(s)")
        
        details = "; ".join(details_parts) if details_parts else "No threats detected"
        
        return AnalysisResult(
            is_threat=is_threat,
            threat_level=severity,
            matched_patterns=[p[0] for p in patterns],
            matched_keywords=keywords,
            suspicious_keywords=suspicious,
            confidence=confidence,
            details=details
        )
    
    def quick_check(self, prompt: str) -> bool:
        """
        ตรวจสอบอย่างรวดเร็วว่าเป็นภัยคุกคามหรือไม่
        
        Returns:
            True if threat detected
        """
        # Check whitelist
        if self.check_whitelist(prompt):
            return False
        
        # Quick pattern check
        normalized = self.normalize_text(prompt)
        text_lower = prompt.lower()
        
        for pattern in self.blocked_patterns:
            if pattern.search(text_lower) or pattern.search(normalized):
                return True
        
        for keyword in BLOCKED_KEYWORDS:
            if keyword in text_lower or keyword in normalized:
                return True
        
        return False
