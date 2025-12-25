#!/usr/bin/env python3
"""
Integration Test for dLNk Telegram Bot
Tests integration with Security System and Backend API
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from config import BOT_TOKEN, ADMIN_CHAT_IDS, APIConfig
        print("✅ config.py imported successfully")
    except Exception as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from bot.bot import DLNkBot
        print("✅ bot.bot imported successfully")
    except Exception as e:
        print(f"❌ Failed to import bot: {e}")
        return False
    
    try:
        from api_client.backend import BackendAPIClient
        print("✅ api_client.backend imported successfully")
    except Exception as e:
        print(f"❌ Failed to import api_client: {e}")
        return False
    
    try:
        from notifications.alert_sender import AlertSender, AlertSeverity, AlertType
        print("✅ notifications.alert_sender imported successfully")
    except Exception as e:
        print(f"❌ Failed to import alert_sender: {e}")
        return False
    
    try:
        from notifications.templates import MessageTemplates
        print("✅ notifications.templates imported successfully")
    except Exception as e:
        print(f"❌ Failed to import templates: {e}")
        return False
    
    try:
        from bot.handlers import commands, callbacks, inline
        print("✅ bot.handlers imported successfully")
    except Exception as e:
        print(f"❌ Failed to import handlers: {e}")
        return False
    
    try:
        from bot.keyboards import main_menu, inline as kb_inline
        print("✅ bot.keyboards imported successfully")
    except Exception as e:
        print(f"❌ Failed to import keyboards: {e}")
        return False
    
    try:
        from bot.middleware import auth, rate_limit
        print("✅ bot.middleware imported successfully")
    except Exception as e:
        print(f"❌ Failed to import middleware: {e}")
        return False
    
    return True

def test_security_integration():
    """Test Security System integration points"""
    print("\n🔒 Testing Security integration...")
    
    try:
        from notifications.alert_sender import AlertSender, AlertSeverity, AlertType
        
        # Check AlertType has SECURITY
        assert hasattr(AlertType, 'SECURITY'), "AlertType.SECURITY not found"
        print("✅ AlertType.SECURITY exists")
        
        # Check AlertSeverity levels
        assert hasattr(AlertSeverity, 'LOW'), "AlertSeverity.LOW not found"
        assert hasattr(AlertSeverity, 'MEDIUM'), "AlertSeverity.MEDIUM not found"
        assert hasattr(AlertSeverity, 'HIGH'), "AlertSeverity.HIGH not found"
        assert hasattr(AlertSeverity, 'CRITICAL'), "AlertSeverity.CRITICAL not found"
        print("✅ AlertSeverity levels exist")
        
        return True
    except Exception as e:
        print(f"❌ Security integration test failed: {e}")
        return False

def test_backend_integration():
    """Test Backend API integration points"""
    print("\n🔌 Testing Backend API integration...")
    
    try:
        from api_client.backend import BackendAPIClient
        
        # Check if BackendAPIClient has required methods
        client = BackendAPIClient()
        
        required_methods = [
            '_get_client',
            'close',
            '_request'
        ]
        
        for method in required_methods:
            assert hasattr(client, method), f"BackendAPIClient.{method} not found"
            print(f"✅ BackendAPIClient.{method} exists")
        
        return True
    except Exception as e:
        print(f"❌ Backend integration test failed: {e}")
        return False

def test_message_templates():
    """Test message templates"""
    print("\n📝 Testing message templates...")
    
    try:
        from notifications.templates import MessageTemplates
        
        templates = MessageTemplates()
        
        # Test security_alert template
        msg = templates.security_alert(
            title="Test Alert",
            message="Test message",
            severity=3,
            user_id="test123",
            ip_address="127.0.0.1",
            timestamp="2025-12-24 16:00:00"
        )
        assert "Test Alert" in msg, "security_alert template failed"
        print("✅ security_alert template works")
        
        return True
    except Exception as e:
        print(f"❌ Message template test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🤖 dLNk Telegram Bot - Integration Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Security Integration", test_security_integration()))
    results.append(("Backend Integration", test_backend_integration()))
    results.append(("Message Templates", test_message_templates()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Bot is ready for integration.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
