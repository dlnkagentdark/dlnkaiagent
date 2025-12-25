#!/usr/bin/env python3
"""
Test Encryption
ทดสอบระบบเข้ารหัส
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encryption import (
    TokenEncryption,
    ConfigEncryption,
    LogEncryption,
    SecureTokenStorage,
    SecureConfigManager
)


def test_token_encryption():
    """ทดสอบ Token Encryption"""
    print("\n=== Testing Token Encryption ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        key_file = os.path.join(tmpdir, ".test_key")
        enc = TokenEncryption(key_file=key_file)
        
        # Test basic encryption/decryption
        original_token = "sk-test-api-key-12345"
        
        encrypted = enc.encrypt(original_token, token_type="api_key")
        print(f"Original: {original_token}")
        print(f"Encrypted: {encrypted.encrypted_data[:50]}...")
        
        decrypted = enc.decrypt(encrypted)
        print(f"Decrypted: {decrypted}")
        
        assert decrypted == original_token, "Decryption failed"
        print("\n✅ Basic encryption test passed")
        
        # Test with expiration
        encrypted_exp = enc.encrypt(original_token, expires_hours=24)
        assert encrypted_exp.expires_at is not None, "Expiration not set"
        print("✅ Expiration test passed")
        
        # Test dictionary encryption
        data = {
            "api_key": "secret123",
            "username": "test_user",
            "password": "pass123"
        }
        
        encrypted_dict = enc.encrypt_dict(data)
        assert encrypted_dict["api_key"]["_encrypted"], "API key not encrypted"
        assert encrypted_dict["password"]["_encrypted"], "Password not encrypted"
        assert encrypted_dict["username"] == "test_user", "Username should not be encrypted"
        print("✅ Dictionary encryption test passed")
    
    return True


def test_config_encryption():
    """ทดสอบ Config Encryption"""
    print("\n=== Testing Config Encryption ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        key_file = os.path.join(tmpdir, ".config_key")
        enc = ConfigEncryption(key_file=key_file)
        
        # Test config encryption
        config = {
            "database": {
                "host": "localhost",
                "port": 3306,
                "password": "secret123"
            },
            "api": {
                "key": "api-key-12345",
                "endpoint": "https://api.example.com"
            }
        }
        
        encrypted = enc.encrypt_config(config)
        print(f"Encrypted data: {encrypted.encrypted_data[:50]}...")
        print(f"Checksum: {encrypted.checksum}")
        
        decrypted = enc.decrypt_config(encrypted)
        assert decrypted == config, "Config decryption failed"
        print("\n✅ Config encryption test passed")
        
        # Test file save/load
        config_file = os.path.join(tmpdir, "test_config.enc")
        enc.save_encrypted_config(config, config_file)
        
        loaded = enc.load_encrypted_config(config_file)
        assert loaded == config, "Config load failed"
        print("✅ Config file save/load test passed")
    
    return True


def test_log_encryption():
    """ทดสอบ Log Encryption"""
    print("\n=== Testing Log Encryption ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        key_file = os.path.join(tmpdir, ".log_key")
        enc = LogEncryption(key_file=key_file)
        
        # Test log entry encryption
        log_data = "2024-01-01 12:00:00 - User login: admin from 192.168.1.1"
        
        encrypted = enc.encrypt_entry(log_data)
        print(f"Original: {log_data}")
        print(f"Encrypted: {encrypted.encrypted_data[:50]}...")
        
        decrypted = enc.decrypt_entry(encrypted)
        assert decrypted == log_data, "Log decryption failed"
        print("\n✅ Log entry encryption test passed")
        
        # Test dictionary log
        log_dict = {
            "timestamp": "2024-01-01T12:00:00",
            "level": "INFO",
            "message": "User action completed",
            "user_id": "user123"
        }
        
        encrypted_dict = enc.encrypt_dict(log_dict)
        assert encrypted_dict["_encrypted"], "Dict not encrypted"
        
        decrypted_dict = enc.decrypt_dict(encrypted_dict)
        assert decrypted_dict == log_dict, "Dict decryption failed"
        print("✅ Dictionary log encryption test passed")
    
    return True


def test_secure_token_storage():
    """ทดสอบ Secure Token Storage"""
    print("\n=== Testing Secure Token Storage ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_file = os.path.join(tmpdir, ".tokens")
        key_file = os.path.join(tmpdir, ".token_key")
        
        enc = TokenEncryption(key_file=key_file)
        storage = SecureTokenStorage(storage_file=storage_file, encryption=enc)
        
        # Store tokens
        storage.store("openai_key", "sk-test-12345", token_type="api_key")
        storage.store("github_token", "ghp_test-67890", token_type="access_token")
        
        print("Stored tokens:", storage.list_tokens())
        
        # Retrieve tokens
        openai_key = storage.retrieve("openai_key")
        assert openai_key == "sk-test-12345", "OpenAI key retrieval failed"
        print(f"Retrieved OpenAI key: {openai_key}")
        
        github_token = storage.retrieve("github_token")
        assert github_token == "ghp_test-67890", "GitHub token retrieval failed"
        print(f"Retrieved GitHub token: {github_token}")
        
        # Delete token
        storage.delete("github_token")
        assert storage.retrieve("github_token") is None, "Token should be deleted"
        print("✅ Token deletion test passed")
        
        print("\n✅ Secure Token Storage test passed")
    
    return True


def test_secure_config_manager():
    """ทดสอบ Secure Config Manager"""
    print("\n=== Testing Secure Config Manager ===\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = os.path.join(tmpdir, "config")
        key_file = os.path.join(tmpdir, ".config_key")
        
        enc = ConfigEncryption(key_file=key_file)
        manager = SecureConfigManager(config_dir=config_dir, encryption=enc)
        
        # Save config
        config = {
            "app": {
                "name": "dLNk IDE",
                "version": "1.0.0"
            },
            "security": {
                "enabled": True,
                "level": "high"
            }
        }
        
        manager.save("app_config", config)
        print("Saved config:", manager.list_configs())
        
        # Load config
        loaded = manager.load("app_config")
        assert loaded == config, "Config load failed"
        print(f"Loaded config: {loaded}")
        
        # Get specific key
        app_name = manager.get("app_config", "app.name")
        assert app_name == "dLNk IDE", "Get key failed"
        print(f"App name: {app_name}")
        
        # Set specific key
        manager.set("app_config", "app.version", "1.1.0")
        new_version = manager.get("app_config", "app.version")
        assert new_version == "1.1.0", "Set key failed"
        print(f"Updated version: {new_version}")
        
        # Delete config
        manager.delete("app_config")
        assert manager.load("app_config") is None, "Config should be deleted"
        print("✅ Config deletion test passed")
        
        print("\n✅ Secure Config Manager test passed")
    
    return True


def run_all_tests():
    """รันทุกการทดสอบ"""
    print("\n" + "=" * 60)
    print("dLNk Encryption Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Token Encryption", test_token_encryption()))
    results.append(("Config Encryption", test_config_encryption()))
    results.append(("Log Encryption", test_log_encryption()))
    results.append(("Secure Token Storage", test_secure_token_storage()))
    results.append(("Secure Config Manager", test_secure_config_manager()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
