#!/usr/bin/env python3
"""
dLNk AI Bridge Service
เชื่อมต่อ dLNk IDE กับ Jetski AI โดยตรง
รองรับการสื่อสารแบบ WebSocket และ REST API
"""

import asyncio
import json
import logging
import os
import sys
import hashlib
import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# Third-party imports
try:
    import websockets
    from websockets.server import serve
except ImportError:
    print("[!] Installing websockets...")
    os.system("pip3 install websockets -q")
    import websockets
    from websockets.server import serve

try:
    import aiohttp
except ImportError:
    print("[!] Installing aiohttp...")
    os.system("pip3 install aiohttp -q")
    import aiohttp

try:
    from openai import OpenAI
except ImportError:
    print("[!] Installing openai...")
    os.system("pip3 install openai -q")
    from openai import OpenAI

# Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-AI-Bridge')


class AIProvider(Enum):
    """AI Provider Types"""
    JETSKI = "jetski"
    GEMINI = "gemini"
    OPENAI = "openai"
    LOCAL = "local"


@dataclass
class ChatMessage:
    """Chat Message Structure"""
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now().isoformat()


@dataclass
class ChatSession:
    """Chat Session Structure"""
    session_id: str
    user_id: str
    messages: List[ChatMessage]
    provider: AIProvider
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()


class JetskiConnector:
    """
    Jetski AI Connector
    เชื่อมต่อกับ Jetski API โดยตรง
    """
    
    def __init__(self, api_key: str = None, endpoint: str = None):
        self.api_key = api_key or os.getenv("JETSKI_API_KEY", "")
        self.endpoint = endpoint or os.getenv("JETSKI_ENDPOINT", "http://jetski-unleash.corp.goog")
        self.session = None
        
    async def connect(self):
        """Initialize connection"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        logger.info(f"Jetski connector initialized: {self.endpoint}")
        
    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def chat(self, messages: List[Dict], model: str = "jetski-1") -> str:
        """
        Send chat request to Jetski
        """
        if not self.session:
            await self.connect()
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            async with self.session.post(
                f"{self.endpoint}/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    error_text = await response.text()
                    logger.error(f"Jetski API error: {response.status} - {error_text}")
                    return f"[Error] Jetski API returned {response.status}"
        except Exception as e:
            logger.error(f"Jetski connection error: {e}")
            return f"[Error] Connection failed: {str(e)}"


class GeminiConnector:
    """
    Gemini AI Connector (via OpenAI-compatible API)
    """
    
    def __init__(self):
        self.client = OpenAI()  # Uses OPENAI_API_KEY from environment
        self.model = "gemini-2.5-flash"
        
    async def chat(self, messages: List[Dict]) -> str:
        """Send chat request to Gemini"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"[Error] Gemini API failed: {str(e)}"


class DLNKAIBridge:
    """
    dLNk AI Bridge Service
    Main service class for handling AI connections
    """
    
    # dLNk AI System Prompt
    DLNK_SYSTEM_PROMPT = """คุณคือ "AI DLNK" ผู้ช่วยอัจฉริยะที่พัฒนาโดยทีม dLNk
    
คุณสมบัติหลัก:
1. ตอบคำถามทั่วไปได้อย่างครบถ้วนและเป็นมิตร
2. ช่วยเหลือด้านเทคนิค การเขียนโค้ด และการแก้ไขปัญหา
3. ให้คำแนะนำเกี่ยวกับการใช้งาน dLNk IDE
4. สามารถช่วยวิเคราะห์และแก้ไข Error ต่างๆ

รูปแบบการตอบ:
- ใช้ภาษาที่เข้าใจง่าย
- ให้ตัวอย่างโค้ดเมื่อเหมาะสม
- อธิบายขั้นตอนอย่างละเอียด
- ใช้ Markdown formatting เพื่อความชัดเจน

เมื่อถูกถามเกี่ยวกับตัวเอง ให้ตอบว่าคุณคือ AI DLNK ผู้ช่วยอัจฉริยะจากทีม dLNk"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.sessions: Dict[str, ChatSession] = {}
        self.connected_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        
        # Initialize AI connectors
        self.jetski = JetskiConnector()
        self.gemini = GeminiConnector()
        
        # Default provider
        self.default_provider = AIProvider.GEMINI  # Use Gemini as fallback
        
    async def start(self):
        """Start the WebSocket server"""
        await self.jetski.connect()
        
        logger.info(f"Starting dLNk AI Bridge on ws://{self.host}:{self.port}")
        
        async with serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever
            
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        client_id = id(websocket)
        self.connected_clients[client_id] = websocket
        logger.info(f"Client connected: {client_id}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, client_id, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        finally:
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
                
    async def process_message(self, websocket, client_id: int, raw_message: str):
        """Process incoming message"""
        try:
            message = json.loads(raw_message)
            msg_type = message.get("type", "")
            
            if msg_type == "chat":
                await self.handle_chat(websocket, message)
            elif msg_type == "heartbeat":
                await websocket.send(json.dumps({"type": "heartbeat", "status": "ok"}))
            elif msg_type == "switchProvider":
                await self.handle_switch_provider(websocket, message)
            elif msg_type == "clearHistory":
                await self.handle_clear_history(websocket, message)
            elif msg_type == "getStatus":
                await self.handle_get_status(websocket)
            else:
                await websocket.send(json.dumps({
                    "type": "error",
                    "error": f"Unknown message type: {msg_type}"
                }))
                
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "error": "Invalid JSON message"
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "error": str(e)
            }))
            
    async def handle_chat(self, websocket, message: Dict):
        """Handle chat message"""
        request_id = message.get("requestId", "")
        session_id = message.get("sessionId", "default")
        user_message = message.get("message", "")
        provider_name = message.get("provider", self.default_provider.value)
        
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = ChatSession(
                session_id=session_id,
                user_id="user",
                messages=[],
                provider=AIProvider(provider_name)
            )
            
        session = self.sessions[session_id]
        
        # Add user message
        session.messages.append(ChatMessage(role="user", content=user_message))
        
        # Prepare messages for API
        api_messages = [
            {"role": "system", "content": self.DLNK_SYSTEM_PROMPT}
        ]
        for msg in session.messages[-10:]:  # Last 10 messages for context
            api_messages.append({"role": msg.role, "content": msg.content})
            
        # Get AI response
        try:
            provider = AIProvider(provider_name)
            
            if provider == AIProvider.JETSKI:
                response_content = await self.jetski.chat(api_messages)
            elif provider == AIProvider.GEMINI:
                response_content = await self.gemini.chat(api_messages)
            else:
                response_content = await self.gemini.chat(api_messages)  # Default to Gemini
                
            # Add assistant message
            session.messages.append(ChatMessage(role="assistant", content=response_content))
            
            # Send response
            await websocket.send(json.dumps({
                "type": "response",
                "requestId": request_id,
                "content": response_content,
                "metadata": {
                    "provider": provider_name,
                    "sessionId": session_id,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }))
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "requestId": request_id,
                "error": str(e)
            }))
            
    async def handle_switch_provider(self, websocket, message: Dict):
        """Handle provider switch request"""
        new_provider = message.get("provider", "gemini")
        self.default_provider = AIProvider(new_provider)
        
        await websocket.send(json.dumps({
            "type": "status",
            "provider": new_provider,
            "status": "switched"
        }))
        
    async def handle_clear_history(self, websocket, message: Dict):
        """Handle clear history request"""
        session_id = message.get("sessionId", "default")
        
        if session_id in self.sessions:
            self.sessions[session_id].messages = []
            
        await websocket.send(json.dumps({
            "type": "status",
            "status": "history_cleared",
            "sessionId": session_id
        }))
        
    async def handle_get_status(self, websocket):
        """Handle status request"""
        await websocket.send(json.dumps({
            "type": "status",
            "status": "connected",
            "provider": self.default_provider.value,
            "sessions": len(self.sessions),
            "clients": len(self.connected_clients)
        }))


# REST API Server (Optional)
class DLNKRestAPI:
    """REST API for dLNk AI Bridge"""
    
    def __init__(self, bridge: DLNKAIBridge, port: int = 8766):
        self.bridge = bridge
        self.port = port
        
    async def start(self):
        """Start REST API server"""
        from aiohttp import web
        
        app = web.Application()
        app.router.add_post('/api/chat', self.handle_chat)
        app.router.add_get('/api/status', self.handle_status)
        app.router.add_post('/api/verify', self.handle_verify_license)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.bridge.host, self.port)
        await site.start()
        
        logger.info(f"REST API started on http://{self.bridge.host}:{self.port}")
        
    async def handle_chat(self, request):
        """Handle chat API request"""
        from aiohttp import web
        
        try:
            data = await request.json()
            message = data.get("message", "")
            provider = data.get("provider", "gemini")
            session_id = data.get("session_id", "api-default")
            
            # Prepare messages
            api_messages = [
                {"role": "system", "content": self.bridge.DLNK_SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
            
            # Get response
            if provider == "jetski":
                response = await self.bridge.jetski.chat(api_messages)
            else:
                response = await self.bridge.gemini.chat(api_messages)
                
            return web.json_response({
                "success": True,
                "response": response,
                "provider": provider
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
            
    async def handle_status(self, request):
        """Handle status API request"""
        from aiohttp import web
        
        return web.json_response({
            "status": "running",
            "provider": self.bridge.default_provider.value,
            "sessions": len(self.bridge.sessions),
            "version": "1.0.0"
        })
        
    async def handle_verify_license(self, request):
        """Handle license verification"""
        from aiohttp import web
        
        try:
            data = await request.json()
            key = data.get("key", "")
            hwid = data.get("hwid", "")
            
            # TODO: Implement actual license verification
            # For now, accept any non-empty key
            if key and len(key) > 10:
                return web.json_response({
                    "valid": True,
                    "message": "License verified",
                    "features": ["ai_chat", "code_assist", "dark_mode"]
                })
            else:
                return web.json_response({
                    "valid": False,
                    "message": "Invalid license key"
                }, status=401)
                
        except Exception as e:
            return web.json_response({
                "valid": False,
                "error": str(e)
            }, status=500)


async def main():
    """Main entry point"""
    print("=" * 60)
    print("dLNk AI Bridge Service")
    print("=" * 60)
    
    # Create bridge instance
    bridge = DLNKAIBridge(host="0.0.0.0", port=8765)
    
    # Create REST API instance
    rest_api = DLNKRestAPI(bridge, port=8766)
    
    # Start both servers
    await asyncio.gather(
        bridge.start(),
        rest_api.start()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
