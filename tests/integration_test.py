#!/usr/bin/env python3
"""
dLNk IDE - Integration Test Suite
==================================
ทดสอบการเชื่อมต่อระหว่าง Components ทั้งหมด

Author: AI Controller (Integration Testing)
Date: December 25, 2025
"""

import sys
import os
import asyncio
import json
import importlib
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Test results
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'errors': [],
    'details': []
}

def log_test(name: str, passed: bool, message: str = ""):
    """Log test result"""
    test_results['total'] += 1
    if passed:
        test_results['passed'] += 1
        print(f"✅ {name}")
    else:
        test_results['failed'] += 1
        test_results['errors'].append(f"{name}: {message}")
        print(f"❌ {name}: {message}")
    
    test_results['details'].append({
        'name': name,
        'passed': passed,
        'message': message
    })

def test_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def reset_sys_path():
    """Reset sys.path to avoid conflicts"""
    # Remove all project-specific paths
    paths_to_remove = []
    for p in sys.path:
        if 'dLNk-IDE-Project' in p:
            paths_to_remove.append(p)
    for p in paths_to_remove:
        sys.path.remove(p)
    
    # Clear cached modules
    modules_to_remove = []
    for mod_name in sys.modules:
        if 'config' in mod_name or 'license' in mod_name or 'auth' in mod_name:
            modules_to_remove.append(mod_name)
    for mod_name in modules_to_remove:
        del sys.modules[mod_name]

def run_in_subprocess(test_code: str, cwd: str) -> tuple:
    """Run test code in subprocess to avoid import conflicts"""
    import subprocess
    result = subprocess.run(
        ['python3.11', '-c', test_code],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.returncode == 0, result.stdout + result.stderr


# ============================================================
# Test 1: License System
# ============================================================
def test_license_system():
    test_section("1. License System")
    
    license_dir = str(PROJECT_ROOT / 'backend' / 'license')
    
    # Test Config
    test_code = """
import sys
sys.path.insert(0, '.')
from config import get_config
config = get_config()
print(f"Database: {config.DATABASE_PATH}")
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("License Config", "SUCCESS" in output, output.split('\n')[-2] if not passed else "")
    
    # Test License Generator
    test_code = """
import sys
sys.path.insert(0, '.')
from license.generator import LicenseGenerator
gen = LicenseGenerator()
key, encrypted = gen.generate(user_id='test_user', license_type='trial', duration_days=14)
if key and key.startswith('DLNK-'):
    print(f"Generated: {key}")
    print("SUCCESS")
else:
    print(f"Invalid key: {key}")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("License Generation", "SUCCESS" in output, output.strip().split('\n')[-1] if not passed else "")
    
    # Test License Validator
    test_code = """
import sys
sys.path.insert(0, '.')
from license.validator import LicenseValidator
validator = LicenseValidator()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("License Validator", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Hardware ID
    test_code = """
import sys
sys.path.insert(0, '.')
from license.hardware import get_hardware_id
hwid = get_hardware_id()
if hwid and len(hwid) == 64:
    print(f"HWID: {hwid[:16]}...")
    print("SUCCESS")
else:
    print(f"Invalid HWID: {hwid}")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("Hardware ID", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Storage
    test_code = """
import sys
sys.path.insert(0, '.')
from license.storage import LicenseStorage
storage = LicenseStorage()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("License Storage", "SUCCESS" in output, output.strip() if not passed else "")


# ============================================================
# Test 2: Authentication System
# ============================================================
def test_auth_system():
    test_section("2. Authentication System")
    
    license_dir = str(PROJECT_ROOT / 'backend' / 'license')
    
    # Test Login Manager
    test_code = """
import sys
sys.path.insert(0, '.')
from auth.login import LoginManager
login_mgr = LoginManager()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("Login Manager", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test TOTP
    test_code = """
import sys
sys.path.insert(0, '.')
from auth.totp import TOTPManager
totp = TOTPManager()
secret = totp.generate_secret()
if secret and len(secret) > 10:
    print(f"Secret: {secret[:10]}...")
    print("SUCCESS")
else:
    print(f"Invalid secret: {secret}")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("TOTP Manager", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Session
    test_code = """
import sys
sys.path.insert(0, '.')
from auth.session import SessionManager
session = SessionManager()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("Session Manager", "SUCCESS" in output, output.strip() if not passed else "")


# ============================================================
# Test 3: AI Bridge Components
# ============================================================
def test_ai_bridge():
    test_section("3. AI Bridge Components")
    
    bridge_dir = str(PROJECT_ROOT / 'backend' / 'ai-bridge')
    
    # Test Config
    test_code = """
import sys
sys.path.insert(0, '.')
from config import Config
config = Config()
print(f"WS Port: {config.WS_PORT}")
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, bridge_dir)
    log_test("AI Bridge Config", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Token Manager
    test_code = """
import sys
sys.path.insert(0, '.')
from token_manager.token_refresh import TokenManager
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, bridge_dir)
    log_test("Token Manager", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test gRPC Client
    test_code = """
import sys
sys.path.insert(0, '.')
from grpc_client.antigravity_client import AntigravityClient
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, bridge_dir)
    log_test("Antigravity Client", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Proto Encoder
    test_code = """
import sys
sys.path.insert(0, '.')
from grpc_client.proto_encoder import ProtoEncoder
encoder = ProtoEncoder()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, bridge_dir)
    log_test("Proto Encoder", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Provider Manager
    test_code = """
import sys
sys.path.insert(0, '.')
from fallback.provider_manager import ProviderManager
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, bridge_dir)
    log_test("Provider Manager", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test WebSocket Server
    test_code = """
import sys
sys.path.insert(0, '.')
from servers.websocket_server import WebSocketServer
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, bridge_dir)
    log_test("WebSocket Server", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test REST Server
    test_code = """
import sys
sys.path.insert(0, '.')
from servers.rest_server import RESTServer
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, bridge_dir)
    log_test("REST Server", "SUCCESS" in output, output.strip() if not passed else "")


# ============================================================
# Test 4: Security System
# ============================================================
def test_security_system():
    test_section("4. Security System")
    
    security_dir = str(PROJECT_ROOT / 'security')
    
    # Test Prompt Filter
    test_code = """
import sys
sys.path.insert(0, '.')
from prompt_filter.filter import PromptFilter
pf = PromptFilter()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, security_dir)
    log_test("Prompt Filter", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Prompt Filter - Safe Prompt
    test_code = """
import sys
sys.path.insert(0, '.')
from prompt_filter.filter import PromptFilter
pf = PromptFilter()
result = pf.filter("Hello, how are you?")
if hasattr(result, 'allowed'):
    if result.allowed:
        print("SUCCESS")
    else:
        print(f"Blocked: {result.reason}")
elif isinstance(result, dict):
    if result.get('allowed', False):
        print("SUCCESS")
    else:
        print(f"Blocked: {result.get('reason', 'unknown')}")
else:
    print(f"Unknown result type: {type(result)}")
"""
    passed, output = run_in_subprocess(test_code, security_dir)
    log_test("Prompt Filter - Safe Prompt", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Activity Logger
    test_code = """
import sys
sys.path.insert(0, '.')
from activity.logger import ActivityLogger
logger = ActivityLogger()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, security_dir)
    log_test("Activity Logger", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Anomaly Detector
    test_code = """
import sys
sys.path.insert(0, '.')
from anomaly.detector import AnomalyDetector
detector = AnomalyDetector()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, security_dir)
    log_test("Anomaly Detector", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Rate Limiter
    test_code = """
import sys
sys.path.insert(0, '.')
from anomaly.rate_limiter import RateLimiter
limiter = RateLimiter()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, security_dir)
    log_test("Rate Limiter", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Test Alert Manager
    test_code = """
import sys
sys.path.insert(0, '.')
from alerts.alert_manager import AlertManager
alert_mgr = AlertManager()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, security_dir)
    log_test("Alert Manager", "SUCCESS" in output, output.strip() if not passed else "")


# ============================================================
# Test 5: Encryption
# ============================================================
def test_encryption():
    test_section("5. Encryption")
    
    # License Encryption
    license_dir = str(PROJECT_ROOT / 'backend' / 'license')
    test_code = """
import sys
sys.path.insert(0, '.')
from utils.encryption import encrypt_string, decrypt_string
original = "Test encryption message"
encrypted = encrypt_string(original)
decrypted = decrypt_string(encrypted)
if decrypted == original:
    print("SUCCESS")
else:
    print(f"Mismatch: {original} != {decrypted}")
"""
    passed, output = run_in_subprocess(test_code, license_dir)
    log_test("License Encryption", "SUCCESS" in output, output.strip() if not passed else "")
    
    # Security Token Encryption
    security_dir = str(PROJECT_ROOT / 'security')
    test_code = """
import sys
sys.path.insert(0, '.')
from encryption.token_encryption import TokenEncryption
te = TokenEncryption()
print("SUCCESS")
"""
    passed, output = run_in_subprocess(test_code, security_dir)
    log_test("Security Token Encryption", "SUCCESS" in output, output.strip() if not passed else "")


# ============================================================
# Test 6: Full License Test Suite
# ============================================================
def test_full_license_suite():
    test_section("6. Full License Test Suite")
    
    license_dir = str(PROJECT_ROOT / 'backend' / 'license')
    
    # Run the original test suite
    import subprocess
    result = subprocess.run(
        ['python3.11', 'test_license.py'],
        cwd=license_dir,
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Check for success indicators
    output = result.stdout + result.stderr
    
    # Count passed tests
    passed_count = output.count('✓')
    failed_count = output.count('✗')
    
    if passed_count > 0 and failed_count == 0:
        log_test(f"License Test Suite ({passed_count} tests)", True)
    else:
        log_test(f"License Test Suite ({passed_count} passed, {failed_count} failed)", 
                 failed_count == 0, 
                 f"Some tests failed")


# ============================================================
# Main
# ============================================================
def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     dLNk IDE - Integration Test Suite                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run all tests
    test_license_system()
    test_auth_system()
    test_ai_bridge()
    test_security_system()
    test_encryption()
    test_full_license_suite()
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  TEST SUMMARY")
    print(f"{'='*60}")
    print(f"\n  Total Tests: {test_results['total']}")
    print(f"  ✅ Passed: {test_results['passed']}")
    print(f"  ❌ Failed: {test_results['failed']}")
    
    if test_results['failed'] > 0:
        print(f"\n  Errors:")
        for error in test_results['errors']:
            print(f"    - {error}")
    
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\n  Success Rate: {success_rate:.1f}%")
    
    # Save results to file
    results_file = PROJECT_ROOT / 'tests' / 'integration_test_results.json'
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    print(f"\n  Results saved to: {results_file}")
    
    print(f"\n{'='*60}\n")
    
    return test_results['failed'] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
