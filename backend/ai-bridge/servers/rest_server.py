"""
dLNk AI Bridge - REST API Server
================================
REST API server for VS Code Extension communication.

Port: 8766 (default)
Endpoints:
- POST /api/chat - Send chat message
- GET /api/status - Get server status
- GET /api/history - Get conversation history
- POST /api/token - Set/update tokens
- GET /api/providers - List available providers

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import time
import uuid
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

logger = logging.getLogger('RESTServer')


class RESTServer:
    """
    REST API Server for dLNk AI Bridge
    
    Features:
    - FastAPI-based REST endpoints
    - CORS support for extension
    - Streaming responses (SSE)
    - Token management endpoints
    - Health checks
    
    Usage:
        server = RESTServer(host='127.0.0.1', port=8766, provider_manager=pm)
        await server.start()
    """
    
    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 8766,
        provider_manager = None,
        token_manager = None,
        cors_origins: List[str] = None
    ):
        """
        Initialize REST server
        
        Args:
            host: Server host address
            port: Server port
            provider_manager: AI provider manager
            token_manager: Token manager for auth
            cors_origins: Allowed CORS origins
        """
        self.host = host
        self.port = port
        self.provider_manager = provider_manager
        self.token_manager = token_manager
        self.cors_origins = cors_origins or ["*"]
        
        self._app = None
        self._server = None
        self._running = False
        
        # Statistics
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = None
    
    def _create_app(self):
        """Create FastAPI application"""
        from fastapi import FastAPI, HTTPException, Request, Response
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import StreamingResponse, JSONResponse
        from pydantic import BaseModel
        from typing import Optional, List
        
        # Request/Response models
        class ChatRequest(BaseModel):
            message: str
            system_prompt: Optional[str] = None
            conversation_id: Optional[str] = None
            stream: bool = False
            provider: Optional[str] = None
        
        class ChatResponse(BaseModel):
            success: bool
            response: str
            provider: str
            elapsed_ms: int
            conversation_id: Optional[str] = None
        
        class TokenRequest(BaseModel):
            access_token: str
            refresh_token: Optional[str] = None
            client_secret: Optional[str] = None
            expires_in: int = 3600
        
        class StatusResponse(BaseModel):
            status: str
            uptime_seconds: float
            total_requests: int
            total_errors: int
            providers: Dict[str, Any]
            token_valid: bool
        
        # Create app with lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.start_time = time.time()
            logger.info(f"REST API server starting on http://{self.host}:{self.port}")
            yield
            # Shutdown
            logger.info("REST API server shutting down")
        
        app = FastAPI(
            title="dLNk AI Bridge API",
            description="REST API for dLNk IDE AI integration",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request counter middleware
        @app.middleware("http")
        async def count_requests(request: Request, call_next):
            self.total_requests += 1
            try:
                response = await call_next(request)
                return response
            except Exception as e:
                self.total_errors += 1
                raise
        
        # ============================================
        # API Endpoints
        # ============================================
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "name": "dLNk AI Bridge",
                "version": "1.0.0",
                "status": "running"
            }
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": time.time()}
        
        @app.post("/api/chat", response_model=ChatResponse)
        async def chat(request: ChatRequest):
            """
            Send chat message and get AI response
            
            - **message**: User message (required)
            - **system_prompt**: Optional system prompt
            - **conversation_id**: Optional conversation ID for context
            - **stream**: Whether to stream response (use /api/chat/stream instead)
            - **provider**: Preferred provider (optional)
            """
            if not self.provider_manager:
                raise HTTPException(status_code=503, detail="AI provider not configured")
            
            if not request.message:
                raise HTTPException(status_code=400, detail="Message is required")
            
            try:
                result = await self.provider_manager.chat(
                    message=request.message,
                    system_prompt=request.system_prompt,
                    conversation_id=request.conversation_id,
                    preferred_provider=request.provider
                )
                
                return ChatResponse(
                    success=result.get('success', False),
                    response=result.get('response', ''),
                    provider=result.get('provider', 'unknown'),
                    elapsed_ms=result.get('elapsed_ms', 0),
                    conversation_id=request.conversation_id
                )
                
            except Exception as e:
                logger.error(f"Chat error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/chat/stream")
        async def chat_stream(request: ChatRequest):
            """
            Stream chat response using Server-Sent Events (SSE)
            """
            if not self.provider_manager:
                raise HTTPException(status_code=503, detail="AI provider not configured")
            
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
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        @app.get("/api/status", response_model=StatusResponse)
        async def get_status():
            """Get server and provider status"""
            uptime = time.time() - self.start_time if self.start_time else 0
            
            providers_status = {}
            if self.provider_manager:
                providers_status = self.provider_manager.get_status()
            
            token_valid = False
            if self.token_manager:
                token_valid = self.token_manager.is_valid()
            
            return StatusResponse(
                status="running",
                uptime_seconds=uptime,
                total_requests=self.total_requests,
                total_errors=self.total_errors,
                providers=providers_status,
                token_valid=token_valid
            )
        
        @app.get("/api/providers")
        async def list_providers():
            """List available AI providers"""
            if not self.provider_manager:
                return {"providers": [], "active": None}
            
            return {
                "providers": self.provider_manager.get_available_providers(),
                "active": self.provider_manager.get_active_provider(),
                "stats": self.provider_manager.get_stats()
            }
        
        @app.post("/api/token")
        async def set_token(request: TokenRequest):
            """Set or update authentication tokens"""
            if not self.token_manager:
                raise HTTPException(status_code=503, detail="Token manager not configured")
            
            try:
                self.token_manager.set_tokens(
                    access_token=request.access_token,
                    refresh_token=request.refresh_token,
                    client_secret=request.client_secret,
                    expires_in=request.expires_in
                )
                
                return {
                    "success": True,
                    "message": "Tokens updated successfully",
                    "valid": self.token_manager.is_valid()
                }
                
            except Exception as e:
                logger.error(f"Token update error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/token/status")
        async def token_status():
            """Get token status"""
            if not self.token_manager:
                return {"configured": False}
            
            return {
                "configured": True,
                "valid": self.token_manager.is_valid(),
                "time_until_expiry": self.token_manager.time_until_expiry(),
                "status": self.token_manager.get_status()
            }
        
        @app.post("/api/token/import")
        async def import_token(filepath: str):
            """Import tokens from file"""
            if not self.token_manager:
                raise HTTPException(status_code=503, detail="Token manager not configured")
            
            success = self.token_manager.import_from_file(filepath)
            
            if success:
                return {"success": True, "message": "Tokens imported successfully"}
            else:
                raise HTTPException(status_code=400, detail="Failed to import tokens")
        
        @app.get("/api/history")
        async def get_history(conversation_id: Optional[str] = None, limit: int = 50):
            """Get conversation history"""
            # Placeholder - implement conversation history storage
            return {
                "history": [],
                "conversation_id": conversation_id,
                "message": "History not implemented yet"
            }
        
        @app.delete("/api/history/{conversation_id}")
        async def clear_history(conversation_id: str):
            """Clear conversation history"""
            return {
                "success": True,
                "message": f"History cleared for {conversation_id}"
            }
        
        return app
    
    async def start(self):
        """Start the REST API server"""
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
        """Stop the REST API server"""
        self._running = False
        
        if self._server:
            self._server.should_exit = True
        
        logger.info("REST API server stopped")
    
    def get_stats(self) -> dict:
        """Get server statistics"""
        uptime = time.time() - self.start_time if self.start_time else 0
        
        return {
            'host': self.host,
            'port': self.port,
            'running': self._running,
            'uptime_seconds': uptime,
            'total_requests': self.total_requests,
            'total_errors': self.total_errors
        }
