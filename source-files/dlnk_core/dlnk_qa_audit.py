#!/usr/bin/env python3
"""
dLNk QA/Audit System v1.0
ระบบทดสอบและตรวจสอบคุณภาพ
- Security Audit
- Performance Testing
- Reasoning Mode Testing
- Coding Mode Testing
- Comparison with Competitors
"""

import os
import sys
import json
import time
import hashlib
import asyncio
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-QA')


class QATestResult:
    """ผลการทดสอบ"""
    
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.passed = False
        self.score = 0.0
        self.max_score = 100.0
        self.details = ""
        self.recommendations = []
        self.execution_time_ms = 0


class DLNKQAAudit:
    """ระบบ QA/Audit สำหรับ dLNk"""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.results: List[QATestResult] = []
        self.overall_score = 0.0
        self.level = "Beginner"
    
    def run_all_tests(self) -> Dict:
        """รันการทดสอบทั้งหมด"""
        print("=" * 70)
        print("dLNk QA/Audit System v1.0")
        print("=" * 70)
        print()
        
        # Security Tests
        self._run_security_tests()
        
        # Code Quality Tests
        self._run_code_quality_tests()
        
        # Feature Completeness Tests
        self._run_feature_tests()
        
        # Reasoning Mode Tests
        self._run_reasoning_tests()
        
        # Coding Mode Tests
        self._run_coding_tests()
        
        # Calculate overall score
        self._calculate_overall_score()
        
        return self._generate_report()
    
    def _run_security_tests(self):
        """ทดสอบความปลอดภัย"""
        print("🔒 Running Security Tests...")
        print("-" * 50)
        
        tests = [
            ("Prompt Filter Protection", self._test_prompt_filter),
            ("Admin Authentication", self._test_admin_auth),
            ("License Encryption", self._test_license_encryption),
            ("Input Validation", self._test_input_validation),
            ("Rate Limiting", self._test_rate_limiting),
            ("Self-Attack Prevention", self._test_self_attack_prevention),
        ]
        
        for name, test_func in tests:
            result = QATestResult(name, "Security")
            start_time = time.time()
            
            try:
                score, details, recommendations = test_func()
                result.score = score
                result.passed = score >= 70
                result.details = details
                result.recommendations = recommendations
            except Exception as e:
                result.score = 0
                result.passed = False
                result.details = f"Test failed with error: {str(e)}"
                result.recommendations = ["Fix the error and re-run"]
            
            result.execution_time_ms = int((time.time() - start_time) * 1000)
            self.results.append(result)
            
            status = "✅" if result.passed else "❌"
            print(f"  {status} {name}: {result.score:.0f}/100")
        
        print()
    
    def _run_code_quality_tests(self):
        """ทดสอบคุณภาพโค้ด"""
        print("📝 Running Code Quality Tests...")
        print("-" * 50)
        
        tests = [
            ("Error Handling", self._test_error_handling),
            ("Code Documentation", self._test_documentation),
            ("Module Structure", self._test_module_structure),
            ("Dependency Management", self._test_dependencies),
        ]
        
        for name, test_func in tests:
            result = QATestResult(name, "Code Quality")
            start_time = time.time()
            
            try:
                score, details, recommendations = test_func()
                result.score = score
                result.passed = score >= 60
                result.details = details
                result.recommendations = recommendations
            except Exception as e:
                result.score = 0
                result.passed = False
                result.details = f"Test failed with error: {str(e)}"
            
            result.execution_time_ms = int((time.time() - start_time) * 1000)
            self.results.append(result)
            
            status = "✅" if result.passed else "❌"
            print(f"  {status} {name}: {result.score:.0f}/100")
        
        print()
    
    def _run_feature_tests(self):
        """ทดสอบความครบถ้วนของ Features"""
        print("🎯 Running Feature Completeness Tests...")
        print("-" * 50)
        
        tests = [
            ("AI Bridge Integration", self._test_ai_bridge),
            ("License System", self._test_license_system),
            ("Telegram Bot", self._test_telegram_bot),
            ("Admin Console", self._test_admin_console),
            ("C2 Logging", self._test_c2_logging),
        ]
        
        for name, test_func in tests:
            result = QATestResult(name, "Features")
            start_time = time.time()
            
            try:
                score, details, recommendations = test_func()
                result.score = score
                result.passed = score >= 50
                result.details = details
                result.recommendations = recommendations
            except Exception as e:
                result.score = 0
                result.passed = False
                result.details = f"Test failed with error: {str(e)}"
            
            result.execution_time_ms = int((time.time() - start_time) * 1000)
            self.results.append(result)
            
            status = "✅" if result.passed else "❌"
            print(f"  {status} {name}: {result.score:.0f}/100")
        
        print()
    
    def _run_reasoning_tests(self):
        """ทดสอบ Reasoning Mode"""
        print("🧠 Running Reasoning Mode Tests...")
        print("-" * 50)
        
        result = QATestResult("Reasoning Mode Dark", "AI Capability")
        
        # Test criteria for Reasoning Mode
        criteria = {
            "prompt_understanding": 0,
            "context_retention": 0,
            "logical_deduction": 0,
            "multi_step_planning": 0,
            "error_recovery": 0,
        }
        
        # Check if AI Bridge exists and has reasoning capabilities
        ai_bridge_path = self.project_path / "dlnk_ai_bridge_v2.py"
        if ai_bridge_path.exists():
            content = ai_bridge_path.read_text()
            
            # Check for reasoning-related features
            if "system_prompt" in content or "SYSTEM_PROMPT" in content:
                criteria["prompt_understanding"] = 20
            
            if "conversation" in content or "history" in content:
                criteria["context_retention"] = 20
            
            if "chain" in content or "step" in content:
                criteria["multi_step_planning"] = 15
            
            if "error" in content.lower() and "handle" in content.lower():
                criteria["error_recovery"] = 15
            
            if "analyze" in content.lower() or "reason" in content.lower():
                criteria["logical_deduction"] = 15
        
        total_score = sum(criteria.values())
        result.score = total_score
        result.passed = total_score >= 50
        result.details = f"Reasoning capabilities: {json.dumps(criteria, indent=2)}"
        result.recommendations = []
        
        if criteria["prompt_understanding"] < 20:
            result.recommendations.append("Add better system prompt handling")
        if criteria["context_retention"] < 20:
            result.recommendations.append("Implement conversation history")
        if criteria["multi_step_planning"] < 15:
            result.recommendations.append("Add multi-step task planning")
        
        self.results.append(result)
        
        status = "✅" if result.passed else "❌"
        print(f"  {status} Reasoning Mode: {result.score:.0f}/100")
        print()
    
    def _run_coding_tests(self):
        """ทดสอบ Coding Mode"""
        print("💻 Running Coding Mode Tests...")
        print("-" * 50)
        
        result = QATestResult("Coding Mode Dark", "AI Capability")
        
        criteria = {
            "code_generation": 0,
            "file_operations": 0,
            "syntax_awareness": 0,
            "multi_language": 0,
            "code_execution": 0,
        }
        
        # Check for coding capabilities
        ai_bridge_path = self.project_path / "dlnk_ai_bridge_v2.py"
        if ai_bridge_path.exists():
            content = ai_bridge_path.read_text()
            
            if "code" in content.lower() or "generate" in content.lower():
                criteria["code_generation"] = 20
            
            if "file" in content.lower() and ("write" in content.lower() or "save" in content.lower()):
                criteria["file_operations"] = 20
            
            if "python" in content.lower() or "javascript" in content.lower():
                criteria["multi_language"] = 15
            
            if "exec" in content.lower() or "run" in content.lower():
                criteria["code_execution"] = 15
            
            if "syntax" in content.lower() or "parse" in content.lower():
                criteria["syntax_awareness"] = 15
        
        total_score = sum(criteria.values())
        result.score = total_score
        result.passed = total_score >= 50
        result.details = f"Coding capabilities: {json.dumps(criteria, indent=2)}"
        result.recommendations = []
        
        if criteria["code_generation"] < 20:
            result.recommendations.append("Enhance code generation prompts")
        if criteria["file_operations"] < 20:
            result.recommendations.append("Add file write/save capabilities")
        if criteria["code_execution"] < 15:
            result.recommendations.append("Implement safe code execution sandbox")
        
        self.results.append(result)
        
        status = "✅" if result.passed else "❌"
        print(f"  {status} Coding Mode: {result.score:.0f}/100")
        print()
    
    # ===== Individual Test Functions =====
    
    def _test_prompt_filter(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Prompt Filter"""
        score = 0
        details = []
        recommendations = []
        
        filter_path = self.project_path / "dlnk_prompt_filter.py"
        if filter_path.exists():
            content = filter_path.read_text()
            
            # Check for blocked patterns
            if "BLOCKED_PATTERNS" in content:
                score += 30
                details.append("✓ Has blocked patterns")
            else:
                recommendations.append("Add blocked patterns for self-attack prevention")
            
            # Check for normalization
            if "normalize" in content.lower():
                score += 20
                details.append("✓ Has text normalization")
            else:
                recommendations.append("Add text normalization to prevent bypass")
            
            # Check for logging
            if "log" in content.lower():
                score += 20
                details.append("✓ Has logging")
            
            # Check for leetspeak handling
            if "leetspeak" in content.lower() or "l33t" in content.lower():
                score += 15
                details.append("✓ Handles leetspeak bypass")
            else:
                recommendations.append("Add leetspeak detection")
            
            # Check for middleware integration
            if "middleware" in content.lower():
                score += 15
                details.append("✓ Has middleware integration")
        else:
            recommendations.append("Create dlnk_prompt_filter.py")
        
        return score, "\n".join(details), recommendations
    
    def _test_admin_auth(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Admin Authentication"""
        score = 0
        details = []
        recommendations = []
        
        auth_path = self.project_path / "dlnk_admin_auth.py"
        if auth_path.exists():
            content = auth_path.read_text()
            
            if "password_hash" in content.lower() or "pbkdf2" in content.lower():
                score += 25
                details.append("✓ Password hashing")
            else:
                recommendations.append("Use secure password hashing (PBKDF2/bcrypt)")
            
            if "session" in content.lower():
                score += 20
                details.append("✓ Session management")
            
            if "rate" in content.lower() and "limit" in content.lower():
                score += 20
                details.append("✓ Rate limiting")
            else:
                recommendations.append("Add login rate limiting")
            
            if "2fa" in content.lower() or "totp" in content.lower():
                score += 20
                details.append("✓ 2FA support")
            else:
                recommendations.append("Add 2FA support")
            
            if "audit" in content.lower() or "log" in content.lower():
                score += 15
                details.append("✓ Audit logging")
        else:
            recommendations.append("Create dlnk_admin_auth.py")
        
        return score, "\n".join(details), recommendations
    
    def _test_license_encryption(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ License Encryption"""
        score = 0
        details = []
        recommendations = []
        
        license_path = self.project_path / "dlnk_license_system.py"
        if license_path.exists():
            content = license_path.read_text()
            
            if "fernet" in content.lower() or "aes" in content.lower():
                score += 30
                details.append("✓ Strong encryption (Fernet/AES)")
            elif "xor" in content.lower():
                score += 10
                details.append("⚠ Weak encryption (XOR)")
                recommendations.append("Upgrade to Fernet or AES encryption")
            
            if "hwid" in content.lower():
                score += 25
                details.append("✓ HWID binding")
            else:
                recommendations.append("Add HWID binding for license")
            
            if "expire" in content.lower():
                score += 20
                details.append("✓ Expiration handling")
            
            if "verify" in content.lower():
                score += 15
                details.append("✓ Verification function")
            
            if "tamper" in content.lower() or "integrity" in content.lower():
                score += 10
                details.append("✓ Tamper detection")
            else:
                recommendations.append("Add license integrity check")
        else:
            recommendations.append("Create dlnk_license_system.py")
        
        return score, "\n".join(details), recommendations
    
    def _test_input_validation(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Input Validation"""
        score = 0
        details = []
        recommendations = []
        
        # Check multiple files for input validation
        files_to_check = [
            "dlnk_ai_bridge_v2.py",
            "dlnk_admin_web.py",
            "dlnk_telegram_bot.py"
        ]
        
        validation_found = 0
        for filename in files_to_check:
            filepath = self.project_path / filename
            if filepath.exists():
                content = filepath.read_text()
                if "validate" in content.lower() or "sanitize" in content.lower():
                    validation_found += 1
                    details.append(f"✓ {filename} has validation")
        
        score = (validation_found / len(files_to_check)) * 100
        
        if validation_found < len(files_to_check):
            recommendations.append("Add input validation to all user-facing modules")
        
        return score, "\n".join(details), recommendations
    
    def _test_rate_limiting(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Rate Limiting"""
        score = 0
        details = []
        recommendations = []
        
        c2_path = self.project_path / "dlnk_c2_logging.py"
        if c2_path.exists():
            content = c2_path.read_text()
            
            if "rate_limit" in content.lower():
                score += 40
                details.append("✓ Rate limiting implemented")
            
            if "per_minute" in content.lower() or "MAX_REQUESTS" in content:
                score += 30
                details.append("✓ Configurable limits")
            
            if "window" in content.lower():
                score += 30
                details.append("✓ Time window tracking")
        else:
            recommendations.append("Implement rate limiting in C2 logging")
        
        return score, "\n".join(details), recommendations
    
    def _test_self_attack_prevention(self) -> Tuple[float, str, List[str]]:
        """ทดสอบการป้องกันการโจมตีตัวเอง"""
        score = 0
        details = []
        recommendations = []
        
        filter_path = self.project_path / "dlnk_prompt_filter.py"
        if filter_path.exists():
            content = filter_path.read_text()
            
            keywords = ["dlnk", "antigravity", "jetski", "admin", "license", "telegram"]
            found_keywords = sum(1 for kw in keywords if kw in content.lower())
            
            score = (found_keywords / len(keywords)) * 100
            details.append(f"✓ Protects {found_keywords}/{len(keywords)} sensitive keywords")
            
            if found_keywords < len(keywords):
                missing = [kw for kw in keywords if kw not in content.lower()]
                recommendations.append(f"Add protection for: {', '.join(missing)}")
        else:
            recommendations.append("Create prompt filter with self-attack prevention")
        
        return score, "\n".join(details), recommendations
    
    def _test_error_handling(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Error Handling"""
        score = 0
        details = []
        recommendations = []
        
        py_files = list(self.project_path.glob("*.py"))
        total_try_except = 0
        
        for filepath in py_files:
            content = filepath.read_text()
            try_count = content.count("try:")
            except_count = content.count("except")
            total_try_except += min(try_count, except_count)
        
        if total_try_except >= 20:
            score = 100
        elif total_try_except >= 10:
            score = 70
        elif total_try_except >= 5:
            score = 50
        else:
            score = 30
        
        details.append(f"Found {total_try_except} try-except blocks")
        
        if score < 70:
            recommendations.append("Add more error handling throughout the codebase")
        
        return score, "\n".join(details), recommendations
    
    def _test_documentation(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Documentation"""
        score = 0
        details = []
        recommendations = []
        
        py_files = list(self.project_path.glob("*.py"))
        total_docstrings = 0
        
        for filepath in py_files:
            content = filepath.read_text()
            docstring_count = content.count('"""')
            total_docstrings += docstring_count // 2
        
        if total_docstrings >= 30:
            score = 100
        elif total_docstrings >= 15:
            score = 70
        elif total_docstrings >= 5:
            score = 50
        else:
            score = 30
        
        details.append(f"Found {total_docstrings} docstrings")
        
        if score < 70:
            recommendations.append("Add more docstrings to functions and classes")
        
        return score, "\n".join(details), recommendations
    
    def _test_module_structure(self) -> Tuple[float, str, List[str]]:
        """ทดสอบโครงสร้าง Module"""
        score = 0
        details = []
        recommendations = []
        
        required_files = [
            "dlnk_ai_bridge_v2.py",
            "dlnk_license_system.py",
            "dlnk_telegram_bot.py",
            "dlnk_admin_web.py",
            "dlnk_launcher_v2.py",
            "dlnk_prompt_filter.py",
            "dlnk_admin_auth.py",
            "dlnk_c2_logging.py",
        ]
        
        found = 0
        for filename in required_files:
            if (self.project_path / filename).exists():
                found += 1
                details.append(f"✓ {filename}")
            else:
                details.append(f"✗ {filename} missing")
                recommendations.append(f"Create {filename}")
        
        score = (found / len(required_files)) * 100
        
        return score, "\n".join(details), recommendations
    
    def _test_dependencies(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Dependencies"""
        score = 70  # Base score
        details = []
        recommendations = []
        
        # Check for requirements.txt
        req_path = self.project_path / "requirements.txt"
        if req_path.exists():
            score += 15
            details.append("✓ requirements.txt exists")
        else:
            recommendations.append("Create requirements.txt")
        
        # Check for common imports
        py_files = list(self.project_path.glob("*.py"))
        imports = set()
        
        for filepath in py_files:
            content = filepath.read_text()
            for line in content.split("\n"):
                if line.startswith("import ") or line.startswith("from "):
                    imports.add(line.split()[1].split(".")[0])
        
        details.append(f"Found {len(imports)} unique imports")
        score += min(15, len(imports))
        
        return score, "\n".join(details), recommendations
    
    def _test_ai_bridge(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ AI Bridge"""
        score = 0
        details = []
        recommendations = []
        
        bridge_path = self.project_path / "dlnk_ai_bridge_v2.py"
        if bridge_path.exists():
            content = bridge_path.read_text()
            
            if "openai" in content.lower() or "client" in content.lower():
                score += 25
                details.append("✓ AI client integration")
            
            if "websocket" in content.lower() or "async" in content.lower():
                score += 25
                details.append("✓ Async/WebSocket support")
            
            if "hash" in content.lower() and "token" in content.lower():
                score += 25
                details.append("✓ Hash token system")
            
            if "process_message" in content.lower():
                score += 25
                details.append("✓ Message processing")
        else:
            recommendations.append("AI Bridge file not found")
        
        return score, "\n".join(details), recommendations
    
    def _test_license_system(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ License System"""
        score = 0
        details = []
        recommendations = []
        
        license_path = self.project_path / "dlnk_license_system.py"
        if license_path.exists():
            content = license_path.read_text()
            
            if "create_license" in content.lower():
                score += 25
                details.append("✓ License creation")
            
            if "verify_license" in content.lower():
                score += 25
                details.append("✓ License verification")
            
            if "hwid" in content.lower():
                score += 25
                details.append("✓ HWID support")
            
            if "database" in content.lower() or "sqlite" in content.lower():
                score += 25
                details.append("✓ Database storage")
        else:
            recommendations.append("License system file not found")
        
        return score, "\n".join(details), recommendations
    
    def _test_telegram_bot(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Telegram Bot"""
        score = 0
        details = []
        recommendations = []
        
        bot_path = self.project_path / "dlnk_telegram_bot.py"
        if bot_path.exists():
            content = bot_path.read_text()
            
            if "telegram" in content.lower() or "telebot" in content.lower():
                score += 25
                details.append("✓ Telegram integration")
            
            if "handler" in content.lower() or "command" in content.lower():
                score += 25
                details.append("✓ Command handlers")
            
            if "admin" in content.lower():
                score += 25
                details.append("✓ Admin functions")
            
            if "broadcast" in content.lower():
                score += 25
                details.append("✓ Broadcast capability")
            else:
                recommendations.append("Add broadcast functionality")
        else:
            recommendations.append("Telegram bot file not found")
        
        return score, "\n".join(details), recommendations
    
    def _test_admin_console(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ Admin Console"""
        score = 0
        details = []
        recommendations = []
        
        admin_path = self.project_path / "dlnk_admin_web.py"
        admin_v2_path = self.project_path / "dlnk_admin_web_v2.py"
        
        target_path = admin_v2_path if admin_v2_path.exists() else admin_path
        
        if target_path.exists():
            content = target_path.read_text()
            
            if "flask" in content.lower():
                score += 20
                details.append("✓ Flask framework")
            
            if "login" in content.lower():
                score += 25
                details.append("✓ Login system")
            else:
                recommendations.append("Add login authentication")
            
            if "dashboard" in content.lower():
                score += 20
                details.append("✓ Dashboard")
            
            if "license" in content.lower():
                score += 20
                details.append("✓ License management")
            
            if "api" in content.lower():
                score += 15
                details.append("✓ API endpoints")
        else:
            recommendations.append("Admin console file not found")
        
        return score, "\n".join(details), recommendations
    
    def _test_c2_logging(self) -> Tuple[float, str, List[str]]:
        """ทดสอบ C2 Logging"""
        score = 0
        details = []
        recommendations = []
        
        c2_path = self.project_path / "dlnk_c2_logging.py"
        if c2_path.exists():
            content = c2_path.read_text()
            
            if "log_request" in content.lower():
                score += 25
                details.append("✓ Request logging")
            
            if "alert" in content.lower():
                score += 25
                details.append("✓ Alert system")
            
            if "rate_limit" in content.lower():
                score += 25
                details.append("✓ Rate limiting")
            
            if "dashboard" in content.lower() or "stats" in content.lower():
                score += 25
                details.append("✓ Statistics/Dashboard")
        else:
            recommendations.append("C2 logging file not found")
        
        return score, "\n".join(details), recommendations
    
    def _calculate_overall_score(self):
        """คำนวณคะแนนรวม"""
        if not self.results:
            self.overall_score = 0
            return
        
        total = sum(r.score for r in self.results)
        self.overall_score = total / len(self.results)
        
        # Determine level
        if self.overall_score >= 90:
            self.level = "Expert"
        elif self.overall_score >= 75:
            self.level = "Advanced"
        elif self.overall_score >= 50:
            self.level = "Intermediate"
        else:
            self.level = "Beginner"
    
    def _generate_report(self) -> Dict:
        """สร้างรายงาน"""
        print("=" * 70)
        print("FINAL REPORT")
        print("=" * 70)
        print()
        
        # Summary by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        print("📊 Category Scores:")
        print("-" * 50)
        category_scores = {}
        for cat, results in categories.items():
            avg = sum(r.score for r in results) / len(results)
            category_scores[cat] = avg
            print(f"  {cat}: {avg:.1f}/100")
        
        print()
        print(f"🎯 Overall Score: {self.overall_score:.1f}/100")
        print(f"📈 Level: {self.level}")
        print()
        
        # Competitor comparison
        print("🏆 Competitor Comparison:")
        print("-" * 50)
        competitors = {
            "Worm v4-5": 85,
            "DeepNude v4": 80,
            "FraudGPT": 75,
            "WormGPT": 70,
        }
        
        for comp, score in competitors.items():
            comparison = "🟢 Ahead" if self.overall_score > score else "🔴 Behind"
            diff = self.overall_score - score
            print(f"  vs {comp}: {comparison} ({diff:+.1f})")
        
        print()
        
        # Top recommendations
        print("📋 Top Recommendations:")
        print("-" * 50)
        all_recommendations = []
        for result in self.results:
            for rec in result.recommendations:
                all_recommendations.append((result.category, rec))
        
        for i, (cat, rec) in enumerate(all_recommendations[:10], 1):
            print(f"  {i}. [{cat}] {rec}")
        
        print()
        print("=" * 70)
        
        return {
            "overall_score": self.overall_score,
            "level": self.level,
            "category_scores": category_scores,
            "results": [
                {
                    "name": r.name,
                    "category": r.category,
                    "score": r.score,
                    "passed": r.passed,
                    "details": r.details,
                    "recommendations": r.recommendations
                }
                for r in self.results
            ],
            "recommendations": all_recommendations[:10]
        }


# ===== MAIN =====

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk QA/Audit System')
    parser.add_argument('--path', default='/home/ubuntu/dlnk_project/core', help='Project path')
    parser.add_argument('--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    qa = DLNKQAAudit(args.path)
    report = qa.run_all_tests()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")
