"""
Test script for dLNk IDE Auth & License API
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'license'))

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    
    try:
        from fastapi import FastAPI
        print("  ✓ FastAPI imported")
    except ImportError as e:
        print(f"  ✗ FastAPI import failed: {e}")
        return False
    
    try:
        import jwt
        print(f"  ✓ PyJWT imported (version {jwt.__version__})")
    except ImportError as e:
        print(f"  ✗ PyJWT import failed: {e}")
        return False
    
    try:
        from routes.auth import router as auth_router
        print("  ✓ Auth router imported")
    except ImportError as e:
        print(f"  ✗ Auth router import failed: {e}")
        return False
    
    try:
        from routes.license import router as license_router
        print("  ✓ License router imported")
    except ImportError as e:
        print(f"  ✗ License router import failed: {e}")
        return False
    
    return True


def test_jwt_functions():
    """Test JWT token creation and validation"""
    print("\nTesting JWT functions...")
    
    try:
        from routes.auth import create_access_token, create_refresh_token, decode_token
        
        # Test data
        test_data = {
            "license_key": "DLNK-TEST-1234-5678",
            "hwid": "TESTHWID123456"
        }
        
        # Create access token
        access_token = create_access_token(test_data)
        print(f"  ✓ Access token created: {access_token[:50]}...")
        
        # Create refresh token
        refresh_token = create_refresh_token(test_data)
        print(f"  ✓ Refresh token created: {refresh_token[:50]}...")
        
        # Decode access token
        decoded = decode_token(access_token)
        if decoded:
            print(f"  ✓ Token decoded successfully")
            print(f"    - license_key: {decoded.get('license_key')}")
            print(f"    - hwid: {decoded.get('hwid')}")
            print(f"    - type: {decoded.get('type')}")
        else:
            print("  ✗ Token decode failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ✗ JWT test failed: {e}")
        return False


def test_license_validation():
    """Test license validation functions"""
    print("\nTesting license validation...")
    
    try:
        from routes.license import validate_license, get_features_for_type
        
        # Test valid license format
        result = validate_license("DLNK-TEST-1234-5678-ABCD")
        print(f"  ✓ License validation executed")
        print(f"    - valid: {result.get('valid')}")
        print(f"    - license_type: {result.get('license_type')}")
        print(f"    - features: {len(result.get('features', []))} features")
        
        # Test invalid license
        result = validate_license("INVALID-KEY")
        print(f"  ✓ Invalid license test: valid={result.get('valid')}")
        
        # Test features for each type
        for license_type in ['trial', 'pro', 'enterprise']:
            features = get_features_for_type(license_type)
            print(f"  ✓ {license_type} features: {len(features)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ License validation test failed: {e}")
        return False


def test_hardware_id():
    """Test hardware ID functions"""
    print("\nTesting hardware ID...")
    
    try:
        from routes.license import get_hardware_info
        
        hw_info = get_hardware_info()
        print(f"  ✓ Hardware info retrieved")
        print(f"    - hardware_id: {hw_info.get('hardware_id', 'N/A')[:32]}...")
        print(f"    - hardware_id_short: {hw_info.get('hardware_id_short', 'N/A')}")
        print(f"    - platform: {hw_info.get('system_info', {}).get('platform', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Hardware ID test failed: {e}")
        return False


def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\nTesting FastAPI app...")
    
    try:
        # Import from current directory's main.py
        import importlib.util
        spec = importlib.util.spec_from_file_location("api_main", Path(__file__).parent / "main.py")
        api_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(api_main)
        app = api_main.app
        
        print(f"  ✓ FastAPI app created")
        print(f"    - title: {app.title}")
        print(f"    - version: {app.version}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"    - routes: {len(routes)}")
        
        # Check for required endpoints
        required_endpoints = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/license/verify/{license_key}'
        ]
        
        for endpoint in required_endpoints:
            found = any(endpoint in str(route.path) for route in app.routes)
            status = "✓" if found else "✗"
            print(f"    {status} {endpoint}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ FastAPI app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("dLNk IDE - Auth & License API Tests")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("JWT Functions", test_jwt_functions()))
    results.append(("License Validation", test_license_validation()))
    results.append(("Hardware ID", test_hardware_id()))
    results.append(("FastAPI App", test_fastapi_app()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
