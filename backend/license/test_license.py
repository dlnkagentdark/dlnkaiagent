#!/usr/bin/env python3
"""
Test Script for dLNk License System
ทดสอบระบบ License และ Authentication
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config():
    """Test configuration"""
    print("\n" + "="*60)
    print("Testing Configuration...")
    print("="*60)
    
    from config import get_config, Config
    
    config = get_config()
    Config.init_directories()
    
    print(f"✓ Database Path: {config.DATABASE_PATH}")
    print(f"✓ API Host: {config.API_HOST}")
    print(f"✓ API Port: {config.API_PORT}")
    print(f"✓ License Prefix: {config.LICENSE_PREFIX}")
    print(f"✓ Session Lifetime: {config.SESSION_LIFETIME_HOURS} hours")
    print(f"✓ Offline Grace Days: {config.OFFLINE_GRACE_DAYS} days")
    
    return True


def test_encryption():
    """Test encryption"""
    print("\n" + "="*60)
    print("Testing Encryption...")
    print("="*60)
    
    from utils.encryption import encrypt, decrypt
    
    # Test string encryption
    test_data = "Hello, dLNk!"
    encrypted = encrypt(test_data)
    decrypted = decrypt(encrypted)
    
    assert decrypted == test_data, "String encryption failed"
    print(f"✓ String encryption: {test_data} -> {encrypted[:30]}...")
    
    # Test dict encryption
    test_dict = {"name": "John", "license": "pro", "features": ["ai_chat", "code_complete"]}
    encrypted_dict = encrypt(test_dict)
    decrypted_dict = decrypt(encrypted_dict)
    
    assert decrypted_dict == test_dict, "Dict encryption failed"
    print(f"✓ Dict encryption: {test_dict}")
    
    return True


def test_hardware_id():
    """Test hardware ID generation"""
    print("\n" + "="*60)
    print("Testing Hardware ID...")
    print("="*60)
    
    from license.hardware import HardwareID, get_hardware_id, get_hardware_id_short
    
    hwid = get_hardware_id()
    hwid_short = get_hardware_id_short()
    
    print(f"✓ Hardware ID: {hwid}")
    print(f"✓ Hardware ID (short): {hwid_short}")
    
    # Test consistency
    hwid2 = get_hardware_id()
    assert hwid == hwid2, "Hardware ID not consistent"
    print(f"✓ Hardware ID is consistent")
    
    # Get system info
    info = HardwareID.get_system_info()
    print(f"✓ Platform: {info['platform']}")
    print(f"✓ Hostname: {info['hostname']}")
    
    return True


def test_license_generation():
    """Test license generation"""
    print("\n" + "="*60)
    print("Testing License Generation...")
    print("="*60)
    
    from license import generate_license, generate_encrypted_license
    
    # Test formatted license
    license_key, encrypted_data = generate_license(
        user_id="test_user",
        license_type="pro",
        duration_days=30,
        owner_name="Test User",
        email="test@example.com"
    )
    
    print(f"✓ Generated License Key: {license_key}")
    print(f"✓ Encrypted Data Length: {len(encrypted_data)} chars")
    
    # Verify format
    import re
    pattern = r'^DLNK-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$'
    assert re.match(pattern, license_key), "License key format invalid"
    print(f"✓ License key format is valid")
    
    # Test encrypted license (legacy)
    encrypted = generate_encrypted_license(days_valid=30, owner="Legacy User")
    print(f"✓ Encrypted License: {encrypted[:50]}...")
    
    return license_key, encrypted_data


def test_license_storage(license_key, encrypted_data):
    """Test license storage"""
    print("\n" + "="*60)
    print("Testing License Storage...")
    print("="*60)
    
    from license import license_storage, LicenseData
    from datetime import datetime, timedelta
    
    # Create license data
    license_data = LicenseData(
        license_id=license_key.replace("DLNK-", ""),
        user_id="test_user",
        license_type="pro",
        created_at=datetime.now().isoformat(),
        expires_at=(datetime.now() + timedelta(days=30)).isoformat(),
        features=["ai_chat", "code_complete"],
        owner_name="Test User",
        email="test@example.com"
    )
    
    # Store license
    success = license_storage.store_license(license_key, license_data, encrypted_data)
    print(f"✓ License stored: {success}")
    
    # Retrieve license
    retrieved = license_storage.get_license(license_key)
    assert retrieved is not None, "Failed to retrieve license"
    print(f"✓ License retrieved: {retrieved['license_key']}")
    
    # Get statistics
    stats = license_storage.get_statistics()
    print(f"✓ Total licenses: {stats['total_licenses']}")
    print(f"✓ Active licenses: {stats['active_licenses']}")
    
    return True


def test_license_validation(license_key):
    """Test license validation"""
    print("\n" + "="*60)
    print("Testing License Validation...")
    print("="*60)
    
    from license import validate_license, get_hardware_id
    
    hwid = get_hardware_id()
    result = validate_license(license_key, hwid)
    
    print(f"✓ Valid: {result.valid}")
    print(f"✓ Features: {result.features}")
    print(f"✓ Days Remaining: {result.days_remaining}")
    
    if result.warning:
        print(f"⚠ Warning: {result.warning}")
    
    if result.error:
        print(f"✗ Error: {result.error}")
    
    return result.valid


def test_user_creation():
    """Test user creation"""
    print("\n" + "="*60)
    print("Testing User Creation...")
    print("="*60)
    
    from auth import login_manager
    
    # Create user
    success, message, user = login_manager.create_user(
        username="testuser",
        password="TestPass123!",
        email="testuser@example.com",
        role="user"
    )
    
    if success:
        print(f"✓ User created: {user.username}")
        print(f"✓ User ID: {user.user_id}")
        print(f"✓ Role: {user.role}")
        return user
    else:
        if "already exists" in message:
            print(f"⚠ User already exists, skipping creation")
            return None
        print(f"✗ Failed: {message}")
        return None


def test_login():
    """Test login"""
    print("\n" + "="*60)
    print("Testing Login...")
    print("="*60)
    
    from auth import login_manager
    
    result = login_manager.login(
        username="testuser",
        password="TestPass123!",
        remember=True
    )
    
    print(f"✓ Login Success: {result.success}")
    
    if result.success:
        print(f"✓ Session ID: {result.session_id[:20]}...")
        print(f"✓ User: {result.user.username}")
        print(f"✓ Offline Mode: {result.offline_mode}")
        return result.session_id
    else:
        print(f"✗ Error: {result.error}")
        return None


def test_session(session_id):
    """Test session validation"""
    print("\n" + "="*60)
    print("Testing Session...")
    print("="*60)
    
    from auth import session_manager
    
    if not session_id:
        print("⚠ No session to test")
        return False
    
    # Validate session
    session_data = session_manager.validate_session(session_id)
    
    if session_data:
        print(f"✓ Session Valid")
        print(f"✓ User ID: {session_data['user_id']}")
        print(f"✓ Username: {session_data['username']}")
        return True
    else:
        print(f"✗ Session Invalid")
        return False


def test_2fa():
    """Test 2FA"""
    print("\n" + "="*60)
    print("Testing 2FA...")
    print("="*60)
    
    from auth import is_2fa_available, setup_2fa, verify_2fa
    
    print(f"✓ 2FA Available: {is_2fa_available()}")
    
    if is_2fa_available():
        secret, uri, qr_code = setup_2fa("testuser")
        print(f"✓ TOTP Secret: {secret}")
        print(f"✓ TOTP URI: {uri[:50]}...")
        print(f"✓ QR Code Generated: {qr_code is not None}")
        
        # Get current code for testing
        from auth.totp import totp_manager
        current_code = totp_manager.get_current_code(secret)
        print(f"✓ Current Code: {current_code}")
        
        # Verify code
        is_valid = verify_2fa(secret, current_code)
        print(f"✓ Code Verification: {is_valid}")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🔑 dLNk License System - Test Suite")
    print("="*60)
    
    results = {}
    
    try:
        results['config'] = test_config()
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        results['config'] = False
    
    try:
        results['encryption'] = test_encryption()
    except Exception as e:
        print(f"✗ Encryption test failed: {e}")
        results['encryption'] = False
    
    try:
        results['hardware_id'] = test_hardware_id()
    except Exception as e:
        print(f"✗ Hardware ID test failed: {e}")
        results['hardware_id'] = False
    
    try:
        license_key, encrypted_data = test_license_generation()
        results['license_generation'] = True
    except Exception as e:
        print(f"✗ License generation test failed: {e}")
        results['license_generation'] = False
        license_key, encrypted_data = None, None
    
    if license_key:
        try:
            results['license_storage'] = test_license_storage(license_key, encrypted_data)
        except Exception as e:
            print(f"✗ License storage test failed: {e}")
            results['license_storage'] = False
        
        try:
            results['license_validation'] = test_license_validation(license_key)
        except Exception as e:
            print(f"✗ License validation test failed: {e}")
            results['license_validation'] = False
    
    try:
        test_user_creation()
        results['user_creation'] = True
    except Exception as e:
        print(f"✗ User creation test failed: {e}")
        results['user_creation'] = False
    
    try:
        session_id = test_login()
        results['login'] = session_id is not None
    except Exception as e:
        print(f"✗ Login test failed: {e}")
        results['login'] = False
        session_id = None
    
    if session_id:
        try:
            results['session'] = test_session(session_id)
        except Exception as e:
            print(f"✗ Session test failed: {e}")
            results['session'] = False
    
    try:
        results['2fa'] = test_2fa()
    except Exception as e:
        print(f"✗ 2FA test failed: {e}")
        results['2fa'] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
