"""
dLNk AI Bridge - OpenAI Client
==============================
OpenAI API client for fallback.

Supports OpenAI-compatible APIs.

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, AsyncIterator, List

logger = logging.getLogger('OpenAIClient')


class OpenAIClient:
    """
    OpenAI API Client
    
    Features:
    - OpenAI API support
    - OpenAI-compatible API support
    - Streaming responses
    - Multiple model support
    """
    
    DEFAULT_MODEL = "gpt-4.1-mini"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = None,
        timeout: float = 60.0
    ):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            base_url: API base URL (for compatible APIs)
            model: Model to use
            timeout: Request timeout
        """
        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip('/')
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        
        self._http_client = None
        self._is_available = bool(api_key)
        
        # Statistics
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
        self.total_tokens = 0
    
    @property
    def is_available(self) -> bool:
        return self._is_available
    
    async def _ensure_client(self):
        """Ensure HTTP client is initialized"""
        if not self._http_client:
            import aiohttp
            self._http_client = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
    
    async def close(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.close()
            self._http_client = None
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        messages: List[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """
        Generate response using OpenAI API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            messages: Optional message history
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
        
        Returns:
            Generated text or None if failed
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return None
        
        await self._ensure_client()
        
        # Build messages
        if messages:
            chat_messages = messages.copy()
        else:
            chat_messages = []
            
            if system_prompt:
                chat_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            chat_messages.append({
                "role": "user",
                "content": prompt
            })
        
        # Build request payload
        payload = {
            "model": self.model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/chat/completions"
        
        start_time = time.time()
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload, headers=headers) as response:
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.total_latency_ms += elapsed_ms
                
                if response.status == 200:
                    self.success_count += 1
                    result = await response.json()
                    
                    # Extract text from response
                    choices = result.get('choices', [])
                    if choices:
                        message = choices[0].get('message', {})
                        content = message.get('content', '')
                        
                        # Track token usage
                        usage = result.get('usage', {})
                        self.total_tokens += usage.get('total_tokens', 0)
                        
                        return content
                    
                    return None
                else:
                    self.error_count += 1
                    error_text = await response.text()
                    logger.error(f"OpenAI error {response.status}: {error_text[:200]}")
                    return None
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"OpenAI exception: {e}")
            return None
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream response from OpenAI API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
        
        Yields:
            Response text chunks
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            return
        
        await self._ensure_client()
        
        # Build messages
        chat_messages = []
        
        if system_prompt:
            chat_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        chat_messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": chat_messages,
            "temperature": temperature,
            "stream": True
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/chat/completions"
        
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    self.success_count += 1
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        
                        if line.startswith('data: '):
                            data = line[6:]
                            
                            if data == '[DONE]':
                                break
                            
                            import json
                            try:
                                chunk = json.loads(data)
                                choices = chunk.get('choices', [])
                                if choices:
                                    delta = choices[0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        yield content
                            except:
                                pass
                else:
                    self.error_count += 1
                    logger.error(f"OpenAI stream error: {response.status}")
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"OpenAI stream exception: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        avg_latency = (
            self.total_latency_ms / self.success_count 
            if self.success_count > 0 else 0
        )
        
        return {
            'provider': 'openai',
            'model': self.model,
            'base_url': self.base_url,
            'available': self._is_available,
            'requests': self.request_count,
            'success': self.success_count,
            'errors': self.error_count,
            'avg_latency_ms': int(avg_latency),
            'total_tokens': self.total_tokens
        }
