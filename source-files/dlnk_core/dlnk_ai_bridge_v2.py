#!/usr/bin/env python3
"""
dLNk AI Bridge Service v2
เชื่อมต่อ dLNk IDE กับ AI Service พร้อมระบบ Hash Token และ Input Validation
"""

import os
import sys
import json
import asyncio
import logging
import hashlib
import hmac
import secrets
import re
import html
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# WebSocket and HTTP
import websockets
from websockets.server import serve
import aiohttp
from aiohttp import web

# OpenAI
from openai import OpenAI

# Configuration
CONFIG_DIR = Path.home() / ".dlnk-ide"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-AI-Bridge-v2')

# ==================== SECURITY: HASH TOKEN SYSTEM ====================

class TokenManager:
    """
    ระบบจัดการ Token พร้อม Hash
    - สร้าง Token ที่ปลอดภัย
    - ตรวจสอบ Token ด้วย HMAC
    - จำกัดอายุการใช้งาน Token
    """
    
    def __init__(self, secret_key: str = None):
        # ใช้ Secret Key จาก Environment หรือสร้างใหม่
        self.secret_key = secret_key or os.environ.get('DLNK_SECRET_KEY') or secrets.token_hex(32)
        self.tokens: Dict[str, Dict] = {}  # token_hash -> {user_id, expires, created}
        self.token_lifetime = timedelta(hours=24)  # Token หมดอายุใน 24 ชั่วโมง
        
        # บันทึก Secret Key สำหรับใช้งานครั้งต่อไป
        secret_file = CONFIG_DIR / "bridge_secret.key"
        if not secret_file.exists():
            with open(secret_file, 'w') as f:
                f.write(self.secret_key)
            os.chmod(secret_file, 0o600)  # เฉพาะ owner อ่านได้
        
        logger.info("TokenManager initialized with HMAC-SHA256")
    
    def generate_token(self, user_id: str, license_key: str) -> str:
        """สร้าง Token ใหม่สำหรับผู้ใช้"""
        # สร้าง Token แบบสุ่ม
        raw_token = secrets.token_urlsafe(32)
        
        # สร้าง Hash ของ Token ด้วย HMAC-SHA256
        token_hash = self._hash_token(raw_token)
        
        # เก็บข้อมูล Token
        self.tokens[token_hash] = {
            'user_id': user_id,
            'license_key': license_key,
            'created': datetime.now(),
            'expires': datetime.now() + self.token_lifetime,
            'requests': 0
        }
        
        logger.info(f"Token generated for user: {user_id[:8]}...")
        return raw_token
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """ตรวจสอบ Token"""
        if not token:
            return False, None
        
        token_hash = self._hash_token(token)
        
        if token_hash not in self.tokens:
            logger.warning("Invalid token attempted")
            return False, None
        
        token_data = self.tokens[token_hash]
        
        # ตรวจสอบหมดอายุ
        if datetime.now() > token_data['expires']:
            del self.tokens[token_hash]
            logger.warning(f"Expired token for user: {token_data['user_id'][:8]}...")
            return False, None
        
        # อัปเดตจำนวน requests
        token_data['requests'] += 1
        
        return True, token_data
    
    def revoke_token(self, token: str) -> bool:
        """ยกเลิก Token"""
        token_hash = self._hash_token(token)
        if token_hash in self.tokens:
            del self.tokens[token_hash]
            return True
        return False
    
    def _hash_token(self, token: str) -> str:
        """Hash Token ด้วย HMAC-SHA256"""
        return hmac.new(
            self.secret_key.encode(),
            token.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def cleanup_expired(self):
        """ลบ Token ที่หมดอายุ"""
        now = datetime.now()
        expired = [h for h, d in self.tokens.items() if now > d['expires']]
        for h in expired:
            del self.tokens[h]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired tokens")


# ==================== SECURITY: INPUT VALIDATION ====================

class InputValidator:
    """
    ระบบตรวจสอบ Input
    - ป้องกัน SQL Injection
    - ป้องกัน XSS
    - ป้องกัน Command Injection
    - จำกัดความยาว Input
    """
    
    # Patterns ที่อาจเป็นอันตราย (สำหรับ Admin/Server side เท่านั้น)
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
        r'--',  # SQL comment
        r';.*?(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE)',  # SQL injection
        r'\|\|',  # Command chaining
        r'`.*`',  # Command substitution
        r'\$\(.*\)',  # Command substitution
    ]
    
    MAX_MESSAGE_LENGTH = 10000  # จำกัดความยาวข้อความ
    MAX_CONTEXT_LENGTH = 50000  # จำกัดความยาว context
    
    @classmethod
    def sanitize_for_admin(cls, text: str) -> str:
        """
        Sanitize input สำหรับ Admin interface
        - Escape HTML
        - ลบ patterns อันตราย
        """
        if not text:
            return ""
        
        # Escape HTML entities
        text = html.escape(text)
        
        # ลบ patterns อันตราย
        for pattern in cls.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    @classmethod
    def validate_message(cls, message: str) -> Tuple[bool, str]:
        """
        ตรวจสอบข้อความจากผู้ใช้
        - ไม่จำกัดเนื้อหา (ผู้ใช้ส่งอะไรก็ได้)
        - จำกัดแค่ความยาว
        """
        if not message:
            return False, "Message cannot be empty"
        
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            return False, f"Message too long (max {cls.MAX_MESSAGE_LENGTH} chars)"
        
        return True, "OK"
    
    @classmethod
    def validate_license_key(cls, key: str) -> Tuple[bool, str]:
        """ตรวจสอบรูปแบบ License Key"""
        if not key:
            return False, "License key required"
        
        # รูปแบบ: DLNK-XXXX-XXXX-XXXX-XXXX
        pattern = r'^DLNK-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$'
        if not re.match(pattern, key):
            return False, "Invalid license key format"
        
        return True, "OK"
    
    @classmethod
    def validate_admin_input(cls, field: str, value: str) -> Tuple[bool, str]:
        """
        ตรวจสอบ Input สำหรับ Admin (เข้มงวดกว่า)
        """
        if not value:
            return False, f"{field} cannot be empty"
        
        # ตรวจสอบ patterns อันตราย
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected in {field}")
                return False, f"Invalid characters in {field}"
        
        return True, "OK"


# ==================== AI BRIDGE SERVICE ====================

class DLNKAIBridge:
    """
    dLNk AI Bridge Service
    - เชื่อมต่อกับ OpenAI Compatible API
    - รองรับ WebSocket และ REST API
    - มีระบบ Token และ Input Validation
    """
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.client = OpenAI()  # ใช้ค่าจาก environment
        self.model = "gpt-4.1-nano"  # Default model
        
        # System prompt สำหรับ dLNk AI
        self.system_prompt = """You are dLNk AI, an intelligent assistant integrated into dLNk IDE.

Your capabilities:
- Answer general questions in any language
- Help with coding and technical problems
- Debug and fix code issues
- Explain technical concepts
- Assist with dLNk IDE usage

Always be helpful, accurate, and professional. If you don't know something, say so.
Respond in the same language as the user's message."""

        logger.info("dLNk AI Bridge initialized")
    
    async def chat(self, message: str, context: list = None, token: str = None) -> Dict[str, Any]:
        """
        ส่งข้อความไปยัง AI และรับคำตอบ
        """
        # ตรวจสอบ Token (ถ้ามี)
        if token:
            valid, token_data = self.token_manager.verify_token(token)
            if not valid:
                return {"error": "Invalid or expired token", "success": False}
        
        # ตรวจสอบ Input
        valid, msg = InputValidator.validate_message(message)
        if not valid:
            return {"error": msg, "success": False}
        
        # สร้าง messages array
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # เพิ่ม context (ประวัติการสนทนา)
        if context:
            for ctx in context[-10:]:  # จำกัดแค่ 10 ข้อความล่าสุด
                messages.append(ctx)
        
        # เพิ่มข้อความใหม่
        messages.append({"role": "user", "content": message})
        
        try:
            # เรียก AI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "success": True,
                "response": ai_response,
                "model": self.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"AI Error: {e}")
            return {"error": str(e), "success": False}
    
    async def handle_websocket(self, websocket):
        """จัดการ WebSocket connection"""
        client_ip = websocket.remote_address[0]
        logger.info(f"WebSocket connected: {client_ip}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    action = data.get('action', 'chat')
                    
                    if action == 'chat':
                        result = await self.chat(
                            message=data.get('message', ''),
                            context=data.get('context', []),
                            token=data.get('token')
                        )
                        await websocket.send(json.dumps(result))
                    
                    elif action == 'ping':
                        await websocket.send(json.dumps({"pong": True}))
                    
                    elif action == 'get_token':
                        # สร้าง Token ใหม่ (ต้องมี license_key)
                        license_key = data.get('license_key', '')
                        valid, msg = InputValidator.validate_license_key(license_key)
                        if valid:
                            token = self.token_manager.generate_token(
                                user_id=data.get('user_id', 'anonymous'),
                                license_key=license_key
                            )
                            await websocket.send(json.dumps({
                                "success": True,
                                "token": token
                            }))
                        else:
                            await websocket.send(json.dumps({
                                "success": False,
                                "error": msg
                            }))
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket disconnected: {client_ip}")
    
    async def start_websocket_server(self, host: str = "0.0.0.0", port: int = 8765):
        """เริ่ม WebSocket server"""
        logger.info(f"Starting WebSocket server on ws://{host}:{port}")
        async with serve(self.handle_websocket, host, port):
            await asyncio.Future()  # Run forever


# ==================== REST API ====================

def create_rest_app(bridge: DLNKAIBridge) -> web.Application:
    """สร้าง REST API application"""
    
    async def health_check(request):
        return web.json_response({"status": "ok", "service": "dLNk AI Bridge v2"})
    
    async def chat_endpoint(request):
        try:
            data = await request.json()
            
            # Sanitize สำหรับ logging (ไม่จำกัดผู้ใช้)
            message = data.get('message', '')
            
            result = await bridge.chat(
                message=message,
                context=data.get('context', []),
                token=data.get('token')
            )
            
            if result.get('success'):
                return web.json_response(result)
            else:
                return web.json_response(result, status=400)
                
        except json.JSONDecodeError:
            return web.json_response({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"REST API Error: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_token_endpoint(request):
        try:
            data = await request.json()
            license_key = data.get('license_key', '')
            
            valid, msg = InputValidator.validate_license_key(license_key)
            if not valid:
                return web.json_response({"error": msg}, status=400)
            
            token = bridge.token_manager.generate_token(
                user_id=data.get('user_id', 'anonymous'),
                license_key=license_key
            )
            
            # Hash token สำหรับ response
            token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
            
            return web.json_response({
                "success": True,
                "token": token,
                "token_hash": token_hash,
                "expires_in": "24 hours"
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def verify_token_endpoint(request):
        try:
            data = await request.json()
            token = data.get('token', '')
            
            valid, token_data = bridge.token_manager.verify_token(token)
            
            if valid:
                return web.json_response({
                    "valid": True,
                    "user_id": token_data['user_id'],
                    "requests": token_data['requests']
                })
            else:
                return web.json_response({"valid": False}, status=401)
                
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_post('/chat', chat_endpoint)
    app.router.add_post('/token', get_token_endpoint)
    app.router.add_post('/verify', verify_token_endpoint)
    
    return app


# ==================== MAIN ====================

async def main():
    print("""
============================================================
dLNk AI Bridge Service v2
============================================================
Features:
  - HMAC-SHA256 Token Authentication
  - Input Validation (Admin-side protection)
  - WebSocket + REST API
  - OpenAI Compatible
============================================================
    """)
    
    bridge = DLNKAIBridge()
    
    # Start REST API
    rest_app = create_rest_app(bridge)
    runner = web.AppRunner(rest_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8766)
    await site.start()
    logger.info("REST API started on http://0.0.0.0:8766")
    
    # Start WebSocket server
    await bridge.start_websocket_server()


if __name__ == "__main__":
    asyncio.run(main())
