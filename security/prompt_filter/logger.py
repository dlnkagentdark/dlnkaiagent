#!/usr/bin/env python3
"""
Filter Logger
บันทึก Log ของ Prompt ที่ถูกบล็อก
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

logger = logging.getLogger('FilterLogger')


@dataclass
class FilterLogEntry:
    """โครงสร้างข้อมูล Log"""
    timestamp: str
    user_id: str
    prompt_hash: str
    prompt_preview: str
    result: str  # BLOCKED, PASSED, SUSPICIOUS
    severity: int
    matched_pattern: Optional[str] = None
    blocked_reason: Optional[str] = None
    suspicious_keywords: Optional[List[str]] = None
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FilterLogger:
    """
    บันทึก Log ของ Prompt Filter
    """
    
    def __init__(
        self,
        log_dir: str = None,
        log_file: str = "prompt_filter.log",
        json_file: str = "prompt_filter.json",
        max_preview_length: int = 200,
        encrypt: bool = False
    ):
        self.log_dir = Path(log_dir) if log_dir else Path.home() / ".dlnk-ide" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.log_dir / log_file
        self.json_file = self.log_dir / json_file
        self.max_preview_length = max_preview_length
        self.encrypt = encrypt
        
        # Statistics
        self.stats = {
            "total_logged": 0,
            "blocked_count": 0,
            "passed_count": 0,
            "suspicious_count": 0,
            "critical_count": 0,
        }
    
    def _hash_prompt(self, prompt: str) -> str:
        """สร้าง hash ของ prompt"""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def _truncate_preview(self, prompt: str) -> str:
        """ตัดข้อความ preview"""
        if len(prompt) > self.max_preview_length:
            return prompt[:self.max_preview_length] + "..."
        return prompt
    
    def log_blocked(
        self,
        prompt: str,
        pattern: str,
        severity: int,
        user_id: str = None,
        ip_address: str = None,
        session_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> FilterLogEntry:
        """บันทึก prompt ที่ถูกบล็อก"""
        
        entry = FilterLogEntry(
            timestamp=datetime.now().isoformat(),
            user_id=user_id or "anonymous",
            prompt_hash=self._hash_prompt(prompt),
            prompt_preview=self._truncate_preview(prompt),
            result="BLOCKED",
            severity=severity,
            matched_pattern=pattern,
            blocked_reason=f"Blocked by pattern: {pattern}",
            ip_address=ip_address,
            session_id=session_id,
            metadata=metadata
        )
        
        self._write_log(entry)
        self.stats["blocked_count"] += 1
        
        if severity >= 4:
            self.stats["critical_count"] += 1
        
        logger.warning(
            f"BLOCKED: user={user_id}, severity={severity}, "
            f"pattern={pattern[:50]}..."
        )
        
        return entry
    
    def log_passed(
        self,
        prompt: str,
        user_id: str = None,
        suspicious_keywords: List[str] = None,
        ip_address: str = None,
        session_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> FilterLogEntry:
        """บันทึก prompt ที่ผ่าน"""
        
        result = "SUSPICIOUS" if suspicious_keywords else "PASSED"
        
        entry = FilterLogEntry(
            timestamp=datetime.now().isoformat(),
            user_id=user_id or "anonymous",
            prompt_hash=self._hash_prompt(prompt),
            prompt_preview=self._truncate_preview(prompt),
            result=result,
            severity=0 if not suspicious_keywords else 1,
            suspicious_keywords=suspicious_keywords,
            ip_address=ip_address,
            session_id=session_id,
            metadata=metadata
        )
        
        self._write_log(entry)
        
        if suspicious_keywords:
            self.stats["suspicious_count"] += 1
            logger.info(f"SUSPICIOUS: user={user_id}, keywords={suspicious_keywords}")
        else:
            self.stats["passed_count"] += 1
        
        return entry
    
    def _write_log(self, entry: FilterLogEntry):
        """เขียน log ลงไฟล์"""
        self.stats["total_logged"] += 1
        
        # Write to JSON file
        try:
            entry_dict = asdict(entry)
            with open(self.json_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry_dict, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to write JSON log: {e}")
        
        # Write to text log file
        try:
            log_line = (
                f"[{entry.timestamp}] [{entry.result}] "
                f"user={entry.user_id} severity={entry.severity} "
                f"hash={entry.prompt_hash}"
            )
            if entry.matched_pattern:
                log_line += f" pattern={entry.matched_pattern[:50]}"
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line + "\n")
        except Exception as e:
            logger.error(f"Failed to write text log: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """ดึงสถิติ"""
        return self.stats.copy()
    
    def get_recent_logs(
        self,
        limit: int = 100,
        result_filter: str = None
    ) -> List[FilterLogEntry]:
        """ดึง log ล่าสุด"""
        logs = []
        
        try:
            if not self.json_file.exists():
                return logs
            
            with open(self.json_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if result_filter and data.get("result") != result_filter:
                            continue
                        logs.append(FilterLogEntry(**data))
                    except json.JSONDecodeError:
                        continue
            
            # Return most recent
            return logs[-limit:]
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")
            return []
    
    def get_blocked_by_user(self, user_id: str) -> List[FilterLogEntry]:
        """ดึง log ที่ถูกบล็อกของ user"""
        all_logs = self.get_recent_logs(limit=1000, result_filter="BLOCKED")
        return [log for log in all_logs if log.user_id == user_id]
    
    def clear_old_logs(self, days: int = 90):
        """ลบ log เก่า"""
        cutoff = datetime.now().isoformat()[:10]  # Simplified for now
        logger.info(f"Clearing logs older than {days} days")
        # Implementation would filter and rewrite files
