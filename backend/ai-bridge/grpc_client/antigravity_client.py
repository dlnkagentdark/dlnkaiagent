"""
dLNk AI Bridge - Antigravity gRPC Client
========================================
gRPC Client for Antigravity/Jetski API with streaming support.

Based on: /source-files/dlnk_core/dlnk_antigravity_bridge.py

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import uuid
import time
from typing import Optional, AsyncIterator, Dict, Any, Callable
from dataclasses import dataclass, field

from .proto_encoder import ProtoEncoder, ProtoDecoder

logger = logging.getLogger('AntigravityClient')


@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # 'user', 'assistant', or 'system'
    content: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp
        }


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
    
    Features:
    - HTTP/2 with binary protobuf encoding
    - Streaming responses
    - Auto-reconnect
    - Token management integration
    - Request/response statistics
    
    Usage:
        client = AntigravityClient(token_manager=token_mgr)
        await client.connect()
        response = await client.chat("Hello!")
        await client.disconnect()
    """
    
    # Default endpoint
    DEFAULT_ENDPOINT = "https://antigravity-worker.google.com/exa.language_server_pb.LanguageServerService/SendUserCascadeMessage"
    
    def __init__(
        self,
        endpoint: str = None,
        token_manager = None,
        use_ssl: bool = True,
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize Antigravity client
        
        Args:
            endpoint: gRPC endpoint URL
            token_manager: TokenManager instance for authentication
            use_ssl: Whether to use SSL/TLS
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        self.token_manager = token_manager
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Connection state
        self._connected = False
        self._http_client = None
        
        # Statistics
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
        
        # Callbacks
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
    
    async def connect(self) -> bool:
        """
        Initialize HTTP/2 client for gRPC communication
        
        Returns:
            True if connection successful
        """
        try:
            import httpx
            
            # Create HTTP/2 client
            self._http_client = httpx.AsyncClient(
                http2=True,
                timeout=httpx.Timeout(self.timeout),
                verify=self.use_ssl
            )
            
            self._connected = True
            logger.info(f"Connected to Antigravity endpoint: {self.endpoint}")
            
            if self._on_connect:
                await self._on_connect()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Antigravity: {e}")
            self._connected = False
            
            if self._on_error:
                await self._on_error(e)
            
            return False
    
    async def disconnect(self):
        """Close HTTP client connection"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        
        self._connected = False
        logger.info("Disconnected from Antigravity")
        
        if self._on_disconnect:
            await self._on_disconnect()
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected and self._http_client is not None
    
    async def _ensure_connected(self):
        """Ensure client is connected, reconnect if needed"""
        if not self.is_connected():
            await self.connect()
    
    async def chat(
        self,
        message: str,
        conversation_id: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> ChatResponse:
        """
        Send chat message and get response (non-streaming)
        
        Args:
            message: User message
            conversation_id: Optional conversation ID for context
            system_prompt: Optional system prompt
            temperature: Sampling temperature (not used in Antigravity)
            max_tokens: Maximum response tokens (not used in Antigravity)
        
        Returns:
            ChatResponse with AI response
        
        Raises:
            ConnectionError: If not connected and cannot reconnect
            RuntimeError: If request fails after retries
        """
        await self._ensure_connected()
        
        if not self.token_manager:
            raise RuntimeError("Token manager not configured")
        
        # Get valid access token
        access_token = await self.token_manager.get_token()
        if not access_token:
            raise RuntimeError("No valid access token available")
        
        # Prepare prompt with system prompt if provided
        full_prompt = message
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {message}"
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Build protobuf request
        payload = ProtoEncoder.build_cascade_request(
            cascade_id=conversation_id,
            prompt=full_prompt,
            access_token=access_token
        )
        
        # Request headers
        headers = {
            "Content-Type": "application/grpc",
            "TE": "trailers",
            "User-Agent": "dLNk-IDE/1.0.0 (compatible; Antigravity)",
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
                    
                    # Parse gRPC response
                    response_text = ProtoDecoder.parse_grpc_response(response.content)
                    
                    if response_text:
                        return ChatResponse(
                            content=response_text,
                            finish_reason='stop',
                            provider='antigravity',
                            elapsed_ms=elapsed_ms
                        )
                    else:
                        # Empty response
                        return ChatResponse(
                            content="",
                            finish_reason='empty',
                            provider='antigravity',
                            elapsed_ms=elapsed_ms
                        )
                else:
                    self.error_count += 1
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(f"Antigravity request failed (attempt {attempt + 1}): {last_error}")
                    
                    # Don't retry on auth errors
                    if response.status_code in (401, 403):
                        break
                    
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
                    
            except Exception as e:
                self.error_count += 1
                last_error = str(e)
                logger.warning(f"Antigravity request exception (attempt {attempt + 1}): {e}")
                
                if self._on_error:
                    await self._on_error(e)
                
                await asyncio.sleep(1 * (attempt + 1))
        
        raise RuntimeError(f"Antigravity request failed after {self.max_retries} attempts: {last_error}")
    
    async def chat_stream(
        self,
        message: str,
        conversation_id: str = None,
        system_prompt: str = None
    ) -> AsyncIterator[str]:
        """
        Send chat message and stream response
        
        Args:
            message: User message
            conversation_id: Optional conversation ID
            system_prompt: Optional system prompt
        
        Yields:
            Response text chunks
        """
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
            "User-Agent": "dLNk-IDE/1.0.0 (compatible; Antigravity)",
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
                        
                        # Try to parse complete frames from buffer
                        while len(buffer) >= 5:
                            # Read frame length
                            import struct
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
                    raise RuntimeError(f"Streaming request failed: HTTP {response.status_code}")
                    
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
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
    
    # Event handlers
    def on_connect(self, callback: Callable):
        """Set connection callback"""
        self._on_connect = callback
    
    def on_disconnect(self, callback: Callable):
        """Set disconnection callback"""
        self._on_disconnect = callback
    
    def on_error(self, callback: Callable):
        """Set error callback"""
        self._on_error = callback
