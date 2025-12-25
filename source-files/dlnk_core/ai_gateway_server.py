#!/usr/bin/env python3
"""
dLNk AI Gateway Server
======================
Unified AI Gateway ที่รวม providers ทั้งหมดเข้าด้วยกัน

Features:
- REST API compatible with OpenAI format
- Multi-provider fallback (dLNk AI → Gemini → Ollama → Offline)
- Token management integration
- Rate limiting and load balancing
- WebSocket support for streaming

Author: dLNk Team
Version: 1.0.0
"""

import os
import sys
import json
import time
import asyncio
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Request, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import StreamingResponse, JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Please install: pip install fastapi uvicorn pydantic")
    sys.exit(1)

# Local imports
try:
    from dlnk_dlnk_ai_bridge import DLNKdLNk AIBridge, TokenManager
    from dlnk_ai_bridge_real import DLNKAIBridgeReal
except ImportError:
    # Fallback if running standalone
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-Gateway')


# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    'host': '0.0.0.0',
    'port': 8000,
    'api_prefix': '/v1',
    'max_tokens_default': 4096,
    'temperature_default': 0.7,
    'rate_limit_rpm': 60,
    'rate_limit_rpd': 1000,
    'enable_streaming': True,
    'enable_logging': True
}


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "dlnk-ai"
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: Optional[bool] = False
    user: Optional[str] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str

class ModelsResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]


# ============================================
# RATE LIMITER
# ============================================

class RateLimiter:
    """Simple rate limiter"""
    
    def __init__(self, rpm: int = 60, rpd: int = 1000):
        self.rpm = rpm
        self.rpd = rpd
        self.minute_requests: Dict[str, List[float]] = {}
        self.day_requests: Dict[str, List[float]] = {}
    
    def check(self, user_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        minute_ago = now - 60
        day_ago = now - 86400
        
        # Clean old entries
        if user_id in self.minute_requests:
            self.minute_requests[user_id] = [
                t for t in self.minute_requests[user_id] if t > minute_ago
            ]
        if user_id in self.day_requests:
            self.day_requests[user_id] = [
                t for t in self.day_requests[user_id] if t > day_ago
            ]
        
        # Check limits
        minute_count = len(self.minute_requests.get(user_id, []))
        day_count = len(self.day_requests.get(user_id, []))
        
        if minute_count >= self.rpm:
            return False
        if day_count >= self.rpd:
            return False
        
        return True
    
    def record(self, user_id: str):
        """Record a request"""
        now = time.time()
        
        if user_id not in self.minute_requests:
            self.minute_requests[user_id] = []
        if user_id not in self.day_requests:
            self.day_requests[user_id] = []
        
        self.minute_requests[user_id].append(now)
        self.day_requests[user_id].append(now)


# ============================================
# AI PROVIDER MANAGER
# ============================================

class AIProviderManager:
    """
    Manages multiple AI providers with fallback
    
    Priority:
    1. dLNk AI gRPC (free, no limits with token)
    2. Gemini API (free tier with limits)
    3. OpenAI-compatible (paid)
    4. Ollama (local)
    5. Offline mode
    """
    
    def __init__(self):
        self.providers = []
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'provider_usage': {}
        }
        
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available providers"""
        # Try to import and init each provider
        
        # 1. dLNk AI Bridge
        try:
            from dlnk_dlnk_ai_bridge import DLNKdLNk AIBridge
            bridge = DLNKdLNk AIBridge()
            if bridge.get_available_providers():
                self.providers.append({
                    'name': 'dlnk_ai',
                    'instance': bridge,
                    'priority': 1,
                    'available': True
                })
                logger.info("dLNk AI provider initialized")
        except Exception as e:
            logger.warning(f"dLNk AI provider not available: {e}")
        
        # 2. Real AI Bridge (OpenAI/Groq/Ollama)
        try:
            from dlnk_ai_bridge_real import DLNKAIBridgeReal
            bridge = DLNKAIBridgeReal()
            if bridge.get_available_providers():
                self.providers.append({
                    'name': 'openai_compatible',
                    'instance': bridge,
                    'priority': 2,
                    'available': True
                })
                logger.info(f"OpenAI-compatible providers: {bridge.get_available_providers()}")
        except Exception as e:
            logger.warning(f"OpenAI-compatible providers not available: {e}")
        
        # 3. Direct Gemini (if not already in bridge)
        gemini_key = os.environ.get('GEMINI_API_KEY')
        if gemini_key:
            self.providers.append({
                'name': 'gemini_direct',
                'api_key': gemini_key,
                'priority': 3,
                'available': True
            })
            logger.info("Gemini direct provider initialized")
        
        # Sort by priority
        self.providers.sort(key=lambda x: x['priority'])
        
        logger.info(f"Total providers available: {len(self.providers)}")
    
    async def generate(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Generate response using available providers"""
        self.stats['total_requests'] += 1
        
        for provider in self.providers:
            if not provider['available']:
                continue
            
            provider_name = provider['name']
            
            try:
                if provider_name == 'dlnk_ai':
                    # Use dLNk AI Bridge
                    bridge = provider['instance']
                    prompt = messages[-1]['content'] if messages else ""
                    result = await bridge.chat(prompt, **kwargs)
                    
                    if result['success']:
                        self._record_usage(provider_name)
                        return {
                            'success': True,
                            'response': result['response'],
                            'provider': f"dlnk_ai/{result['provider']}"
                        }
                
                elif provider_name == 'openai_compatible':
                    # Use Real AI Bridge
                    bridge = provider['instance']
                    prompt = messages[-1]['content'] if messages else ""
                    result = await bridge.chat(prompt, **kwargs)
                    
                    if result['success']:
                        self._record_usage(provider_name)
                        return {
                            'success': True,
                            'response': result['response'],
                            'provider': f"openai/{result['provider']}"
                        }
                
                elif provider_name == 'gemini_direct':
                    # Direct Gemini call
                    result = await self._call_gemini_direct(
                        messages, 
                        provider['api_key'],
                        **kwargs
                    )
                    
                    if result:
                        self._record_usage(provider_name)
                        return {
                            'success': True,
                            'response': result,
                            'provider': 'gemini_direct'
                        }
                        
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                continue
        
        # All providers failed
        return {
            'success': False,
            'response': "⚠️ All AI providers are currently unavailable. Please try again later.",
            'provider': 'offline'
        }
    
    async def _call_gemini_direct(self, messages: List[Dict], api_key: str, **kwargs) -> Optional[str]:
        """Direct Gemini API call"""
        try:
            import requests
            
            # Build prompt from messages
            prompt_parts = []
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                prompt_parts.append(f"{role}: {content}")
            
            full_prompt = "\n".join(prompt_parts)
            
            payload = {
                "contents": [{
                    "role": "user",
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "maxOutputTokens": kwargs.get('max_tokens', 4096)
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            }
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                return text
            
            return None
            
        except Exception as e:
            logger.error(f"Gemini direct error: {e}")
            return None
    
    def _record_usage(self, provider_name: str):
        """Record provider usage"""
        self.stats['successful_requests'] += 1
        if provider_name not in self.stats['provider_usage']:
            self.stats['provider_usage'][provider_name] = 0
        self.stats['provider_usage'][provider_name] += 1
    
    def get_stats(self) -> Dict:
        """Get provider statistics"""
        return {
            **self.stats,
            'available_providers': [p['name'] for p in self.providers if p['available']]
        }
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        models = ['dlnk-ai', 'dlnk-ai-fast']
        
        for provider in self.providers:
            if provider['name'] == 'dlnk_ai':
                models.append('dlnk_ai-cascade')
            elif provider['name'] == 'gemini_direct':
                models.append('gemini-2.0-flash')
            elif provider['name'] == 'openai_compatible':
                models.extend(['gpt-4.1-mini', 'llama-3.3-70b'])
        
        return list(set(models))


# ============================================
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="dLNk AI Gateway",
    description="Unified AI Gateway - OpenAI-compatible API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
provider_manager: AIProviderManager = None
rate_limiter: RateLimiter = None


@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    global provider_manager, rate_limiter
    
    provider_manager = AIProviderManager()
    rate_limiter = RateLimiter(
        rpm=CONFIG['rate_limit_rpm'],
        rpd=CONFIG['rate_limit_rpd']
    )
    
    logger.info("dLNk AI Gateway started")


# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "dLNk AI Gateway",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health",
            "stats": "/stats"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "providers": provider_manager.get_stats()['available_providers'] if provider_manager else []
    }


@app.get("/stats")
async def stats():
    """Get gateway statistics"""
    if not provider_manager:
        return {"error": "Not initialized"}
    
    return {
        "gateway": provider_manager.get_stats(),
        "timestamp": datetime.now().isoformat()
    }


@app.get(f"{CONFIG['api_prefix']}/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    if not provider_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    models = provider_manager.get_available_models()
    
    return ModelsResponse(
        data=[
            ModelInfo(
                id=model,
                created=int(time.time()),
                owned_by="dlnk"
            )
            for model in models
        ]
    )


@app.post(f"{CONFIG['api_prefix']}/chat/completions")
async def chat_completions(request: ChatCompletionRequest, req: Request):
    """
    Chat completions endpoint (OpenAI-compatible)
    
    Supports:
    - Standard chat completion
    - Streaming (stream=true)
    - Multiple models
    """
    if not provider_manager:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    # Get user ID for rate limiting
    user_id = request.user or req.client.host or "anonymous"
    
    # Check rate limit
    if not rate_limiter.check(user_id):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later."
        )
    
    # Record request
    rate_limiter.record(user_id)
    
    # Convert messages
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    # Generate response
    start_time = time.time()
    
    result = await provider_manager.generate(
        messages,
        max_tokens=request.max_tokens or CONFIG['max_tokens_default'],
        temperature=request.temperature or CONFIG['temperature_default']
    )
    
    elapsed = time.time() - start_time
    
    # Build response
    response_id = f"chatcmpl-{hashlib.md5(str(time.time()).encode()).hexdigest()[:24]}"
    
    # Estimate tokens (rough)
    prompt_tokens = sum(len(m.content.split()) for m in request.messages) * 1.3
    completion_tokens = len(result['response'].split()) * 1.3
    
    if request.stream:
        # Streaming response
        async def generate_stream():
            # Send chunks
            words = result['response'].split()
            for i, word in enumerate(words):
                chunk = {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": int(time.time()),
                    "model": request.model,
                    "choices": [{
                        "index": 0,
                        "delta": {"content": word + " "},
                        "finish_reason": None if i < len(words) - 1 else "stop"
                    }]
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.02)  # Simulate streaming
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
    
    # Standard response
    return ChatCompletionResponse(
        id=response_id,
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(
                    role="assistant",
                    content=result['response']
                ),
                finish_reason="stop"
            )
        ],
        usage=ChatCompletionUsage(
            prompt_tokens=int(prompt_tokens),
            completion_tokens=int(completion_tokens),
            total_tokens=int(prompt_tokens + completion_tokens)
        )
    )


# ============================================
# TOKEN MANAGEMENT ENDPOINTS
# ============================================

@app.post("/admin/token/import")
async def import_token(filepath: str):
    """Import token from file"""
    try:
        from dlnk_dlnk_ai_bridge import TokenManager
        manager = TokenManager()
        success = manager.import_from_file(filepath)
        
        return {
            "success": success,
            "message": "Token imported" if success else "Import failed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/token/set")
async def set_token(access_token: str, refresh_token: str = None):
    """Set token manually"""
    try:
        from dlnk_dlnk_ai_bridge import TokenManager
        manager = TokenManager()
        manager.set_tokens(access_token, refresh_token)
        
        return {
            "success": True,
            "message": "Token set successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/admin/token/status")
async def token_status():
    """Get token status"""
    try:
        from dlnk_dlnk_ai_bridge import TokenManager
        manager = TokenManager()
        
        return {
            "valid": manager.is_valid(),
            "has_refresh_token": bool(manager.refresh_token)
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================
# MAIN
# ============================================

def run_server(host: str = None, port: int = None):
    """Run the gateway server"""
    host = host or CONFIG['host']
    port = port or CONFIG['port']
    
    print("=" * 60)
    print("dLNk AI Gateway Server")
    print("=" * 60)
    print(f"Starting on http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/docs")
    print("=" * 60)
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="dLNk AI Gateway Server")
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    
    args = parser.parse_args()
    run_server(args.host, args.port)
