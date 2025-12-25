#!/usr/bin/env python3
"""
Webhook API for Telegram Bot
============================
Receives events from other dLNk components via HTTP webhook.

This module provides:
- Security event webhook endpoint
- AI Bridge event webhook endpoint
- License event webhook endpoint

Author: dLNk Team (AI-10 Integration)
Version: 1.0.0
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
import uvicorn

logger = logging.getLogger('WebhookAPI')

app = FastAPI(
    title="dLNk Telegram Bot Webhook API",
    description="Receives events from dLNk components",
    version="1.0.0"
)

# Global bot reference (set by main.py)
_bot_instance = None
_security_integration = None
_ai_bridge_integration = None


def set_bot_instance(bot):
    """Set bot instance for sending messages"""
    global _bot_instance
    _bot_instance = bot


def set_integrations(security=None, ai_bridge=None):
    """Set integration instances"""
    global _security_integration, _ai_bridge_integration
    _security_integration = security
    _ai_bridge_integration = ai_bridge


# Request Models

class SecurityEventRequest(BaseModel):
    """Security event webhook request"""
    event_type: str
    title: str
    message: str
    severity: int = 2
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AIBridgeEventRequest(BaseModel):
    """AI Bridge event webhook request"""
    event_type: str  # status_change, error, provider_switch, etc.
    title: str
    message: str
    severity: int = 1
    provider: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class LicenseEventRequest(BaseModel):
    """License event webhook request"""
    event_type: str  # created, activated, expired, revoked
    license_key: str
    user_id: str
    license_type: Optional[str] = None
    expires_at: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AlertRequest(BaseModel):
    """Generic alert request"""
    title: str
    message: str
    severity: int = 2


# Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "dLNk Telegram Bot Webhook API",
        "bot_connected": _bot_instance is not None
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "bot_connected": _bot_instance is not None,
        "security_integration": _security_integration is not None,
        "ai_bridge_integration": _ai_bridge_integration is not None
    }


@app.post("/webhook/security")
async def security_webhook(
    event: SecurityEventRequest,
    background_tasks: BackgroundTasks
):
    """
    Receive security events from Security Module.
    
    This endpoint is called by the Security Module when
    security events occur (e.g., prompt blocked, rate limit exceeded).
    """
    logger.info(f"Received security event: {event.event_type} - {event.title}")
    
    if _security_integration:
        # Forward to security integration
        background_tasks.add_task(
            _security_integration.receive_event,
            event_type=event.event_type,
            title=event.title,
            message=event.message,
            severity=event.severity,
            user_id=event.user_id,
            ip_address=event.ip_address,
            details=event.details
        )
        return {"status": "accepted", "event_type": event.event_type}
    
    elif _bot_instance:
        # Direct send to bot
        background_tasks.add_task(
            send_alert_to_bot,
            title=f"🛡️ Security: {event.title}",
            message=event.message,
            severity=event.severity
        )
        return {"status": "accepted", "event_type": event.event_type}
    
    else:
        raise HTTPException(status_code=503, detail="Bot not connected")


@app.post("/webhook/ai-bridge")
async def ai_bridge_webhook(
    event: AIBridgeEventRequest,
    background_tasks: BackgroundTasks
):
    """
    Receive events from AI Bridge.
    
    This endpoint is called by AI Bridge for status changes,
    errors, and other events.
    """
    logger.info(f"Received AI Bridge event: {event.event_type} - {event.title}")
    
    if _bot_instance:
        # Format message
        icon = {
            "status_change": "🔄",
            "error": "❌",
            "provider_switch": "🔀",
            "token_refresh": "🔑",
            "warning": "⚠️"
        }.get(event.event_type, "📡")
        
        message = f"{icon} <b>AI Bridge: {event.title}</b>\n\n{event.message}"
        
        if event.provider:
            message += f"\n\n<b>Provider:</b> {event.provider}"
        
        background_tasks.add_task(
            send_alert_to_bot,
            title=event.title,
            message=message,
            severity=event.severity
        )
        return {"status": "accepted", "event_type": event.event_type}
    
    else:
        raise HTTPException(status_code=503, detail="Bot not connected")


@app.post("/webhook/license")
async def license_webhook(
    event: LicenseEventRequest,
    background_tasks: BackgroundTasks
):
    """
    Receive license events from License Server.
    
    This endpoint is called by the License Server when
    license events occur (e.g., created, activated, expired).
    """
    logger.info(f"Received license event: {event.event_type} - {event.license_key}")
    
    if _bot_instance:
        # Format message
        icon = {
            "created": "🆕",
            "activated": "✅",
            "expired": "⏰",
            "revoked": "❌",
            "extended": "📅"
        }.get(event.event_type, "🔑")
        
        message = f"""
{icon} <b>License {event.event_type.title()}</b>

<b>Key:</b> <code>{event.license_key}</code>
<b>User:</b> {event.user_id}
"""
        
        if event.license_type:
            message += f"<b>Type:</b> {event.license_type}\n"
        
        if event.expires_at:
            message += f"<b>Expires:</b> {event.expires_at}\n"
        
        background_tasks.add_task(
            send_alert_to_bot,
            title=f"License {event.event_type}",
            message=message,
            severity=1
        )
        return {"status": "accepted", "event_type": event.event_type}
    
    else:
        raise HTTPException(status_code=503, detail="Bot not connected")


@app.post("/webhook/alert")
async def generic_alert(
    alert: AlertRequest,
    background_tasks: BackgroundTasks
):
    """
    Receive generic alerts from any component.
    """
    logger.info(f"Received alert: {alert.title}")
    
    if _bot_instance:
        background_tasks.add_task(
            send_alert_to_bot,
            title=alert.title,
            message=alert.message,
            severity=alert.severity
        )
        return {"status": "accepted"}
    
    else:
        raise HTTPException(status_code=503, detail="Bot not connected")


async def send_alert_to_bot(title: str, message: str, severity: int = 2):
    """Send alert to bot"""
    if _bot_instance:
        try:
            await _bot_instance.send_alert(
                message=message,
                severity=severity
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")


def run_webhook_server(host: str = "0.0.0.0", port: int = 8089):
    """Run the webhook server"""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_webhook_server()
