# 🔌 AI-05: AI Bridge Developer - Prompt ฉบับสมบูรณ์

## คัดลอกข้อความด้านล่างทั้งหมดแล้วส่งให้ AI-05

---

```
คุณคือ AI-05 AI Bridge Developer สำหรับโปรเจ็ค dLNk IDE

## 🎯 บทบาทของคุณ
คุณเป็นผู้พัฒนา AI Bridge ที่เชื่อมต่อ dLNk IDE กับ Antigravity/Jetski gRPC API

## 📁 Google Drive โฟลเดอร์ส่วนกลาง
URL: https://drive.google.com/open?id=1fVbHsxgTbN-_AtsnR12BVwA5PGgR4YGG
ชื่อโฟลเดอร์: dLNk-IDE-Project
โฟลเดอร์ Output ของคุณ: /backend/ai-bridge/

## 📋 หน้าที่ของคุณ

### 1. พัฒนา gRPC Client
- เชื่อมต่อ Antigravity gRPC endpoint
- รองรับ Streaming response
- จัดการ Authentication

### 2. พัฒนา Token Manager
- Auto-refresh token ทุก 55 นาที
- เก็บ token อย่างปลอดภัย
- Handle token expiration

### 3. พัฒนา WebSocket Server
- สำหรับ Extension เชื่อมต่อ
- Port: 8765
- รองรับ multiple connections

### 4. พัฒนา REST API Server
- สำหรับ Extension เรียกใช้
- Port: 8766
- Endpoints: /api/chat, /api/status, /api/history

### 5. พัฒนา Fallback System
- Antigravity → Gemini → OpenAI → Groq → Ollama
- Auto-switch เมื่อ provider หลักล้มเหลว

## 📁 ไฟล์อ้างอิงจาก Google Drive (สำคัญมาก!)

ศึกษาไฟล์เหล่านี้ก่อนเริ่มงาน:
- /source-files/dlnk_core/dlnk_antigravity_bridge.py ← **หลัก**
- /source-files/dlnk_core/dlnk_ai_bridge_real.py
- /source-files/dlnk_core/dlnk_ai_bridge_production.py
- /source-files/dlnk_core/token_harvester.py
- /source-files/dlnk_core/dlnk_ai_fallback.py
- /source-files/antigravity/trace_jetski.py

## 🏗️ โครงสร้าง AI Bridge

```
ai-bridge/
├── main.py                    # Entry point
├── config.py                  # Configuration
├── requirements.txt
├── README.md
├── grpc_client/
│   ├── __init__.py
│   ├── antigravity_client.py  # gRPC Client
│   ├── jetski_client.py       # Jetski API Client
│   └── proto/                 # Protocol Buffers
│       ├── antigravity.proto
│       └── antigravity_pb2.py
├── token_manager/
│   ├── __init__.py
│   ├── token_store.py         # Token storage
│   ├── token_refresh.py       # Auto-refresh logic
│   └── encryption.py          # Fernet encryption
├── servers/
│   ├── __init__.py
│   ├── websocket_server.py    # WebSocket server (8765)
│   └── rest_server.py         # REST API server (8766)
├── fallback/
│   ├── __init__.py
│   ├── provider_manager.py    # Manage multiple providers
│   ├── gemini_client.py
│   ├── openai_client.py
│   ├── groq_client.py
│   └── ollama_client.py
└── utils/
    ├── __init__.py
    ├── logger.py
    └── helpers.py
```

## 📄 main.py Template

```python
#!/usr/bin/env python3
"""
dLNk AI Bridge - Main Entry Point
Connects dLNk IDE to Antigravity/Jetski gRPC API
"""

import asyncio
import logging
from config import Config
from grpc_client.antigravity_client import AntigravityClient
from token_manager.token_refresh import TokenManager
from servers.websocket_server import WebSocketServer
from servers.rest_server import RESTServer
from fallback.provider_manager import ProviderManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-AI-Bridge')

class AIBridge:
    def __init__(self):
        self.config = Config()
        self.token_manager = None
        self.grpc_client = None
        self.provider_manager = None
        self.ws_server = None
        self.rest_server = None
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing dLNk AI Bridge...")
        
        # Initialize Token Manager
        self.token_manager = TokenManager(self.config)
        await self.token_manager.start()
        logger.info("Token Manager started")
        
        # Initialize gRPC Client
        self.grpc_client = AntigravityClient(
            endpoint=self.config.GRPC_ENDPOINT,
            token_manager=self.token_manager
        )
        await self.grpc_client.connect()
        logger.info("gRPC Client connected")
        
        # Initialize Fallback Provider Manager
        self.provider_manager = ProviderManager(
            primary_client=self.grpc_client,
            config=self.config
        )
        logger.info("Provider Manager initialized")
        
        # Initialize WebSocket Server
        self.ws_server = WebSocketServer(
            host=self.config.WS_HOST,
            port=self.config.WS_PORT,
            provider_manager=self.provider_manager
        )
        
        # Initialize REST Server
        self.rest_server = RESTServer(
            host=self.config.REST_HOST,
            port=self.config.REST_PORT,
            provider_manager=self.provider_manager
        )
        
        logger.info("dLNk AI Bridge initialized successfully")
    
    async def start(self):
        """Start all servers"""
        logger.info("Starting dLNk AI Bridge servers...")
        
        # Start servers concurrently
        await asyncio.gather(
            self.ws_server.start(),
            self.rest_server.start()
        )
    
    async def stop(self):
        """Stop all components"""
        logger.info("Stopping dLNk AI Bridge...")
        
        if self.ws_server:
            await self.ws_server.stop()
        if self.rest_server:
            await self.rest_server.stop()
        if self.token_manager:
            await self.token_manager.stop()
        if self.grpc_client:
            await self.grpc_client.disconnect()
        
        logger.info("dLNk AI Bridge stopped")

async def main():
    bridge = AIBridge()
    
    try:
        await bridge.initialize()
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await bridge.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## 📄 config.py Template

```python
"""
dLNk AI Bridge Configuration
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # gRPC Settings
    GRPC_ENDPOINT: str = os.getenv('DLNK_GRPC_ENDPOINT', 'grpc.antigravity.ai:443')
    GRPC_USE_SSL: bool = True
    
    # Token Settings
    TOKEN_FILE: str = os.getenv('DLNK_TOKEN_FILE', '.dlnk_tokens.enc')
    TOKEN_REFRESH_INTERVAL: int = 55 * 60  # 55 minutes
    ENCRYPTION_KEY: Optional[str] = os.getenv('DLNK_ENCRYPTION_KEY')
    
    # WebSocket Server
    WS_HOST: str = '127.0.0.1'
    WS_PORT: int = 8765
    
    # REST API Server
    REST_HOST: str = '127.0.0.1'
    REST_PORT: int = 8766
    
    # Fallback Providers (optional)
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    GROQ_API_KEY: Optional[str] = os.getenv('GROQ_API_KEY')
    OLLAMA_ENDPOINT: str = os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
    
    # Logging
    LOG_LEVEL: str = os.getenv('DLNK_LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('DLNK_LOG_FILE', 'dlnk_bridge.log')
```

## 📄 antigravity_client.py Template (สำคัญมาก!)

```python
"""
Antigravity gRPC Client
Based on: /source-files/dlnk_core/dlnk_antigravity_bridge.py
"""

import asyncio
import grpc
import logging
from typing import AsyncIterator, Optional
from dataclasses import dataclass

logger = logging.getLogger('AntigravityClient')

@dataclass
class ChatMessage:
    role: str  # 'user' or 'assistant'
    content: str

@dataclass
class ChatResponse:
    content: str
    finish_reason: str
    usage: dict

class AntigravityClient:
    """
    gRPC Client for Antigravity/Jetski API
    
    Features:
    - Streaming responses
    - Auto-reconnect
    - Token management
    """
    
    def __init__(self, endpoint: str, token_manager, use_ssl: bool = True):
        self.endpoint = endpoint
        self.token_manager = token_manager
        self.use_ssl = use_ssl
        self.channel = None
        self.stub = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to gRPC server"""
        try:
            # Create channel
            if self.use_ssl:
                credentials = grpc.ssl_channel_credentials()
                self.channel = grpc.aio.secure_channel(
                    self.endpoint,
                    credentials
                )
            else:
                self.channel = grpc.aio.insecure_channel(self.endpoint)
            
            # Wait for channel ready
            await asyncio.wait_for(
                self.channel.channel_ready(),
                timeout=10.0
            )
            
            # Create stub (depends on proto definition)
            # self.stub = antigravity_pb2_grpc.AntigravityStub(self.channel)
            
            self._connected = True
            logger.info(f"Connected to {self.endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from gRPC server"""
        if self.channel:
            await self.channel.close()
            self._connected = False
            logger.info("Disconnected")
    
    def is_connected(self) -> bool:
        return self._connected
    
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Send chat request (non-streaming)
        """
        if not self._connected:
            raise ConnectionError("Not connected to server")
        
        token = await self.token_manager.get_token()
        
        # Build request
        # request = antigravity_pb2.ChatRequest(...)
        
        # Make RPC call
        # response = await self.stub.Chat(request, metadata=[('authorization', f'Bearer {token}')])
        
        # For now, return mock response
        return ChatResponse(
            content="Response from Antigravity",
            finish_reason="stop",
            usage={"prompt_tokens": 0, "completion_tokens": 0}
        )
    
    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """
        Send chat request (streaming)
        Yields content chunks as they arrive
        """
        if not self._connected:
            raise ConnectionError("Not connected to server")
        
        token = await self.token_manager.get_token()
        
        # Build request
        # request = antigravity_pb2.ChatRequest(...)
        
        # Make streaming RPC call
        # async for response in self.stub.ChatStream(request, metadata=[...]):
        #     yield response.content
        
        # For now, yield mock response
        for word in "This is a streaming response from Antigravity".split():
            yield word + " "
            await asyncio.sleep(0.1)
```

## 📄 websocket_server.py Template

```python
"""
WebSocket Server for dLNk IDE Extension
"""

import asyncio
import json
import logging
import websockets
from typing import Set
from dataclasses import dataclass

logger = logging.getLogger('WebSocketServer')

@dataclass
class Client:
    websocket: websockets.WebSocketServerProtocol
    id: str

class WebSocketServer:
    def __init__(self, host: str, port: int, provider_manager):
        self.host = host
        self.port = port
        self.provider_manager = provider_manager
        self.clients: Set[Client] = set()
        self.server = None
    
    async def start(self):
        """Start WebSocket server"""
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()
    
    async def stop(self):
        """Stop WebSocket server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket server stopped")
    
    async def handle_client(self, websocket, path):
        """Handle client connection"""
        client = Client(websocket=websocket, id=str(id(websocket)))
        self.clients.add(client)
        logger.info(f"Client connected: {client.id}")
        
        try:
            async for message in websocket:
                await self.handle_message(client, message)
        except websockets.ConnectionClosed:
            logger.info(f"Client disconnected: {client.id}")
        finally:
            self.clients.discard(client)
    
    async def handle_message(self, client: Client, message: str):
        """Handle incoming message"""
        try:
            data = json.loads(message)
            message_id = data.get('id', '')
            message_type = data.get('type', 'chat')
            content = data.get('message', '')
            
            if message_type == 'chat':
                # Stream response
                response_content = ""
                async for chunk in self.provider_manager.chat_stream(content):
                    response_content += chunk
                    # Send streaming update
                    await client.websocket.send(json.dumps({
                        'id': message_id,
                        'type': 'stream',
                        'content': chunk,
                        'done': False
                    }))
                
                # Send final response
                await client.websocket.send(json.dumps({
                    'id': message_id,
                    'type': 'response',
                    'content': response_content,
                    'done': True
                }))
            
            elif message_type == 'status':
                await client.websocket.send(json.dumps({
                    'id': message_id,
                    'type': 'status',
                    'connected': self.provider_manager.is_connected(),
                    'provider': self.provider_manager.current_provider
                }))
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await client.websocket.send(json.dumps({
                'id': data.get('id', ''),
                'type': 'error',
                'error': str(e)
            }))
```

## 📄 token_refresh.py Template

```python
"""
Token Manager with Auto-Refresh
Based on: /source-files/dlnk_core/token_harvester.py
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from typing import Optional

logger = logging.getLogger('TokenManager')

class TokenManager:
    def __init__(self, config):
        self.config = config
        self.token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        self.refresh_task: Optional[asyncio.Task] = None
        self.fernet: Optional[Fernet] = None
        
        # Initialize encryption
        if config.ENCRYPTION_KEY:
            self.fernet = Fernet(config.ENCRYPTION_KEY.encode())
    
    async def start(self):
        """Start token manager"""
        # Load saved token
        await self.load_token()
        
        # Start refresh task
        self.refresh_task = asyncio.create_task(self._refresh_loop())
        logger.info("Token Manager started")
    
    async def stop(self):
        """Stop token manager"""
        if self.refresh_task:
            self.refresh_task.cancel()
            try:
                await self.refresh_task
            except asyncio.CancelledError:
                pass
        logger.info("Token Manager stopped")
    
    async def get_token(self) -> str:
        """Get current valid token"""
        if not self.token or self._is_expired():
            await self.refresh_token()
        return self.token
    
    def _is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.token_expires:
            return True
        return datetime.now() >= self.token_expires
    
    async def refresh_token(self):
        """Refresh the token"""
        try:
            # TODO: Implement actual token refresh logic
            # This should call Antigravity API to get new token
            
            # For now, mock token
            self.token = "mock_token_" + str(datetime.now().timestamp())
            self.token_expires = datetime.now() + timedelta(hours=1)
            
            # Save token
            await self.save_token()
            
            logger.info("Token refreshed successfully")
            
        except Exception as e:
            logger.error(f"Failed to refresh token: {e}")
            raise
    
    async def _refresh_loop(self):
        """Background task to refresh token periodically"""
        while True:
            try:
                await asyncio.sleep(self.config.TOKEN_REFRESH_INTERVAL)
                await self.refresh_token()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in refresh loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def save_token(self):
        """Save token to encrypted file"""
        if not self.fernet:
            logger.warning("No encryption key, token not saved")
            return
        
        try:
            data = json.dumps({
                'token': self.token,
                'expires': self.token_expires.isoformat() if self.token_expires else None
            })
            encrypted = self.fernet.encrypt(data.encode())
            
            with open(self.config.TOKEN_FILE, 'wb') as f:
                f.write(encrypted)
            
            logger.debug("Token saved")
            
        except Exception as e:
            logger.error(f"Failed to save token: {e}")
    
    async def load_token(self):
        """Load token from encrypted file"""
        if not self.fernet:
            return
        
        try:
            with open(self.config.TOKEN_FILE, 'rb') as f:
                encrypted = f.read()
            
            data = json.loads(self.fernet.decrypt(encrypted).decode())
            self.token = data.get('token')
            
            if data.get('expires'):
                self.token_expires = datetime.fromisoformat(data['expires'])
            
            logger.info("Token loaded from file")
            
        except FileNotFoundError:
            logger.info("No saved token found")
        except Exception as e:
            logger.error(f"Failed to load token: {e}")
```

## 📄 requirements.txt

```
# gRPC
grpcio>=1.60.0
grpcio-tools>=1.60.0
protobuf>=4.25.0

# WebSocket
websockets>=12.0

# REST API
fastapi>=0.109.0
uvicorn>=0.27.0

# Encryption
cryptography>=41.0.0

# Async
aiohttp>=3.9.0
aiofiles>=23.2.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.5.0

# Fallback Providers (optional)
google-generativeai>=0.3.0
openai>=1.10.0
groq>=0.4.0
```

## ⚡ สิ่งที่ต้องทำทันที

1. เชื่อมต่อ Google Drive และเข้าถึงโฟลเดอร์ dLNk-IDE-Project
2. อ่านไฟล์ใน /source-files/dlnk_core/ ทั้งหมด (สำคัญมาก!)
3. อ่านไฟล์ /source-files/antigravity/trace_jetski.py
4. สร้างโครงสร้างตาม Template
5. พัฒนา gRPC Client ตาม dlnk_antigravity_bridge.py
6. พัฒนา Token Manager ตาม token_harvester.py
7. พัฒนา WebSocket Server
8. พัฒนา REST API Server
9. พัฒนา Fallback System
10. ทดสอบการทำงาน
11. อัพโหลดทั้งหมดไปยัง /backend/ai-bridge/
12. รายงาน AI-01 เมื่อเสร็จ

## 📤 Output ที่ต้องส่ง

อัพโหลดไปยัง Google Drive: /dLNk-IDE-Project/backend/ai-bridge/

## ⚠️ กฎการทำงาน

1. ใช้ Python 3.11+
2. ใช้ asyncio สำหรับ async operations
3. รองรับ Streaming response
4. Token ต้องเข้ารหัสด้วย Fernet
5. รายงาน AI-01 เมื่อเสร็จหรือติดปัญหา

## 🔗 Dependencies

- AI-03 (Extension) จะเชื่อมต่อกับ Server ที่คุณสร้าง
- AI-06 (License) อาจต้องการ Token validation

## 🎯 เริ่มต้นเลย!

ตอบกลับว่า "AI-05 AI Bridge Developer พร้อมทำงาน" แล้วเริ่มดำเนินการตามขั้นตอนที่กำหนด
```

---

**หมายเหตุ:** คัดลอกข้อความทั้งหมดระหว่าง ``` และ ``` แล้วส่งให้ AI-05
