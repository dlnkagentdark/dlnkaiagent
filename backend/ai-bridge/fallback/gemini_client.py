"""
dLNk AI Bridge - Gemini Client
==============================
Google Gemini API client for fallback.

Free tier limits (as of Dec 2024):
- gemini-2.0-flash-exp: ~20-250 requests/day
- gemini-1.5-flash: ~15 RPM, 1500 RPD

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, AsyncIterator

logger = logging.getLogger('GeminiClient')


class GeminiClient:
    """
    Google Gemini API Client
    
    Features:
    - Free tier support
    - Streaming responses
    - Safety settings bypass
    - Multiple model support
    """
    
    DEFAULT_MODEL = "gemini-2.0-flash-exp"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        timeout: float = 60.0
    ):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key
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
        max_tokens: int = 8192
    ) -> Optional[str]:
        """
        Generate response using Gemini API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
        
        Returns:
            Generated text or None if failed
        """
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return None
        
        await self._ensure_client()
        
        # Prepare prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
        
        # Build request payload
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        url = f"{self.BASE_URL}/{self.model}:generateContent?key={self.api_key}"
        
        start_time = time.time()
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload) as response:
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.total_latency_ms += elapsed_ms
                
                if response.status == 200:
                    self.success_count += 1
                    result = await response.json()
                    
                    # Extract text from response
                    candidates = result.get('candidates', [])
                    if candidates:
                        content = candidates[0].get('content', {})
                        parts = content.get('parts', [])
                        if parts:
                            return parts[0].get('text', '')
                    
                    return None
                else:
                    self.error_count += 1
                    error_text = await response.text()
                    logger.error(f"Gemini error {response.status}: {error_text[:200]}")
                    return None
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Gemini exception: {e}")
            return None
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream response from Gemini API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
        
        Yields:
            Response text chunks
        """
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return
        
        await self._ensure_client()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 8192
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        url = f"{self.BASE_URL}/{self.model}:streamGenerateContent?key={self.api_key}"
        
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload) as response:
                if response.status == 200:
                    self.success_count += 1
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            import json
                            try:
                                data = json.loads(line[6:])
                                candidates = data.get('candidates', [])
                                if candidates:
                                    content = candidates[0].get('content', {})
                                    parts = content.get('parts', [])
                                    if parts:
                                        text = parts[0].get('text', '')
                                        if text:
                                            yield text
                            except:
                                pass
                else:
                    self.error_count += 1
                    logger.error(f"Gemini stream error: {response.status}")
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Gemini stream exception: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        avg_latency = (
            self.total_latency_ms / self.success_count 
            if self.success_count > 0 else 0
        )
        
        return {
            'provider': 'gemini',
            'model': self.model,
            'available': self._is_available,
            'requests': self.request_count,
            'success': self.success_count,
            'errors': self.error_count,
            'avg_latency_ms': int(avg_latency)
        }
