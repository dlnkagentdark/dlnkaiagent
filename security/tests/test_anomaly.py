#!/usr/bin/env python3
"""
Test Anomaly Detection
ทดสอบระบบตรวจจับพฤติกรรมผิดปกติ
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anomaly import (
    AnomalyDetector,
    RateLimiter,
    RateLimitConfig,
    BruteForceDetector,
    BruteForceConfig
)


def test_rate_limiter():
    """ทดสอบ Rate Limiter"""
    print("\n=== Testing Rate Limiter ===\n")
    
    config = RateLimitConfig(
        requests_per_minute=5,
        requests_per_hour=20,
        requests_per_day=100,
        burst_limit=3
    )
    
    limiter = RateLimiter(config)
    
    user_id = "test_user"
    
    # Test normal requests
    print("Testing normal requests...")
    for i in range(5):
        status = limiter.check(user_id)
        print(f"  Request {i+1}: {'✅ Allowed' if status.allowed else '❌ Blocked'}")
    
    # Should be blocked now
    status = limiter.check(user_id)
    assert not status.allowed, "Should be blocked after limit"
    print(f"  Request 6: {'✅ Allowed' if status.allowed else '❌ Blocked (expected)'}")
    
    # Test reset
    limiter.reset_user(user_id)
    status = limiter.check(user_id)
    assert status.allowed, "Should be allowed after reset"
    print(f"  After reset: {'✅ Allowed' if status.allowed else '❌ Blocked'}")
    
    print("\n✅ Rate Limiter test passed")
    return True


def test_brute_force_detector():
    """ทดสอบ Brute Force Detector"""
    print("\n=== Testing Brute Force Detector ===\n")
    
    config = BruteForceConfig(
        max_attempts=3,
        window_minutes=5,
        lockout_minutes=1
    )
    
    detector = BruteForceDetector(config)
    
    user_id = "test_user"
    target = "login"
    
    # Test failed attempts
    print("Testing failed login attempts...")
    for i in range(3):
        status = detector.record_attempt(user_id, target, success=False)
        print(f"  Attempt {i+1}: Blocked={status.is_blocked}, "
              f"Remaining={status.remaining_attempts}")
    
    # Should be locked out now
    status = detector.record_attempt(user_id, target, success=False)
    assert status.is_blocked, "Should be blocked after max attempts"
    print(f"  Attempt 4: {'❌ Blocked (expected)' if status.is_blocked else '✅ Allowed'}")
    
    # Test successful login resets
    detector.reset_user(user_id, target)
    status = detector.record_attempt(user_id, target, success=True)
    assert not status.is_blocked, "Should not be blocked after success"
    print(f"  After success: {'❌ Blocked' if status.is_blocked else '✅ Allowed'}")
    
    print("\n✅ Brute Force Detector test passed")
    return True


def test_anomaly_detector():
    """ทดสอบ Anomaly Detector"""
    print("\n=== Testing Anomaly Detector ===\n")
    
    detector = AnomalyDetector(
        max_requests_per_minute=10,
        max_blocked_prompts=3,
        window_minutes=5
    )
    
    user_id = "test_user"
    
    # Test normal behavior
    print("Testing normal behavior...")
    for i in range(5):
        result = detector.check_request_rate(user_id)
        print(f"  Request {i+1}: Anomaly={result.is_anomaly}")
    
    # Test blocked prompts
    print("\nTesting blocked prompts detection...")
    for i in range(3):
        result = detector.check_blocked_prompts(user_id)
        print(f"  Blocked {i+1}: Anomaly={result.is_anomaly}")
    
    # Should detect anomaly now
    result = detector.check_blocked_prompts(user_id)
    assert result.is_anomaly, "Should detect anomaly after repeated blocks"
    print(f"  Blocked 4: Anomaly={result.is_anomaly} (expected True)")
    
    # Test risk score
    risk_score = detector.get_user_risk_score(user_id)
    print(f"\nRisk score: {risk_score}")
    
    # Test reset
    detector.reset_user(user_id)
    risk_score = detector.get_user_risk_score(user_id)
    assert risk_score == 0, "Risk score should be 0 after reset"
    print(f"After reset: {risk_score}")
    
    print("\n✅ Anomaly Detector test passed")
    return True


def test_combined_detection():
    """ทดสอบการตรวจจับแบบรวม"""
    print("\n=== Testing Combined Detection ===\n")
    
    detector = AnomalyDetector(
        max_requests_per_minute=5,
        max_failed_logins=3,
        max_blocked_prompts=2
    )
    
    user_id = "attacker"
    
    # Simulate attack pattern
    print("Simulating attack pattern...")
    
    # Multiple requests
    for i in range(6):
        result = detector.check_all(user_id)
        if result.is_anomaly:
            print(f"  Request {i+1}: ⚠️ Anomaly detected - {result.anomaly_type}")
            break
    
    # Failed logins
    detector.reset_user(user_id)
    for i in range(4):
        result = detector.check_all(user_id, {"failed_login": True})
        if result.is_anomaly:
            print(f"  Login {i+1}: ⚠️ Anomaly detected - {result.anomaly_type}")
            break
    
    # Blocked prompts
    detector.reset_user(user_id)
    for i in range(3):
        result = detector.check_all(user_id, {"blocked_prompt": True})
        if result.is_anomaly:
            print(f"  Blocked {i+1}: ⚠️ Anomaly detected - {result.anomaly_type}")
            break
    
    # Get high risk users
    high_risk = detector.get_high_risk_users(threshold=1.0)
    print(f"\nHigh risk users: {high_risk}")
    
    print("\n✅ Combined Detection test passed")
    return True


def test_statistics():
    """ทดสอบการเก็บสถิติ"""
    print("\n=== Testing Statistics ===\n")
    
    limiter = RateLimiter()
    detector = AnomalyDetector()
    brute_force = BruteForceDetector()
    
    # Generate some activity
    for i in range(10):
        limiter.check(f"user_{i % 3}")
        detector.check_request_rate(f"user_{i % 3}")
        brute_force.record_attempt(f"user_{i % 3}", "api", success=i % 2 == 0)
    
    # Get stats
    print("Rate Limiter Stats:")
    for key, value in limiter.get_stats().items():
        print(f"  {key}: {value}")
    
    print("\nAnomaly Detector Stats:")
    for key, value in detector.get_stats().items():
        print(f"  {key}: {value}")
    
    print("\nBrute Force Stats:")
    for key, value in brute_force.get_stats().items():
        print(f"  {key}: {value}")
    
    print("\n✅ Statistics test passed")
    return True


def run_all_tests():
    """รันทุกการทดสอบ"""
    print("\n" + "=" * 60)
    print("dLNk Anomaly Detection Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Rate Limiter", test_rate_limiter()))
    results.append(("Brute Force Detector", test_brute_force_detector()))
    results.append(("Anomaly Detector", test_anomaly_detector()))
    results.append(("Combined Detection", test_combined_detection()))
    results.append(("Statistics", test_statistics()))
    
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
