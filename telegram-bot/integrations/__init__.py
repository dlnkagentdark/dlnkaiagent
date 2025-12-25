#!/usr/bin/env python3
"""
Integrations Module for dLNk Telegram Bot
==========================================
Contains integration modules for connecting with other dLNk components.
"""

from .security_integration import (
    SecurityIntegration,
    SecurityEvent,
    SecurityEventType,
    get_security_integration,
    forward_security_event
)

from .ai_bridge_integration import (
    AIBridgeIntegration,
    get_ai_bridge_integration
)

__all__ = [
    # Security Integration
    'SecurityIntegration',
    'SecurityEvent',
    'SecurityEventType',
    'get_security_integration',
    'forward_security_event',
    
    # AI Bridge Integration
    'AIBridgeIntegration',
    'get_ai_bridge_integration',
]
