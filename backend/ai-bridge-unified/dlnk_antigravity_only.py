#!/usr/bin/env python3
"""
dLNk AI Bridge - Antigravity Only Edition
==========================================
Unified AI Bridge for dLNk IDE using Antigravity as the sole AI provider.

Features:
- Antigravity gRPC Client with HTTP/2
- Token Management with auto-refresh
- WebSocket Server for real-time communication (port 8765)
- REST API Server (port 8766)
- Secure token storage with encryption

Author: dLNk Team (AI-05)
Version: 2.0.0 - Antigravity Only
"""

import asyncio
import json
import logging
import os
import struct
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable, AsyncIterator, Set
from contextlib import asynccontextmanager

# ============================================
# Logging Configuration
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('dLNk-Bridge')


# ============================================
# Configuration
# ============================================
@dataclass
class Config:
    """Application configuration"""
    # Server ports
    WS_HOST: str = os.getenv('DLNK_WS_HOST', '127.0.0.1')
    WS_PORT: int = int(os.getenv('DLNK_WS_PORT', '8765'))
    REST_HOST: str = os.getenv('DLNK_REST_HOST', '127.0.0.1')
    REST_PORT: int = int(os.getenv('DLNK_REST_PORT', '8766'))
    
    # Antigravity endpoint
    ANTIGRAVITY_ENDPOINT: str = "https://antigravity-worker.google.com/exa.language_server_pb.LanguageServerService/SendUserCascadeMessage"
    
    # Token settings
    TOKEN_DIR: Path = Path.home() / '.dlnk' / 'tokens'
    TOKEN_REFRESH_INTERVAL: int = 55 * 60  # 55 minutes
    
    # Request settings
    REQUEST_TIMEOUT: float = 60.0
    MAX_RETRIES: int = 3


config = Config()


# ============================================
# Protobuf Encoder/Decoder
# ============================================
class ProtoEncoder:
    """
    Lightweight encoder for Antigravity Protobuf messages
    Based on: /backend/ai-bridge/grpc_client/proto_encoder.py
    """
    
    @staticmethod
    def _encode_varint(value: int) -> bytearray:
        """Encode integer as varint"""
        bytes_out = bytearray()
        while value > 0x7F:
            bytes_out.append((value & 0x7F) | 0x80)
            value >>= 7
        bytes_out.append(value)
        return bytes_out
    
    @staticmethod
    def _encode_field(field_no: int, wire_type: int, data: bytes) -> bytes:
        """Encode a protobuf field"""
        tag = (field_no << 3) | wire_type
        return bytes(ProtoEncoder._encode_varint(tag)) + data
    
    @staticmethod
    def encode_string(field_no: int, value: str) -> bytes:
        """Encode string field (wire type 2)"""
        data = value.encode('utf-8')
        length = ProtoEncoder._encode_varint(len(data))
        return ProtoEncoder._encode_field(field_no, 2, bytes(length) + data)
    
    @staticmethod
    def encode_message(field_no: int, data: bytes) -> bytes:
        """Encode nested message field (wire type 2)"""
        length = ProtoEncoder._encode_varint(len(data))
        return ProtoEncoder._encode_field(field_no, 2, bytes(length) + data)
    
    @staticmethod
    def encode_bool(field_no: int, value: bool) -> bytes:
        """Encode boolean field (wire type 0)"""
        data = bytearray([1 if value else 0])
        return ProtoEncoder._encode_field(field_no, 0, bytes(data))
    
    @staticmethod
    def build_cascade_request(
        cascade_id: str,
        prompt: str,
        access_token: str,
        session_id: Optional[str] = None
    ) -> bytes:
        """
        Build SendUserCascadeMessageRequest binary payload
        
        Field Mapping (based on reverse engineering):
        1: cascade_id (string)
        2: items (TextOrScopeItem - Repeated)
        3: metadata (Metadata)
        4: experiment_config (ExperimentConfig)
        7: cascade_config (CascadeConfig)
        8: blocking (bool)
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 1. Encode Items (Field 2) - Text Message
        text_chunk = ProtoEncoder.encode_string(9, prompt)
        scope_item = ProtoEncoder.encode_message(1, text_chunk)
        items_payload = ProtoEncoder.encode_message(2, scope_item)
        
        # 2. Encode Metadata (Field 3)
        meta_token = ProtoEncoder.encode_string(1, access_token)
        meta_session = ProtoEncoder.encode_string(4, session_id)
        meta_payload = ProtoEncoder.encode_message(3, meta_token + meta_session)
        
        # 3. Encode ExperimentConfig (Field 4) - Empty
        exp_payload = ProtoEncoder.encode_message(4, b"")
        
        # 4. Encode CascadeConfig (Field 7)
        model_alias = ProtoEncoder.encode_message(1, b"")
        cascade_config = ProtoEncoder.encode_message(1, model_alias)
        config_payload = ProtoEncoder.encode_message(7, cascade_config)
        
        # 5. Build Final Request Payload
        request = (
            ProtoEncoder.encode_string(1, cascade_id) +
            items_payload +
            meta_payload +
            exp_payload +
            config_payload +
            ProtoEncoder.encode_bool(8, True)  # blocking = true
        )
        
        # 6. Add gRPC framing
        framed = b"\x00" + struct.pack(">I", len(request)) + request
        
        return framed


class ProtoDecoder:
    """Lightweight decoder for Antigravity Protobuf responses"""
    
    @staticmethod
    def parse_grpc_response(data: bytes) -> Optional[str]:
        """Parse gRPC response to extract text content"""
        try:
            if len(data) < 5:
                return None
            
            message_length = struct.unpack(">I", data[1:5])[0]
            message = data[5:5 + message_length]
            
            return ProtoDecoder._extract_text(message)
            
        except Exception:
            return None
    
    @staticmethod
    def _extract_text(message: bytes) -> Optional[str]:
        """Extract readable text from protobuf message"""
        text_parts = []
        i = 0
        
        while i < len(message):
            if i >= len(message):
                break
            
            tag = message[i]
            wire_type = tag & 0x07
            
            if wire_type == 2:  # Length-delimited
                i += 1
                if i >= len(message):
                    break
                
                # Read length (varint)
                length = 0
                shift = 0
                while i < len(message):
                    byte = message[i]
                    i += 1
                    length |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                
                # Extract string content
                if i + length <= len(message) and length > 10:
                    try:
                        text = message[i:i + length].decode('utf-8', errors='ignore')
                        if text.isprintable() and len(text.strip()) > 5:
                            text_parts.append(text.strip())
                    except:
                        pass
                
                i += length
            else:
                i += 1
        
        return '\n'.join(text_parts) if text_parts else None


# ============================================
# Token Manager
# ============================================
class TokenManager:
    """
    Token Manager for Antigravity OAuth tokens
    Based on: /backend/ai-bridge/token_manager/
    """
    
    def __init__(self, token_dir: Path = None):
        self.token_dir = token_dir or config.TOKEN_DIR
        self.token_dir.mkdir(parents=True, exist_ok=True)
        
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._client_secret: Optional[str] = None
        self._expires_at: float = 0
        
        self._refresh_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Load saved tokens
        self._load_tokens()
    
    def _get_token_file(self) -> Path:
        return self.token_dir / 'tokens.json'
    
    def _load_tokens(self):
        """Load tokens from file"""
        token_file = self._get_token_file()
        if token_file.exists():
            try:
                with open(token_file, 'r') as f:
                    data = json.load(f)
                
                self._access_token = data.get('access_token')
                self._refresh_token = data.get('refresh_token')
                self._client_secret = data.get('client_secret')
                self._expires_at = data.get('expires_at', 0)
                
                logger.info("Tokens loaded from file")
            except Exception as e:
                logger.error(f"Failed to load tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to file"""
        token_file = self._get_token_file()
        try:
            data = {
                'access_token': self._access_token,
                'refresh_token': self._refresh_token,
                'client_secret': self._client_secret,
                'expires_at': self._expires_at,
                'saved_at': time.time()
            }
            
            with open(token_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info("Tokens saved to file")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")
    
    def set_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        client_secret: Optional[str] = None,
        expires_in: int = 3600
    ):
        """Set authentication tokens"""
        self._access_token = access_token
        if refresh_token:
            self._refresh_token = refresh_token
        if client_secret:
            self._client_secret = client_secret
        self._expires_at = time.time() + expires_in
        
        self._save_tokens()
        logger.info("Tokens updated")
    
    def import_from_dict(self, data: dict) -> bool:
        """Import tokens from dictionary"""
        try:
            access_token = data.get('access_token')
            if not access_token:
                logger.error("No access_token in data")
                return False
            
            self.set_tokens(
                access_token=access_token,
                refresh_token=data.get('refresh_token'),
                client_secret=data.get('client_secret'),
                expires_in=data.get('expires_in', 3600)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to import tokens: {e}")
            return False
    
    def import_from_file(self, filepath: str) -> bool:
        """Import tokens from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            return self.import_from_dict(data)
        except Exception as e:
            logger.error(f"Failed to import from file: {e}")
            return False
    
    def is_valid(self) -> bool:
        """Check if current token is valid"""
        if not self._access_token:
            return False
        return time.time() < self._expires_at
    
    def time_until_expiry(self) -> float:
        """Get seconds until token expires"""
        return max(0, self._expires_at - time.time())
    
    async def get_token(self) -> Optional[str]:
        """Get valid access token, refreshing if needed"""
        if self.is_valid():
            return self._access_token
        
        # Try to refresh
        if await self._refresh_access_token():
            return self._access_token
        
        return None
    
    async def _refresh_access_token(self) -> bool:
        """Refresh access token using refresh_token"""
        if not self._refresh_token:
            logger.warning("No refresh token available")
            return False
        
        if not self._client_secret:
            logger.warning("No client secret available for refresh")
            return False
        
        try:
            import httpx
            
            # Google OAuth2 token endpoint
            token_url = "https://oauth2.googleapis.com/token"
            
            # Client ID from Antigravity
            client_id = "77185425430.apps.googleusercontent.com"
            
            payload = {
                "client_id": client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    self._access_token = data.get('access_token')
                    self._expires_at = time.time() + data.get('expires_in', 3600)
                    
                    # Update refresh token if provided
                    if 'refresh_token' in data:
                        self._refresh_token = data['refresh_token']
                    
                    self._save_tokens()
                    logger.info("Token refreshed successfully")
                    return True
                else:
                    logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False
    
    async def start_auto_refresh(self):
        """Start automatic token refresh task"""
        self._running = True
        self._refresh_task = asyncio.create_task(self._auto_refresh_loop())
        logger.info("Auto token refresh started")
    
    async def stop(self):
        """Stop token manager"""
        self._running = False
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
        logger.info("Token manager stopped")
    
    async def _auto_refresh_loop(self):
        """Background task for auto-refreshing tokens"""
        while self._running:
            try:
                # Check if refresh is needed
                time_left = self.time_until_expiry()
                
                if time_left < config.TOKEN_REFRESH_INTERVAL:
                    logger.info("Token expiring soon, refreshing...")
                    await self._refresh_access_token()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto refresh error: {e}")
                await asyncio.sleep(60)
    
    def get_status(self) -> dict:
        """Get token status"""
        return {
            'has_access_token': bool(self._access_token),
            'has_refresh_token': bool(self._refresh_token),
            'has_client_secret': bool(self._client_secret),
            'is_valid': self.is_valid(),
            'expires_at': self._expires_at,
            'time_until_expiry': self.time_until_expiry()
        }


# ============================================
# Antigravity Client
# ============================================
@dataclass
class ChatResponse:
    """Represents a chat response"""
    content: str
    finish_reason: str = 'stop'
    provider: str = 'antigravity'
    model: str = 'default'
    usage: Dict[str, int] = field(default_factory=dict)
    elapsed_ms: int = 0
    
    def to_dict(self) -> dict:
        return {
            'content': self.content,
            'finish_reason': self.finish_reason,
            'provider': self.provider,
            'model': self.model,
            'usage': self.usage,
            'elapsed_ms': self.elapsed_ms
        }


class AntigravityClient:
    """
    gRPC Client for Antigravity/Jetski API
    Based on: /backend/ai-bridge/grpc_client/antigravity_client.py
    """
    
    def __init__(
        self,
        endpoint: str = None,
        token_manager: TokenManager = None,
        timeout: float = None,
        max_retries: int = None
    ):
        self.endpoint = endpoint or config.ANTIGRAVITY_ENDPOINT
        self.token_manager = token_manager
        self.timeout = timeout or config.REQUEST_TIMEOUT
        self.max_retries = max_retries or config.MAX_RETRIES
        
        self._connected = False
        self._http_client = None
        
        # Statistics
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
    
    async def connect(self) -> bool:
        """Initialize HTTP/2 client"""
        try:
            import httpx
            
            self._http_client = httpx.AsyncClient(
                http2=True,
                timeout=httpx.Timeout(self.timeout),
                verify=True
            )
            
            self._connected = True
            logger.info(f"Connected to Antigravity: {self.endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        
        self._connected = False
        logger.info("Disconnected from Antigravity")
    
    def is_connected(self) -> bool:
        return self._connected and self._http_client is not None
    
    async def _ensure_connected(self):
        if not self.is_connected():
            await self.connect()
    
    async def chat(
        self,
        message: str,
        conversation_id: str = None,
        system_prompt: str = None
    ) -> ChatResponse:
        """Send chat message and get response"""
        await self._ensure_connected()
        
        if not self.token_manager:
            raise RuntimeError("Token manager not configured")
        
        access_token = await self.token_manager.get_token()
        if not access_token:
            raise RuntimeError("No valid access token available")
        
        # Prepare prompt
        full_prompt = message
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {message}"
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Build request
        payload = ProtoEncoder.build_cascade_request(
            cascade_id=conversation_id,
            prompt=full_prompt,
            access_token=access_token
        )
        
        headers = {
            "Content-Type": "application/grpc",
            "TE": "trailers",
            "User-Agent": "dLNk-IDE/2.0.0 (compatible; Antigravity)",
            "Authorization": f"Bearer {access_token}"
        }
        
        start_time = time.time()
        self.request_count += 1
        
        # Retry loop
        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await self._http_client.post(
                    self.endpoint,
                    content=payload,
                    headers=headers
                )
                
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.total_latency_ms += elapsed_ms
                
                if response.status_code == 200:
                    self.success_count += 1
                    
                    response_text = ProtoDecoder.parse_grpc_response(response.content)
                    
                    return ChatResponse(
                        content=response_text or "",
                        finish_reason='stop' if response_text else 'empty',
                        provider='antigravity',
                        elapsed_ms=elapsed_ms
                    )
                else:
                    self.error_count += 1
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(f"Request failed (attempt {attempt + 1}): {last_error}")
                    
                    if response.status_code in (401, 403):
                        break
                    
                    await asyncio.sleep(1 * (attempt + 1))
                    
            except Exception as e:
                self.error_count += 1
                last_error = str(e)
                logger.warning(f"Request exception (attempt {attempt + 1}): {e}")
                await asyncio.sleep(1 * (attempt + 1))
        
        raise RuntimeError(f"Request failed after {self.max_retries} attempts: {last_error}")
    
    async def chat_stream(
        self,
        message: str,
        conversation_id: str = None,
        system_prompt: str = None
    ) -> AsyncIterator[str]:
        """Send chat message and stream response"""
        await self._ensure_connected()
        
        if not self.token_manager:
            raise RuntimeError("Token manager not configured")
        
        access_token = await self.token_manager.get_token()
        if not access_token:
            raise RuntimeError("No valid access token available")
        
        full_prompt = message
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {message}"
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        payload = ProtoEncoder.build_cascade_request(
            cascade_id=conversation_id,
            prompt=full_prompt,
            access_token=access_token
        )
        
        headers = {
            "Content-Type": "application/grpc",
            "TE": "trailers",
            "User-Agent": "dLNk-IDE/2.0.0 (compatible; Antigravity)",
            "Authorization": f"Bearer {access_token}"
        }
        
        self.request_count += 1
        
        try:
            async with self._http_client.stream(
                "POST",
                self.endpoint,
                content=payload,
                headers=headers
            ) as response:
                if response.status_code == 200:
                    self.success_count += 1
                    
                    buffer = b""
                    async for chunk in response.aiter_bytes():
                        buffer += chunk
                        
                        while len(buffer) >= 5:
                            message_length = struct.unpack(">I", buffer[1:5])[0]
                            
                            if len(buffer) >= 5 + message_length:
                                frame = buffer[:5 + message_length]
                                buffer = buffer[5 + message_length:]
                                
                                text = ProtoDecoder.parse_grpc_response(frame)
                                if text:
                                    yield text
                            else:
                                break
                else:
                    self.error_count += 1
                    raise RuntimeError(f"Streaming failed: HTTP {response.status_code}")
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Streaming error: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        avg_latency = (
            self.total_latency_ms / self.success_count 
            if self.success_count > 0 else 0
        )
        
        success_rate = (
            self.success_count / self.request_count * 100 
            if self.request_count > 0 else 0
        )
        
        return {
            'endpoint': self.endpoint,
            'connected': self._connected,
            'requests': self.request_count,
            'success': self.success_count,
            'errors': self.error_count,
            'success_rate': f"{success_rate:.1f}%",
            'avg_latency_ms': int(avg_latency),
            'token_valid': self.token_manager.is_valid() if self.token_manager else False
        }


# ============================================
# Provider Manager (Antigravity Only)
# ============================================
class ProviderManager:
    """
    Provider Manager - Antigravity Only
    Simplified version without fallback providers
    """
    
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self.client = AntigravityClient(token_manager=token_manager)
    
    async def initialize(self):
        """Initialize provider"""
        await self.client.connect()
        logger.info("Provider manager initialized (Antigravity only)")
    
    async def shutdown(self):
        """Shutdown provider"""
        await self.client.disconnect()
    
    async def chat(
        self,
        message: str,
        system_prompt: str = None,
        conversation_id: str = None,
        **kwargs
    ) -> dict:
        """Send chat message"""
        try:
            response = await self.client.chat(
                message=message,
                system_prompt=system_prompt,
                conversation_id=conversation_id
            )
            
            return {
                'success': True,
                'response': response.content,
                'provider': 'antigravity',
                'elapsed_ms': response.elapsed_ms
            }
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                'success': False,
                'response': str(e),
                'provider': 'antigravity',
                'elapsed_ms': 0
            }
    
    async def chat_stream(
        self,
        message: str,
        system_prompt: str = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat response"""
        async for chunk in self.client.chat_stream(
            message=message,
            system_prompt=system_prompt
        ):
            yield chunk
    
    def get_status(self) -> dict:
        """Get provider status"""
        return {
            'antigravity': {
                'available': True,
                'active': True,
                'stats': self.client.get_stats()
            }
        }
    
    def get_available_providers(self) -> List[str]:
        return ['antigravity']
    
    def get_active_provider(self) -> str:
        return 'antigravity'
    
    def get_stats(self) -> dict:
        return self.client.get_stats()


# ============================================
# WebSocket Server
# ============================================
@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client"""
    id: str
    websocket: Any
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    
    def update_activity(self):
        self.last_activity = time.time()


class WebSocketServer:
    """
    WebSocket Server for dLNk AI Bridge
    Based on: /backend/ai-bridge/servers/websocket_server.py
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        provider_manager: ProviderManager = None
    ):
        self.host = host or config.WS_HOST
        self.port = port or config.WS_PORT
        self.provider_manager = provider_manager
        
        self._clients: Dict[str, WebSocketClient] = {}
        self._server = None
        self._running = False
        
        # Statistics
        self.total_connections = 0
        self.total_messages = 0
        self.total_errors = 0
    
    async def start(self):
        """Start WebSocket server"""
        try:
            import websockets
            
            self._running = True
            
            self._server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10,
                max_size=10 * 1024 * 1024
            )
            
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            
            await self._server.wait_closed()
            
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
            raise
    
    async def stop(self):
        """Stop WebSocket server"""
        self._running = False
        
        for client_id in list(self._clients.keys()):
            await self._disconnect_client(client_id)
        
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        
        logger.info("WebSocket server stopped")
    
    async def _handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        client_id = str(uuid.uuid4())[:8]
        
        client = WebSocketClient(id=client_id, websocket=websocket)
        self._clients[client_id] = client
        self.total_connections += 1
        
        logger.info(f"Client connected: {client_id} (total: {len(self._clients)})")
        
        # Send welcome
        await self._send_to_client(client_id, {
            'type': 'connected',
            'data': {'client_id': client_id, 'server_time': time.time()}
        })
        
        try:
            async for message in websocket:
                await self._handle_message(client_id, message)
                
        except Exception as e:
            logger.error(f"Client {client_id} error: {e}")
            self.total_errors += 1
            
        finally:
            await self._disconnect_client(client_id)
    
    async def _disconnect_client(self, client_id: str):
        """Disconnect client"""
        if client_id in self._clients:
            client = self._clients[client_id]
            try:
                await client.websocket.close()
            except:
                pass
            del self._clients[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    async def _handle_message(self, client_id: str, raw_message: str):
        """Handle incoming message"""
        client = self._clients.get(client_id)
        if not client:
            return
        
        client.update_activity()
        self.total_messages += 1
        
        try:
            message = json.loads(raw_message)
            msg_type = message.get('type', 'unknown')
            msg_id = message.get('id', str(uuid.uuid4()))
            msg_data = message.get('data', {})
            
            # Handle different message types
            if msg_type == 'chat':
                await self._handle_chat(client_id, msg_id, msg_data)
            elif msg_type == 'chat_stream':
                await self._handle_chat_stream(client_id, msg_id, msg_data)
            elif msg_type == 'status':
                await self._handle_status(client_id, msg_id)
            elif msg_type == 'ping':
                await self._send_to_client(client_id, {
                    'type': 'pong',
                    'id': msg_id,
                    'data': {'timestamp': time.time()}
                })
            else:
                await self._send_error(client_id, msg_id, f"Unknown type: {msg_type}")
                
        except json.JSONDecodeError:
            await self._send_error(client_id, None, "Invalid JSON")
        except Exception as e:
            logger.error(f"Message error: {e}")
            await self._send_error(client_id, None, str(e))
    
    async def _handle_chat(self, client_id: str, msg_id: str, data: dict):
        """Handle chat message"""
        message = data.get('message', '')
        system_prompt = data.get('system_prompt')
        conversation_id = data.get('conversation_id')
        
        if not message:
            await self._send_error(client_id, msg_id, "Message is required")
            return
        
        if not self.provider_manager:
            await self._send_error(client_id, msg_id, "Provider not configured")
            return
        
        try:
            result = await self.provider_manager.chat(
                message=message,
                system_prompt=system_prompt,
                conversation_id=conversation_id
            )
            
            await self._send_to_client(client_id, {
                'type': 'response',
                'id': msg_id,
                'data': {
                    'content': result.get('response', ''),
                    'provider': result.get('provider', 'unknown'),
                    'elapsed_ms': result.get('elapsed_ms', 0),
                    'success': result.get('success', False)
                }
            })
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            await self._send_error(client_id, msg_id, str(e))
    
    async def _handle_chat_stream(self, client_id: str, msg_id: str, data: dict):
        """Handle streaming chat"""
        message = data.get('message', '')
        system_prompt = data.get('system_prompt')
        
        if not message:
            await self._send_error(client_id, msg_id, "Message is required")
            return
        
        if not self.provider_manager:
            await self._send_error(client_id, msg_id, "Provider not configured")
            return
        
        try:
            async for chunk in self.provider_manager.chat_stream(
                message=message,
                system_prompt=system_prompt
            ):
                await self._send_to_client(client_id, {
                    'type': 'stream',
                    'id': msg_id,
                    'data': {'chunk': chunk, 'done': False}
                })
            
            await self._send_to_client(client_id, {
                'type': 'stream',
                'id': msg_id,
                'data': {'chunk': '', 'done': True}
            })
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            await self._send_error(client_id, msg_id, str(e))
    
    async def _handle_status(self, client_id: str, msg_id: str):
        """Handle status request"""
        status = {
            'server': {
                'running': self._running,
                'clients': len(self._clients),
                'total_connections': self.total_connections,
                'total_messages': self.total_messages
            }
        }
        
        if self.provider_manager:
            status['providers'] = self.provider_manager.get_status()
        
        await self._send_to_client(client_id, {
            'type': 'response',
            'id': msg_id,
            'data': status
        })
    
    async def _send_to_client(self, client_id: str, message: dict):
        """Send message to client"""
        client = self._clients.get(client_id)
        if not client:
            return
        
        try:
            await client.websocket.send(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Send error: {e}")
    
    async def _send_error(self, client_id: str, msg_id: Optional[str], error: str):
        """Send error to client"""
        await self._send_to_client(client_id, {
            'type': 'error',
            'id': msg_id,
            'data': {'error': error, 'timestamp': time.time()}
        })
    
    def get_stats(self) -> dict:
        return {
            'host': self.host,
            'port': self.port,
            'running': self._running,
            'connected_clients': len(self._clients),
            'total_connections': self.total_connections,
            'total_messages': self.total_messages
        }


# ============================================
# REST API Server
# ============================================
class RESTServer:
    """
    REST API Server for dLNk AI Bridge
    Based on: /backend/ai-bridge/servers/rest_server.py
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        provider_manager: ProviderManager = None,
        token_manager: TokenManager = None
    ):
        self.host = host or config.REST_HOST
        self.port = port or config.REST_PORT
        self.provider_manager = provider_manager
        self.token_manager = token_manager
        
        self._app = None
        self._server = None
        self._running = False
        
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = None
    
    def _create_app(self):
        """Create FastAPI application"""
        from fastapi import FastAPI, HTTPException, Request
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import StreamingResponse, JSONResponse
        from pydantic import BaseModel
        
        class ChatRequest(BaseModel):
            message: str
            system_prompt: Optional[str] = None
            conversation_id: Optional[str] = None
            stream: bool = False
        
        class TokenRequest(BaseModel):
            access_token: str
            refresh_token: Optional[str] = None
            client_secret: Optional[str] = None
            expires_in: int = 3600
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            self.start_time = time.time()
            logger.info(f"REST API starting on http://{self.host}:{self.port}")
            yield
            logger.info("REST API shutting down")
        
        app = FastAPI(
            title="dLNk AI Bridge API",
            description="REST API for dLNk IDE - Antigravity Only",
            version="2.0.0",
            lifespan=lifespan
        )
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.middleware("http")
        async def count_requests(request: Request, call_next):
            self.total_requests += 1
            try:
                return await call_next(request)
            except Exception:
                self.total_errors += 1
                raise
        
        @app.get("/")
        async def root():
            return {
                "name": "dLNk AI Bridge",
                "version": "2.0.0",
                "provider": "antigravity",
                "status": "running"
            }
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "timestamp": time.time()}
        
        @app.post("/api/chat")
        async def chat(request: ChatRequest):
            if not self.provider_manager:
                raise HTTPException(503, "Provider not configured")
            
            if not request.message:
                raise HTTPException(400, "Message is required")
            
            try:
                result = await self.provider_manager.chat(
                    message=request.message,
                    system_prompt=request.system_prompt,
                    conversation_id=request.conversation_id
                )
                
                return {
                    "success": result.get('success', False),
                    "content": result.get('response', ''),
                    "provider": result.get('provider', 'unknown'),
                    "elapsed_ms": result.get('elapsed_ms', 0)
                }
                
            except Exception as e:
                logger.error(f"Chat error: {e}")
                raise HTTPException(500, str(e))
        
        @app.post("/api/chat/stream")
        async def chat_stream(request: ChatRequest):
            if not self.provider_manager:
                raise HTTPException(503, "Provider not configured")
            
            async def generate():
                try:
                    async for chunk in self.provider_manager.chat_stream(
                        message=request.message,
                        system_prompt=request.system_prompt
                    ):
                        yield f"data: {chunk}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: [ERROR] {str(e)}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
            )
        
        @app.get("/api/status")
        async def status():
            uptime = time.time() - self.start_time if self.start_time else 0
            
            return {
                "status": "running",
                "uptime_seconds": uptime,
                "total_requests": self.total_requests,
                "total_errors": self.total_errors,
                "provider": "antigravity",
                "token_valid": self.token_manager.is_valid() if self.token_manager else False,
                "providers": self.provider_manager.get_status() if self.provider_manager else {}
            }
        
        @app.post("/api/token")
        async def set_token(request: TokenRequest):
            if not self.token_manager:
                raise HTTPException(503, "Token manager not configured")
            
            try:
                self.token_manager.set_tokens(
                    access_token=request.access_token,
                    refresh_token=request.refresh_token,
                    client_secret=request.client_secret,
                    expires_in=request.expires_in
                )
                
                return {
                    "success": True,
                    "message": "Tokens updated",
                    "valid": self.token_manager.is_valid()
                }
                
            except Exception as e:
                logger.error(f"Token error: {e}")
                raise HTTPException(500, str(e))
        
        @app.post("/api/import-token")
        async def import_token(request: Request):
            if not self.token_manager:
                raise HTTPException(503, "Token manager not configured")
            
            try:
                data = await request.json()
                success = self.token_manager.import_from_dict(data)
                
                if success:
                    return {"success": True, "message": "Tokens imported"}
                else:
                    raise HTTPException(400, "Failed to import tokens")
                    
            except Exception as e:
                logger.error(f"Import error: {e}")
                raise HTTPException(500, str(e))
        
        @app.get("/api/token/status")
        async def token_status():
            if not self.token_manager:
                return {"configured": False}
            
            return {
                "configured": True,
                "status": self.token_manager.get_status()
            }
        
        return app
    
    async def start(self):
        """Start REST server"""
        import uvicorn
        
        self._app = self._create_app()
        self._running = True
        
        config = uvicorn.Config(
            app=self._app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=False
        )
        
        self._server = uvicorn.Server(config)
        
        try:
            await self._server.serve()
        except Exception as e:
            logger.error(f"REST server error: {e}")
            raise
    
    async def stop(self):
        """Stop REST server"""
        self._running = False
        if self._server:
            self._server.should_exit = True
        logger.info("REST server stopped")
    
    def get_stats(self) -> dict:
        uptime = time.time() - self.start_time if self.start_time else 0
        return {
            'host': self.host,
            'port': self.port,
            'running': self._running,
            'uptime_seconds': uptime,
            'total_requests': self.total_requests,
            'total_errors': self.total_errors
        }


# ============================================
# Main Application
# ============================================
class DLNKBridge:
    """
    Main dLNk AI Bridge Application
    Antigravity Only Edition
    """
    
    def __init__(self):
        self.token_manager = TokenManager()
        self.provider_manager = ProviderManager(self.token_manager)
        
        self.ws_server = WebSocketServer(provider_manager=self.provider_manager)
        self.rest_server = RESTServer(
            provider_manager=self.provider_manager,
            token_manager=self.token_manager
        )
        
        self._running = False
    
    async def start(self):
        """Start all services"""
        logger.info("=" * 60)
        logger.info("  dLNk AI Bridge - Antigravity Only Edition")
        logger.info("  Version: 2.0.0")
        logger.info("=" * 60)
        
        self._running = True
        
        # Initialize provider
        await self.provider_manager.initialize()
        
        # Start token auto-refresh
        await self.token_manager.start_auto_refresh()
        
        # Start servers
        ws_task = asyncio.create_task(self.ws_server.start())
        rest_task = asyncio.create_task(self.rest_server.start())
        
        logger.info("")
        logger.info("Services started:")
        logger.info(f"  WebSocket: ws://{config.WS_HOST}:{config.WS_PORT}")
        logger.info(f"  REST API:  http://{config.REST_HOST}:{config.REST_PORT}")
        logger.info("")
        logger.info("Token status:")
        logger.info(f"  Valid: {self.token_manager.is_valid()}")
        logger.info(f"  Time until expiry: {self.token_manager.time_until_expiry():.0f}s")
        logger.info("")
        
        if not self.token_manager.is_valid():
            logger.warning("No valid token found. Please import tokens via:")
            logger.warning(f"  POST http://{config.REST_HOST}:{config.REST_PORT}/api/import-token")
            logger.warning("")
        
        try:
            await asyncio.gather(ws_task, rest_task)
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        """Stop all services"""
        logger.info("Shutting down...")
        
        self._running = False
        
        await self.ws_server.stop()
        await self.rest_server.stop()
        await self.provider_manager.shutdown()
        await self.token_manager.stop()
        
        logger.info("Shutdown complete")


async def main():
    """Main entry point"""
    bridge = DLNKBridge()
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await bridge.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBye!")
