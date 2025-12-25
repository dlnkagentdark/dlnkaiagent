"""
dLNk AI Bridge - Groq Client
============================
Groq API client for fast inference fallback.

Free tier available with rate limits.

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, AsyncIterator

logger = logging.getLogger('GroqClient')


class GroqClient:
    """
    Groq API Client
    
    Features:
    - Ultra-fast inference
    - Free tier support
    - Streaming responses
    - Multiple model support
    """
    
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        timeout: float = 30.0
    ):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key
            model: Model to use
            timeout: Request timeout
        """
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        
        self._http_client = None
        self._is_available = bool(api_key)
        
        # Statistics
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_latency_ms = 0
    
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
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """
        Generate response using Groq API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
        
        Returns:
            Generated text or None if failed
        """
        if not self.api_key:
            logger.warning("Groq API key not configured")
            return None
        
        await self._ensure_client()
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}/chat/completions"
        
        start_time = time.time()
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload, headers=headers) as response:
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.total_latency_ms += elapsed_ms
                
                if response.status == 200:
                    self.success_count += 1
                    result = await response.json()
                    
                    choices = result.get('choices', [])
                    if choices:
                        message = choices[0].get('message', {})
                        return message.get('content', '')
                    
                    return None
                else:
                    self.error_count += 1
                    error_text = await response.text()
                    logger.error(f"Groq error {response.status}: {error_text[:200]}")
                    return None
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Groq exception: {e}")
            return None
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream response from Groq API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
        
        Yields:
            Response text chunks
        """
        if not self.api_key:
            logger.warning("Groq API key not configured")
            return
        
        await self._ensure_client()
        
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.BASE_URL}/chat/completions"
        
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
                    logger.error(f"Groq stream error: {response.status}")
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Groq stream exception: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        avg_latency = (
            self.total_latency_ms / self.success_count 
            if self.success_count > 0 else 0
        )
        
        return {
            'provider': 'groq',
            'model': self.model,
            'available': self._is_available,
            'requests': self.request_count,
            'success': self.success_count,
            'errors': self.error_count,
            'avg_latency_ms': int(avg_latency)
        }
