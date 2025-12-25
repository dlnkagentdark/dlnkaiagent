#!/usr/bin/env python3
"""
dLNk AI Bridge - Health Check System
=====================================
ระบบตรวจสอบสุขภาพของ AI Providers และ Services

Features:
- Basic health check endpoint
- Detailed provider health status
- System metrics
- Uptime tracking

Author: dLNk IDE Project (AI-01 The Architect)
Date: December 25, 2025
"""

import time
import psutil
import platform
from datetime import datetime
from typing import Dict, Any, Optional, List
from flask import Blueprint, jsonify, request
import logging

from .auto_failover import get_failover, ProviderStatus

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
health_bp = Blueprint('health', __name__)

# Track start time for uptime
_start_time = datetime.now()


def get_uptime() -> Dict[str, Any]:
    """คำนวณ uptime ของระบบ"""
    uptime = datetime.now() - _start_time
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return {
        "started_at": _start_time.isoformat(),
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_formatted": f"{days}d {hours}h {minutes}m {seconds}s"
    }


def get_system_metrics() -> Dict[str, Any]:
    """ดึง metrics ของระบบ"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": round(disk.percent, 1)
            },
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "python_version": platform.python_version()
            }
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {"error": str(e)}


@health_bp.route('/health', methods=['GET'])
def basic_health():
    """
    Basic health check endpoint
    
    Returns:
        200 OK if service is running
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "dLNk AI Bridge"
    }), 200


@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """
    Detailed health check with provider status
    
    Returns:
        Comprehensive health information
    """
    failover = get_failover()
    
    # Get provider health
    provider_health = failover.check_health()
    
    # Count healthy/unhealthy providers
    healthy_count = sum(
        1 for h in provider_health.values() 
        if h.get('status') == ProviderStatus.HEALTHY.value
    )
    total_providers = len(provider_health)
    
    # Determine overall status
    if healthy_count == 0 and total_providers > 0:
        overall_status = "critical"
    elif healthy_count < total_providers:
        overall_status = "degraded"
    else:
        overall_status = "healthy"
    
    # Get failover stats
    failover_stats = failover.get_stats()
    
    return jsonify({
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "service": "dLNk AI Bridge",
        "uptime": get_uptime(),
        "providers": {
            "total": total_providers,
            "healthy": healthy_count,
            "available": failover_stats.get("available_providers", 0),
            "details": provider_health
        },
        "statistics": {
            "total_requests": failover_stats.get("total_requests", 0),
            "total_successes": failover_stats.get("total_successes", 0),
            "overall_success_rate": failover_stats.get("overall_success_rate", "0%")
        },
        "system": get_system_metrics()
    }), 200


@health_bp.route('/health/providers', methods=['GET'])
def provider_health():
    """
    Get health status of all providers
    
    Query params:
        - name: Filter by provider name (optional)
    """
    failover = get_failover()
    provider_name = request.args.get('name')
    
    if provider_name:
        health = failover.check_health(provider_name)
        if not health:
            return jsonify({
                "error": f"Provider '{provider_name}' not found"
            }), 404
    else:
        health = failover.check_health()
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "providers": health
    }), 200


@health_bp.route('/health/providers/<name>/enable', methods=['POST'])
def enable_provider(name: str):
    """Enable a specific provider"""
    failover = get_failover()
    
    if failover.enable_provider(name):
        return jsonify({
            "status": "success",
            "message": f"Provider '{name}' enabled",
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"Provider '{name}' not found"
        }), 404


@health_bp.route('/health/providers/<name>/disable', methods=['POST'])
def disable_provider(name: str):
    """Disable a specific provider"""
    failover = get_failover()
    
    if failover.disable_provider(name):
        return jsonify({
            "status": "success",
            "message": f"Provider '{name}' disabled",
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"Provider '{name}' not found"
        }), 404


@health_bp.route('/health/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    failover = get_failover()
    stats = failover.get_stats()
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "statistics": stats
    }), 200


@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    Kubernetes-style readiness probe
    
    Returns 200 if at least one provider is available
    """
    failover = get_failover()
    available = failover.get_available_providers()
    
    if available:
        return jsonify({
            "ready": True,
            "available_providers": len(available),
            "timestamp": datetime.now().isoformat()
        }), 200
    else:
        return jsonify({
            "ready": False,
            "available_providers": 0,
            "message": "No providers available",
            "timestamp": datetime.now().isoformat()
        }), 503


@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    Kubernetes-style liveness probe
    
    Returns 200 if service is alive
    """
    return jsonify({
        "alive": True,
        "timestamp": datetime.now().isoformat()
    }), 200


# ==================== Health Check Functions ====================

def create_provider_health_check(provider_type: str):
    """
    สร้าง health check function สำหรับ provider แต่ละประเภท
    
    Args:
        provider_type: ประเภทของ provider (jetski, groq, ollama, etc.)
        
    Returns:
        Health check function
    """
    def jetski_health_check(client) -> bool:
        """Health check สำหรับ Jetski MITM"""
        try:
            # ลองเรียก endpoint ง่ายๆ
            response = client.get("/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _removed_openai_health_check(client) -> bool:
        """REMOVED - No paid APIs"""
        try:
            # ลองเรียก models endpoint
            models = client.models.list()
            return len(list(models)) > 0
        except:
            return False
    
    def groq_health_check(client) -> bool:
        """Health check สำหรับ Groq"""
        try:
            models = client.models.list()
            return len(list(models)) > 0
        except:
            return False
    
    def generic_health_check(client) -> bool:
        """Generic health check"""
        try:
            # ลอง ping หรือเรียก method ง่ายๆ
            if hasattr(client, 'ping'):
                return client.ping()
            if hasattr(client, 'health'):
                return client.health()
            return True
        except:
            return False
    
    health_checks = {
        "jetski": jetski_health_check,
        "ollama": generic_health_check,
        "groq": groq_health_check,
        "together": generic_health_check,
        "anthropic": generic_health_check,
        "mistral": generic_health_check
    }
    
    return health_checks.get(provider_type.lower(), generic_health_check)


# ==================== Test ====================

if __name__ == "__main__":
    from flask import Flask
    
    app = Flask(__name__)
    app.register_blueprint(health_bp)
    
    print("=" * 60)
    print("🧪 Testing Health Check System")
    print("=" * 60)
    
    # Test with Flask test client
    with app.test_client() as client:
        # Test basic health
        print("\n📤 Test 1: Basic health check")
        response = client.get('/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test liveness
        print("\n📤 Test 2: Liveness check")
        response = client.get('/health/live')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test readiness
        print("\n📤 Test 3: Readiness check")
        response = client.get('/health/ready')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # Test detailed health
        print("\n📤 Test 4: Detailed health check")
        response = client.get('/health/detailed')
        print(f"Status: {response.status_code}")
        data = response.get_json()
        print(f"Overall status: {data.get('status')}")
        print(f"Uptime: {data.get('uptime', {}).get('uptime_formatted')}")
    
    print("\n✅ Health Check test completed!")
