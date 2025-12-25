"""
dLNk AI Bridge - Jetski API Client
==================================
Alternative client for Jetski API (dLNk AI variant).

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import uuid
import time
from typing import Optional, Dict, Any, AsyncIterator
from dataclasses import dataclass

logger = logging.getLogger('JetskiClient')


@dataclass
class JetskiResponse:
    """Response from Jetski API"""
    content: str
    model: str = 'jetski'
    finish_reason: str = 'stop'
    elapsed_ms: int = 0


class JetskiClient:
    """
    Client for Jetski API
    
    Jetski is an alternative endpoint that may use different
    authentication or protocol variants.
    
    Features:
    - REST API support
    - Streaming responses
    - Token management
    """
    
    DEFAULT_ENDPOINT = "https://jetski.googleapis.com/v1/chat"
    
    def __init__(
        self,
        endpoint: str = None,
        token_manager = None,
        timeout: float = 30.0
    ):
        """
        Initialize Jetski client
        
        Args:
            endpoint: API endpoint URL
            token_manager: TokenManager instance
            timeout: Request timeout
        """
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        self.token_manager = token_manager
        self.timeout = timeout
        
        self._http_client = None
        self._connected = False
        
        # Stats
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
    
    async def connect(self) -> bool:
        """Initialize HTTP client"""
        try:
            import httpx
            
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout)
            )
            self._connected = True
            logger.info(f"Jetski client connected: {self.endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Jetski connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        self._connected = False
        logger.info("Jetski client disconnected")
    
    def is_connected(self) -> bool:
        return self._connected and self._http_client is not None
    
    async def chat(
        self,
        message: str,
        system_prompt: str = None,
        conversation_id: str = None
    ) -> JetskiResponse:
        """
        Send chat message to Jetski API
        
        Args:
            message: User message
            system_prompt: Optional system prompt
            conversation_id: Optional conversation ID
        
        Returns:
            JetskiResponse with AI response
        """
        if not self.is_connected():
            await self.connect()
        
        if not self.token_manager:
            raise RuntimeError("Token manager not configured")
        
        access_token = await self.token_manager.get_token()
        if not access_token:
            raise RuntimeError("No valid access token")
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Build request payload
        payload = {
            "messages": [
                {"role": "user", "content": message}
            ],
            "conversation_id": conversation_id
        }
        
        if system_prompt:
            payload["messages"].insert(0, {
                "role": "system",
                "content": system_prompt
            })
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        start_time = time.time()
        self.request_count += 1
        
        try:
            response = await self._http_client.post(
                self.endpoint,
                json=payload,
                headers=headers
            )
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                self.success_count += 1
                data = response.json()
                
                content = data.get('response', '')
                if not content and 'choices' in data:
                    content = data['choices'][0].get('message', {}).get('content', '')
                
                return JetskiResponse(
                    content=content,
                    model=data.get('model', 'jetski'),
                    elapsed_ms=elapsed_ms
                )
            else:
                self.error_count += 1
                raise RuntimeError(f"Jetski error: HTTP {response.status_code}")
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"Jetski request failed: {e}")
            raise
    
    async def chat_stream(
        self,
        message: str,
        system_prompt: str = None
    ) -> AsyncIterator[str]:
        """
        Stream chat response from Jetski
        
        Args:
            message: User message
            system_prompt: Optional system prompt
        
        Yields:
            Response text chunks
        """
        if not self.is_connected():
            await self.connect()
        
        if not self.token_manager:
            raise RuntimeError("Token manager not configured")
        
        access_token = await self.token_manager.get_token()
        
        payload = {
            "messages": [{"role": "user", "content": message}],
            "stream": True
        }
        
        if system_prompt:
            payload["messages"].insert(0, {
                "role": "system",
                "content": system_prompt
            })
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        self.request_count += 1
        
        try:
            async with self._http_client.stream(
                "POST",
                self.endpoint,
                json=payload,
                headers=headers
            ) as response:
                if response.status_code == 200:
                    self.success_count += 1
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data != "[DONE]":
                                import json
                                try:
                                    chunk = json.loads(data)
                                    content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                                    if content:
                                        yield content
                                except:
                                    pass
                else:
                    self.error_count += 1
                    raise RuntimeError(f"Jetski stream error: HTTP {response.status_code}")
                    
        except Exception as e:
            self.error_count += 1
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        return {
            'endpoint': self.endpoint,
            'connected': self._connected,
            'requests': self.request_count,
            'success': self.success_count,
            'errors': self.error_count
        }
