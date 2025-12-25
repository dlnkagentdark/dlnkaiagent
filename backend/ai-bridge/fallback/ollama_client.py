"""
dLNk AI Bridge - Ollama Client
==============================
Ollama client for local LLM inference.

Offline fallback option.

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any, AsyncIterator

logger = logging.getLogger('OllamaClient')


class OllamaClient:
    """
    Ollama Client for Local LLM
    
    Features:
    - Local inference (offline capable)
    - Streaming responses
    - Multiple model support
    - No API key required
    """
    
    DEFAULT_MODEL = "llama3.2"
    DEFAULT_ENDPOINT = "http://localhost:11434"
    
    def __init__(
        self,
        endpoint: str = None,
        model: str = None,
        timeout: float = 120.0
    ):
        """
        Initialize Ollama client
        
        Args:
            endpoint: Ollama server endpoint
            model: Model to use
            timeout: Request timeout (longer for local inference)
        """
        self.endpoint = (endpoint or self.DEFAULT_ENDPOINT).rstrip('/')
        self.model = model or self.DEFAULT_MODEL
        self.timeout = timeout
        
        self._http_client = None
        self._is_available = False
        
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
    
    async def check_availability(self) -> bool:
        """
        Check if Ollama server is available
        
        Returns:
            True if server is reachable
        """
        await self._ensure_client()
        
        try:
            url = f"{self.endpoint}/api/tags"
            async with self._http_client.get(url) as response:
                self._is_available = response.status == 200
                
                if self._is_available:
                    data = await response.json()
                    models = [m.get('name') for m in data.get('models', [])]
                    logger.info(f"Ollama available with models: {models}")
                
                return self._is_available
                
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            self._is_available = False
            return False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """
        Generate response using Ollama
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
        
        Returns:
            Generated text or None if failed
        """
        await self._ensure_client()
        
        # Check availability first
        if not self._is_available:
            await self.check_availability()
            if not self._is_available:
                return None
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        url = f"{self.endpoint}/api/generate"
        
        start_time = time.time()
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload) as response:
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.total_latency_ms += elapsed_ms
                
                if response.status == 200:
                    self.success_count += 1
                    result = await response.json()
                    return result.get('response', '')
                else:
                    self.error_count += 1
                    error_text = await response.text()
                    logger.error(f"Ollama error {response.status}: {error_text[:200]}")
                    return None
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Ollama exception: {e}")
            self._is_available = False
            return None
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """
        Stream response from Ollama
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
        
        Yields:
            Response text chunks
        """
        await self._ensure_client()
        
        if not self._is_available:
            await self.check_availability()
            if not self._is_available:
                return
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        url = f"{self.endpoint}/api/generate"
        
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload) as response:
                if response.status == 200:
                    self.success_count += 1
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line:
                            import json
                            try:
                                data = json.loads(line)
                                text = data.get('response', '')
                                if text:
                                    yield text
                                
                                if data.get('done', False):
                                    break
                            except:
                                pass
                else:
                    self.error_count += 1
                    logger.error(f"Ollama stream error: {response.status}")
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Ollama stream exception: {e}")
            self._is_available = False
    
    async def chat(
        self,
        messages: list,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Chat completion using Ollama chat API
        
        Args:
            messages: List of message dicts with role and content
            temperature: Sampling temperature
        
        Returns:
            Generated text or None if failed
        """
        await self._ensure_client()
        
        if not self._is_available:
            await self.check_availability()
            if not self._is_available:
                return None
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        url = f"{self.endpoint}/api/chat"
        
        start_time = time.time()
        self.request_count += 1
        
        try:
            async with self._http_client.post(url, json=payload) as response:
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.total_latency_ms += elapsed_ms
                
                if response.status == 200:
                    self.success_count += 1
                    result = await response.json()
                    message = result.get('message', {})
                    return message.get('content', '')
                else:
                    self.error_count += 1
                    return None
                    
        except Exception as e:
            self.error_count += 1
            logger.error(f"Ollama chat exception: {e}")
            return None
    
    async def list_models(self) -> list:
        """
        List available models
        
        Returns:
            List of model names
        """
        await self._ensure_client()
        
        try:
            url = f"{self.endpoint}/api/tags"
            async with self._http_client.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return [m.get('name') for m in data.get('models', [])]
                return []
        except:
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics"""
        avg_latency = (
            self.total_latency_ms / self.success_count 
            if self.success_count > 0 else 0
        )
        
        return {
            'provider': 'ollama',
            'model': self.model,
            'endpoint': self.endpoint,
            'available': self._is_available,
            'requests': self.request_count,
            'success': self.success_count,
            'errors': self.error_count,
            'avg_latency_ms': int(avg_latency)
        }
