#!/usr/bin/env python3
"""
dLNk AI Bridge - Main Entry Point
==================================
Connects dLNk IDE to dLNk AI/Jetski gRPC API with fallback support.

Features:
- gRPC Client for dLNk AI
- Token Manager with auto-refresh
- WebSocket Server (port 8765)
- REST API Server (port 8766)
- Multi-provider fallback system

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import signal
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from grpc_client.dlnk_ai_client import dLNk AIClient
from token_manager.token_refresh import TokenManager
from servers.websocket_server import WebSocketServer
from servers.rest_server import RESTServer
from fallback.provider_manager import ProviderManager
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(
    name='dLNk-AI-Bridge',
    level='INFO',
    log_file='dlnk_bridge.log'
)


class AIBridge:
    """
    dLNk AI Bridge - Main Application Class
    
    Orchestrates all components:
    - Token Manager
    - gRPC Client
    - Provider Manager
    - WebSocket Server
    - REST API Server
    """
    
    def __init__(self):
        self.config = Config()
        self.token_manager: TokenManager = None
        self.grpc_client: dLNk AIClient = None
        self.provider_manager: ProviderManager = None
        self.ws_server: WebSocketServer = None
        self.rest_server: RESTServer = None
        
        self._running = False
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("=" * 60)
        logger.info("Initializing dLNk AI Bridge...")
        logger.info("=" * 60)
        
        # 1. Initialize Token Manager
        logger.info("Starting Token Manager...")
        self.token_manager = TokenManager(self.config)
        await self.token_manager.start()
        
        token_status = "Valid" if self.token_manager.is_valid() else "Not available"
        logger.info(f"Token Manager started - Token: {token_status}")
        
        # 2. Initialize gRPC Client
        logger.info("Initializing dLNk AI gRPC Client...")
        self.grpc_client = dLNk AIClient(
            endpoint=self.config.DLNK_AI_ENDPOINT,
            token_manager=self.token_manager
        )
        
        if await self.grpc_client.connect():
            logger.info("gRPC Client connected")
        else:
            logger.warning("gRPC Client connection failed - will use fallback providers")
        
        # 3. Initialize Provider Manager with fallback
        logger.info("Initializing Provider Manager...")
        self.provider_manager = ProviderManager(
            primary_client=self.grpc_client,
            config=self.config
        )
        
        available = self.provider_manager.get_available_providers()
        logger.info(f"Provider Manager initialized - Available: {available}")
        
        # 4. Initialize WebSocket Server
        logger.info("Initializing WebSocket Server...")
        self.ws_server = WebSocketServer(
            host=self.config.WS_HOST,
            port=self.config.WS_PORT,
            provider_manager=self.provider_manager,
            max_connections=self.config.WS_MAX_CONNECTIONS
        )
        
        # 5. Initialize REST API Server
        logger.info("Initializing REST API Server...")
        self.rest_server = RESTServer(
            host=self.config.REST_HOST,
            port=self.config.REST_PORT,
            provider_manager=self.provider_manager,
            token_manager=self.token_manager,
            cors_origins=self.config.REST_CORS_ORIGINS
        )
        
        logger.info("=" * 60)
        logger.info("dLNk AI Bridge initialized successfully!")
        logger.info("=" * 60)
        logger.info(f"WebSocket Server: ws://{self.config.WS_HOST}:{self.config.WS_PORT}")
        logger.info(f"REST API Server: http://{self.config.REST_HOST}:{self.config.REST_PORT}")
        logger.info("=" * 60)
    
    async def start(self):
        """Start all servers"""
        self._running = True
        
        logger.info("Starting dLNk AI Bridge servers...")
        
        try:
            # Start servers concurrently
            await asyncio.gather(
                self.ws_server.start(),
                self.rest_server.start(),
                self._wait_for_shutdown()
            )
        except asyncio.CancelledError:
            logger.info("Servers cancelled")
    
    async def _wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self._shutdown_event.wait()
    
    async def stop(self):
        """Stop all components gracefully"""
        logger.info("Stopping dLNk AI Bridge...")
        
        self._running = False
        self._shutdown_event.set()
        
        # Stop servers
        if self.ws_server:
            await self.ws_server.stop()
            logger.info("WebSocket Server stopped")
        
        if self.rest_server:
            await self.rest_server.stop()
            logger.info("REST API Server stopped")
        
        # Stop provider manager
        if self.provider_manager:
            await self.provider_manager.close()
            logger.info("Provider Manager closed")
        
        # Stop token manager
        if self.token_manager:
            await self.token_manager.stop()
            logger.info("Token Manager stopped")
        
        # Disconnect gRPC client
        if self.grpc_client:
            await self.grpc_client.disconnect()
            logger.info("gRPC Client disconnected")
        
        logger.info("dLNk AI Bridge stopped")
    
    def get_status(self) -> dict:
        """Get bridge status"""
        return {
            'running': self._running,
            'token_valid': self.token_manager.is_valid() if self.token_manager else False,
            'providers': self.provider_manager.get_status() if self.provider_manager else {},
            'ws_server': self.ws_server.get_stats() if self.ws_server else {},
            'rest_server': self.rest_server.get_stats() if self.rest_server else {}
        }


async def main():
    """Main entry point"""
    bridge = AIBridge()
    
    # Setup signal handlers
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(bridge.stop())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass
    
    try:
        await bridge.initialize()
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
    finally:
        await bridge.stop()


def run():
    """Run the AI Bridge"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║     ██████╗ ██╗     ███╗   ██╗██╗  ██╗                   ║
    ║     ██╔══██╗██║     ████╗  ██║██║ ██╔╝                   ║
    ║     ██║  ██║██║     ██╔██╗ ██║█████╔╝                    ║
    ║     ██║  ██║██║     ██║╚██╗██║██╔═██╗                    ║
    ║     ██████╔╝███████╗██║ ╚████║██║  ██╗                   ║
    ║     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝                   ║
    ║                                                           ║
    ║              AI Bridge - No Limits AI                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())


if __name__ == "__main__":
    run()
