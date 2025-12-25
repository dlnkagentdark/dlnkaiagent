"""
dLNk AI Bridge Module
=====================
ระบบเชื่อมต่อ AI หลายตัวแบบรวมศูนย์

Modules:
- auto_failover: ระบบ Failover อัตโนมัติ
- health_check: ระบบตรวจสอบสุขภาพ
- unified_bridge: Bridge หลักสำหรับเรียก AI
- token_integration: เชื่อมต่อกับ Token Harvester
"""

from .auto_failover import (
    AutoFailover,
    FailoverConfig,
    ProviderStatus,
    ProviderHealth,
    get_failover
)

from .health_check import (
    health_bp,
    get_uptime,
    get_system_metrics
)

from .unified_bridge import (
    UnifiedAIBridge,
    AIMode,
    AIRequest,
    AIResponse,
    AI_MODE_PROMPTS,
    get_bridge
)

__all__ = [
    # Auto Failover
    'AutoFailover',
    'FailoverConfig',
    'ProviderStatus',
    'ProviderHealth',
    'get_failover',
    
    # Health Check
    'health_bp',
    'get_uptime',
    'get_system_metrics',
    
    # Unified Bridge
    'UnifiedAIBridge',
    'AIMode',
    'AIRequest',
    'AIResponse',
    'AI_MODE_PROMPTS',
    'get_bridge'
]

__version__ = '1.0.0'
__author__ = 'dLNk IDE Project'
