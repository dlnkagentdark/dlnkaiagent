"""
dLNk AI Bridge - Antigravity gRPC Client
========================================
gRPC Client for Antigravity/Jetski API with streaming support.

Enhanced Error Handling (v1.1.0):
- Connection error recovery
- Token refresh on auth failure
- Graceful degradation
- Detailed error logging
- Circuit breaker pattern

Based on: /source-files/dlnk_core/dlnk_antigravity_bridge.py

Author: dLNk Team (AI-05)
Version: 1.1.0
Updated: 2024-12-25
"""

import asyncio
import logging
import uuid
import time
import traceback
from typing import Optional, AsyncIterator, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .proto_encoder import ProtoEncoder, ProtoDecoder

logger = logging.getLogger('AntigravityClient')


class ConnectionState(Enum):
    """Connection state enum"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class GRPCError(Exception):
    """Base exception for gRPC errors"""
    def __init__(self, message: str, code: int = None, details: str = None):
        super().__init__(message)
        self.code = code
        self.details = details


class AuthenticationError(GRPCError):
    """Authentication failed"""
    pass


class ConnectionError(GRPCError):
    """Connection failed"""
    pass


class TimeoutError(GRPCError):
    """Request timeout"""
    pass


class RateLimitError(GRPCError):
    """Rate limit exceeded"""
    pass


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
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'content': self.content,
            'finish_reason': self.finish_reason,
            'provider': self.provider,
            'model': self.model,
            'usage': self.usage,
            'elapsed_ms': self.elapsed_ms,
            'error': self.error
        }


class AntigravityClient:
    """
    gRPC Client for Antigravity/Jetski API
    
    Features:
    - HTTP/2 with binary protobuf encoding
    - Streaming responses
    - Auto-reconnect with exponential backoff
    - Token management integration
    - Request/response statistics
    - Enhanced error handling
    - Circuit breaker pattern
    
    Usage:
        client = AntigravityClient(token_manager=token_mgr)
        await client.connect()
        response = await client.chat("Hello!")
        await client.disconnect()
    """
    
    # Default endpoint
    DEFAULT_ENDPOINT = "https://antigravity-worker.google.com/exa.language_server_pb.LanguageServerService/SendUserCascadeMessage"
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_THRESHOLD = 5  # failures before opening circuit
    CIRCUIT_BREAKER_TIMEOUT = 60   # seconds before trying again
    
    def __init__(
        self,
        endpoint: str = None,
        token_manager = None,
        use_ssl: bool = True,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Antigravity client
        
        Args:
            endpoint: gRPC endpoint URL
            token_manager: TokenManager instance for authentication
            use_ssl: Whether to use SSL/TLS
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Base delay between retries (exponential backoff)
        """
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        self.token_manager = token_manager
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Connection state
        self._state = ConnectionState.DISCONNECTED
        self._http_client = None
        self._last_error: Optional[str] = None
        
        # Circuit breaker
        self._consecutive_failures = 0
        self._circuit_open_until = 0
        
        # Statistics
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
        self._error_history: list = []
        
        # Callbacks
        self._on_connect: Optional[Callable] = None
        self._on_disconnect: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._on_reconnect: Optional[Callable] = None
    
    @property
    def state(self) -> ConnectionState:
        """Get current connection state"""
        return self._state
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self._consecutive_failures >= self.CIRCUIT_BREAKER_THRESHOLD:
            if time.time() < self._circuit_open_until:
                return True
            # Reset circuit breaker for retry
            self._consecutive_failures = 0
        return False
    
    def _record_failure(self, error: str):
        """Record a failure for circuit breaker"""
        self._consecutive_failures += 1
        self._last_error = error
        self._error_history.append({
            'time': time.time(),
            'error': error
        })
        # Keep only last 100 errors
        if len(self._error_history) > 100:
            self._error_history = self._error_history[-100:]
        
        if self._consecutive_failures >= self.CIRCUIT_BREAKER_THRESHOLD:
            self._circuit_open_until = time.time() + self.CIRCUIT_BREAKER_TIMEOUT
            logger.warning(f"Circuit breaker OPEN - too many failures ({self._consecutive_failures})")
    
    def _record_success(self):
        """Record a success, reset circuit breaker"""
        self._consecutive_failures = 0
        self._last_error = None
    
    async def connect(self) -> bool:
        """
        Initialize HTTP/2 client for gRPC communication
        
        Returns:
            True if connection successful
            
        Raises:
            ConnectionError: If connection fails
        """
        if self._state == ConnectionState.CONNECTED:
            return True
        
        self._state = ConnectionState.CONNECTING
        
        try:
            import httpx
            
            # Create HTTP/2 client with proper error handling
            self._http_client = httpx.AsyncClient(
                http2=True,
                timeout=httpx.Timeout(self.timeout, connect=10.0),
                verify=self.use_ssl,
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
            
            self._state = ConnectionState.CONNECTED
            logger.info(f"Connected to Antigravity endpoint: {self.endpoint}")
            
            if self._on_connect:
                try:
                    await self._on_connect()
                except Exception as e:
                    logger.warning(f"on_connect callback error: {e}")
            
            return True
            
        except ImportError as e:
            error_msg = f"httpx not installed: {e}"
            logger.error(error_msg)
            self._state = ConnectionState.ERROR
            self._last_error = error_msg
            raise ConnectionError(error_msg)
            
        except Exception as e:
            error_msg = f"Failed to connect to Antigravity: {e}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            self._state = ConnectionState.ERROR
            self._last_error = error_msg
            self._record_failure(error_msg)
            
            if self._on_error:
                try:
                    await self._on_error(e)
                except Exception:
                    pass
            
            raise ConnectionError(error_msg)
    
    async def disconnect(self):
        """Close HTTP client connection gracefully"""
        if self._http_client:
            try:
                await self._http_client.aclose()
            except Exception as e:
                logger.warning(f"Error closing HTTP client: {e}")
            finally:
                self._http_client = None
        
        self._state = ConnectionState.DISCONNECTED
        logger.info("Disconnected from Antigravity")
        
        if self._on_disconnect:
            try:
                await self._on_disconnect()
            except Exception as e:
                logger.warning(f"on_disconnect callback error: {e}")
    
    async def reconnect(self) -> bool:
        """
        Attempt to reconnect with exponential backoff
        
        Returns:
            True if reconnection successful
        """
        self._state = ConnectionState.RECONNECTING
        
        for attempt in range(self.max_retries):
            try:
                await self.disconnect()
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                
                if await self.connect():
                    logger.info(f"Reconnected after {attempt + 1} attempts")
                    if self._on_reconnect:
                        await self._on_reconnect()
                    return True
                    
            except Exception as e:
                logger.warning(f"Reconnect attempt {attempt + 1} failed: {e}")
        
        self._state = ConnectionState.ERROR
        return False
    
    def is_connected(self) -> bool:
        """Check if client is connected and ready"""
        return (
            self._state == ConnectionState.CONNECTED and 
            self._http_client is not None and
            not self._is_circuit_open()
        )
    
    async def _ensure_connected(self):
        """Ensure client is connected, reconnect if needed"""
        if self._is_circuit_open():
            raise ConnectionError(
                f"Circuit breaker is open due to repeated failures. "
                f"Last error: {self._last_error}"
            )
        
        if not self.is_connected():
            if not await self.connect():
                raise ConnectionError("Failed to establish connection")
    
    async def _validate_token(self) -> str:
        """
        Validate and get access token
        
        Returns:
            Valid access token
            
        Raises:
            AuthenticationError: If token is invalid or unavailable
        """
        if not self.token_manager:
            raise AuthenticationError("Token manager not configured")
        
        try:
            access_token = await self.token_manager.get_token()
            if not access_token:
                raise AuthenticationError("No valid access token available")
            return access_token
        except Exception as e:
            raise AuthenticationError(f"Token validation failed: {e}")
    
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
            AuthenticationError: If authentication fails
            TimeoutError: If request times out
            GRPCError: For other gRPC errors
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            await self._ensure_connected()
            access_token = await self._validate_token()
            
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
                "User-Agent": "dLNk-IDE/1.1.0 (compatible; Antigravity)",
                "Authorization": f"Bearer {access_token}"
            }
            
            # Retry loop with exponential backoff
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
                    
                    # Handle response based on status code
                    if response.status_code == 200:
                        self.success_count += 1
                        self._record_success()
                        
                        # Parse gRPC response
                        response_text = ProtoDecoder.parse_grpc_response(response.content)
                        
                        return ChatResponse(
                            content=response_text or "",
                            finish_reason='stop' if response_text else 'empty',
                            provider='antigravity',
                            elapsed_ms=elapsed_ms
                        )
                    
                    elif response.status_code == 401:
                        # Authentication error - try to refresh token
                        self.error_count += 1
                        if self.token_manager and hasattr(self.token_manager, 'refresh'):
                            logger.info("Attempting token refresh...")
                            await self.token_manager.refresh()
                            access_token = await self._validate_token()
                            headers["Authorization"] = f"Bearer {access_token}"
                            continue
                        raise AuthenticationError("Authentication failed", code=401)
                    
                    elif response.status_code == 403:
                        self.error_count += 1
                        raise AuthenticationError("Access forbidden", code=403)
                    
                    elif response.status_code == 429:
                        # Rate limit - wait and retry
                        self.error_count += 1
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logger.warning(f"Rate limited, waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue
                    
                    elif response.status_code >= 500:
                        # Server error - retry with backoff
                        self.error_count += 1
                        last_error = f"Server error: HTTP {response.status_code}"
                        logger.warning(f"{last_error} (attempt {attempt + 1})")
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    
                    else:
                        self.error_count += 1
                        last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                        logger.warning(f"Request failed (attempt {attempt + 1}): {last_error}")
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                
                except asyncio.TimeoutError:
                    self.error_count += 1
                    last_error = "Request timeout"
                    logger.warning(f"Timeout (attempt {attempt + 1})")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    
                except Exception as e:
                    self.error_count += 1
                    last_error = str(e)
                    logger.warning(f"Request exception (attempt {attempt + 1}): {e}")
                    logger.debug(traceback.format_exc())
                    
                    if self._on_error:
                        try:
                            await self._on_error(e)
                        except Exception:
                            pass
                    
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
            
            # All retries failed
            self._record_failure(last_error)
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            return ChatResponse(
                content="",
                finish_reason='error',
                provider='antigravity',
                elapsed_ms=elapsed_ms,
                error=f"Request failed after {self.max_retries} attempts: {last_error}"
            )
            
        except (AuthenticationError, ConnectionError) as e:
            self._record_failure(str(e))
            elapsed_ms = int((time.time() - start_time) * 1000)
            return ChatResponse(
                content="",
                finish_reason='error',
                provider='antigravity',
                elapsed_ms=elapsed_ms,
                error=str(e)
            )
    
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
            
        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
        """
        self.request_count += 1
        
        try:
            await self._ensure_connected()
            access_token = await self._validate_token()
            
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
                "User-Agent": "dLNk-IDE/1.1.0 (compatible; Antigravity)",
                "Authorization": f"Bearer {access_token}"
            }
            
            async with self._http_client.stream(
                "POST",
                self.endpoint,
                content=payload,
                headers=headers
            ) as response:
                if response.status_code == 200:
                    self.success_count += 1
                    self._record_success()
                    
                    buffer = b""
                    async for chunk in response.aiter_bytes():
                        buffer += chunk
                        
                        # Try to parse complete frames from buffer
                        while len(buffer) >= 5:
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
                
                elif response.status_code == 401:
                    self.error_count += 1
                    self._record_failure("Authentication failed")
                    raise AuthenticationError("Authentication failed during streaming")
                
                else:
                    self.error_count += 1
                    error_msg = f"Streaming request failed: HTTP {response.status_code}"
                    self._record_failure(error_msg)
                    raise GRPCError(error_msg, code=response.status_code)
                    
        except (AuthenticationError, ConnectionError, GRPCError):
            raise
        except Exception as e:
            self.error_count += 1
            error_msg = f"Streaming error: {e}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            self._record_failure(error_msg)
            raise GRPCError(error_msg)
    
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
            'state': self._state.value,
            'connected': self.is_connected(),
            'requests': self.request_count,
            'success': self.success_count,
            'errors': self.error_count,
            'success_rate': f"{success_rate:.1f}%",
            'avg_latency_ms': int(avg_latency),
            'token_valid': self.token_manager.is_valid() if self.token_manager else False,
            'circuit_breaker': {
                'consecutive_failures': self._consecutive_failures,
                'is_open': self._is_circuit_open(),
                'last_error': self._last_error
            }
        }
    
    def get_error_history(self, limit: int = 10) -> list:
        """Get recent error history"""
        return self._error_history[-limit:]
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
        self._error_history = []
    
    def reset_circuit_breaker(self):
        """Manually reset circuit breaker"""
        self._consecutive_failures = 0
        self._circuit_open_until = 0
        self._last_error = None
        logger.info("Circuit breaker reset manually")
    
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
    
    def on_reconnect(self, callback: Callable):
        """Set reconnection callback"""
        self._on_reconnect = callback
