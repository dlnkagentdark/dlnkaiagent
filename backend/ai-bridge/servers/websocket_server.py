"""
dLNk AI Bridge - WebSocket Server
=================================
WebSocket server for real-time communication with VS Code Extension.

Port: 8765 (default)

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Set, Optional, Any, Callable
from dataclasses import dataclass, field

logger = logging.getLogger('WebSocketServer')


@dataclass
class WebSocketClient:
    """Represents a connected WebSocket client"""
    id: str
    websocket: Any
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    
    def update_activity(self):
        self.last_activity = time.time()


class WebSocketServer:
    """
    WebSocket Server for dLNk AI Bridge
    
    Features:
    - Multiple client connections
    - Real-time streaming responses
    - Ping/pong for connection health
    - Message routing
    - Event broadcasting
    
    Message Protocol:
    {
        "type": "chat" | "status" | "ping" | "subscribe" | "unsubscribe",
        "id": "unique-message-id",
        "data": { ... }
    }
    
    Response Protocol:
    {
        "type": "response" | "stream" | "error" | "pong" | "event",
        "id": "original-message-id",
        "data": { ... }
    }
    """
    
    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 8765,
        provider_manager = None,
        max_connections: int = 100,
        ping_interval: int = 30,
        ping_timeout: int = 10
    ):
        """
        Initialize WebSocket server
        
        Args:
            host: Server host address
            port: Server port
            provider_manager: AI provider manager for handling requests
            max_connections: Maximum concurrent connections
            ping_interval: Interval for ping messages (seconds)
            ping_timeout: Timeout for pong response (seconds)
        """
        self.host = host
        self.port = port
        self.provider_manager = provider_manager
        self.max_connections = max_connections
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        
        # Connected clients
        self._clients: Dict[str, WebSocketClient] = {}
        
        # Server state
        self._server = None
        self._running = False
        
        # Statistics
        self.total_connections = 0
        self.total_messages = 0
        self.total_errors = 0
        
        # Event handlers
        self._message_handlers: Dict[str, Callable] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default message handlers"""
        self._message_handlers = {
            'chat': self._handle_chat,
            'chat_stream': self._handle_chat_stream,
            'status': self._handle_status,
            'ping': self._handle_ping,
            'history': self._handle_history,
        }
    
    async def start(self):
        """Start the WebSocket server"""
        try:
            import websockets
            
            self._running = True
            
            self._server = await websockets.serve(
                self._handle_connection,
                self.host,
                self.port,
                ping_interval=self.ping_interval,
                ping_timeout=self.ping_timeout,
                max_size=10 * 1024 * 1024  # 10 MB max message size
            )
            
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            
            # Keep server running
            await self._server.wait_closed()
            
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
            raise
    
    async def stop(self):
        """Stop the WebSocket server"""
        self._running = False
        
        # Close all client connections
        for client_id in list(self._clients.keys()):
            await self._disconnect_client(client_id)
        
        # Close server
        if self._server:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
        
        logger.info("WebSocket server stopped")
    
    async def _handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        client_id = str(uuid.uuid4())[:8]
        
        # Check connection limit
        if len(self._clients) >= self.max_connections:
            await websocket.close(1013, "Server at capacity")
            logger.warning(f"Connection rejected: server at capacity")
            return
        
        # Register client
        client = WebSocketClient(
            id=client_id,
            websocket=websocket,
            metadata={'path': path}
        )
        self._clients[client_id] = client
        self.total_connections += 1
        
        logger.info(f"Client connected: {client_id} (total: {len(self._clients)})")
        
        # Send welcome message
        await self._send_to_client(client_id, {
            'type': 'connected',
            'data': {
                'client_id': client_id,
                'server_time': time.time()
            }
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
        """Disconnect and cleanup client"""
        if client_id in self._clients:
            client = self._clients[client_id]
            
            try:
                await client.websocket.close()
            except:
                pass
            
            del self._clients[client_id]
            logger.info(f"Client disconnected: {client_id} (total: {len(self._clients)})")
    
    async def _handle_message(self, client_id: str, raw_message: str):
        """Handle incoming message from client"""
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
            
            logger.debug(f"Message from {client_id}: type={msg_type}")
            
            # Route to handler
            handler = self._message_handlers.get(msg_type)
            
            if handler:
                await handler(client_id, msg_id, msg_data)
            else:
                await self._send_error(client_id, msg_id, f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            await self._send_error(client_id, None, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await self._send_error(client_id, None, str(e))
    
    async def _handle_chat(self, client_id: str, msg_id: str, data: dict):
        """Handle chat message (non-streaming)"""
        message = data.get('message', '')
        system_prompt = data.get('system_prompt')
        conversation_id = data.get('conversation_id')
        
        if not message:
            await self._send_error(client_id, msg_id, "Message is required")
            return
        
        if not self.provider_manager:
            await self._send_error(client_id, msg_id, "AI provider not configured")
            return
        
        try:
            # Get response from provider
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
        """Handle streaming chat message"""
        message = data.get('message', '')
        system_prompt = data.get('system_prompt')
        
        if not message:
            await self._send_error(client_id, msg_id, "Message is required")
            return
        
        if not self.provider_manager:
            await self._send_error(client_id, msg_id, "AI provider not configured")
            return
        
        try:
            # Stream response
            async for chunk in self.provider_manager.chat_stream(
                message=message,
                system_prompt=system_prompt
            ):
                await self._send_to_client(client_id, {
                    'type': 'stream',
                    'id': msg_id,
                    'data': {
                        'chunk': chunk,
                        'done': False
                    }
                })
            
            # Send completion
            await self._send_to_client(client_id, {
                'type': 'stream',
                'id': msg_id,
                'data': {
                    'chunk': '',
                    'done': True
                }
            })
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            await self._send_error(client_id, msg_id, str(e))
    
    async def _handle_status(self, client_id: str, msg_id: str, data: dict):
        """Handle status request"""
        status = {
            'server': {
                'running': self._running,
                'clients': len(self._clients),
                'total_connections': self.total_connections,
                'total_messages': self.total_messages,
                'total_errors': self.total_errors
            }
        }
        
        if self.provider_manager:
            status['providers'] = self.provider_manager.get_status()
        
        await self._send_to_client(client_id, {
            'type': 'response',
            'id': msg_id,
            'data': status
        })
    
    async def _handle_ping(self, client_id: str, msg_id: str, data: dict):
        """Handle ping message"""
        await self._send_to_client(client_id, {
            'type': 'pong',
            'id': msg_id,
            'data': {
                'timestamp': time.time()
            }
        })
    
    async def _handle_history(self, client_id: str, msg_id: str, data: dict):
        """Handle history request"""
        # Placeholder - implement conversation history
        await self._send_to_client(client_id, {
            'type': 'response',
            'id': msg_id,
            'data': {
                'history': [],
                'message': 'History not implemented yet'
            }
        })
    
    async def _send_to_client(self, client_id: str, message: dict):
        """Send message to specific client"""
        client = self._clients.get(client_id)
        if not client:
            return
        
        try:
            await client.websocket.send(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Send error to {client_id}: {e}")
    
    async def _send_error(self, client_id: str, msg_id: Optional[str], error: str):
        """Send error message to client"""
        await self._send_to_client(client_id, {
            'type': 'error',
            'id': msg_id,
            'data': {
                'error': error,
                'timestamp': time.time()
            }
        })
    
    async def broadcast(self, message: dict, exclude: Set[str] = None):
        """Broadcast message to all connected clients"""
        exclude = exclude or set()
        
        for client_id in self._clients:
            if client_id not in exclude:
                await self._send_to_client(client_id, message)
    
    def get_stats(self) -> dict:
        """Get server statistics"""
        return {
            'host': self.host,
            'port': self.port,
            'running': self._running,
            'connected_clients': len(self._clients),
            'total_connections': self.total_connections,
            'total_messages': self.total_messages,
            'total_errors': self.total_errors
        }
    
    def register_handler(self, msg_type: str, handler: Callable):
        """Register custom message handler"""
        self._message_handlers[msg_type] = handler
