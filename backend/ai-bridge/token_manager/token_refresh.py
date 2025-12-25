"""
dLNk AI Bridge - Token Manager with Auto-Refresh
================================================
Manages OAuth tokens with automatic refresh before expiry.

Based on: /source-files/dlnk_core/token_harvester.py

Author: dLNk Team (AI-05)
Version: 1.0.0
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from pathlib import Path

from .token_store import TokenStore

logger = logging.getLogger('TokenManager')


# Google OAuth Configuration
GOOGLE_CLIENT_ID = "1090535352638-q5m3558i87588pnd64fjm614un18k0id.apps.googleusercontent.com"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


class TokenManager:
    """
    Token Manager with Auto-Refresh
    
    Features:
    - Automatic token refresh before expiry
    - Background refresh task
    - Token validation
    - Multiple token source support
    - Event callbacks for token changes
    
    Usage:
        manager = TokenManager(config)
        await manager.start()
        token = await manager.get_token()
        await manager.stop()
    """
    
    def __init__(
        self,
        config = None,
        storage_path: Path = None,
        refresh_interval: int = 55 * 60,  # 55 minutes
        refresh_buffer: int = 5 * 60  # 5 minutes before expiry
    ):
        """
        Initialize Token Manager
        
        Args:
            config: Configuration object
            storage_path: Path for token storage
            refresh_interval: Interval for refresh checks (seconds)
            refresh_buffer: Buffer time before expiry to trigger refresh
        """
        self.config = config
        self.refresh_interval = refresh_interval
        self.refresh_buffer = refresh_buffer
        
        # Initialize token store
        storage = storage_path
        if config and hasattr(config, 'TOKEN_STORAGE_PATH'):
            storage = config.TOKEN_STORAGE_PATH
        
        encryption_key = None
        if config and hasattr(config, 'ENCRYPTION_KEY'):
            encryption_key = config.ENCRYPTION_KEY
        
        self.store = TokenStore(
            storage_path=storage,
            encryption_key=encryption_key
        )
        
        # State
        self._refresh_task: Optional[asyncio.Task] = None
        self._running = False
        self._last_refresh: Optional[float] = None
        
        # Callbacks
        self._on_token_refresh: Optional[Callable] = None
        self._on_token_error: Optional[Callable] = None
        
        # Client secret for refresh
        self._client_secret: Optional[str] = None
    
    async def start(self):
        """Start the token manager and background refresh task"""
        if self._running:
            return
        
        self._running = True
        
        # Load client secret if available
        self._client_secret = self.store.get_token('client_secret')
        
        # Start background refresh task
        self._refresh_task = asyncio.create_task(self._refresh_loop())
        
        logger.info("Token Manager started")
        logger.info(f"Access token valid: {self.is_valid()}")
        logger.info(f"Refresh token available: {self.store.is_valid('refresh')}")
    
    async def stop(self):
        """Stop the token manager"""
        self._running = False
        
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            self._refresh_task = None
        
        logger.info("Token Manager stopped")
    
    async def get_token(self) -> Optional[str]:
        """
        Get a valid access token
        
        If the current token is expired or about to expire,
        attempts to refresh it first.
        
        Returns:
            Valid access token or None
        """
        # Check if token needs refresh
        time_until_expiry = self.store.time_until_expiry('access')
        
        if time_until_expiry < self.refresh_buffer:
            logger.info("Token expiring soon, attempting refresh...")
            await self.refresh_token()
        
        return self.store.get_token('access')
    
    def is_valid(self) -> bool:
        """Check if access token is valid"""
        return self.store.is_valid('access')
    
    def get_expiry(self) -> Optional[float]:
        """Get access token expiry timestamp"""
        return self.store.get_expiry('access')
    
    def time_until_expiry(self) -> float:
        """Get seconds until access token expires"""
        return self.store.time_until_expiry('access')
    
    async def refresh_token(self) -> bool:
        """
        Refresh the access token using refresh token
        
        Returns:
            True if refresh successful
        """
        refresh_token = self.store.get_token('refresh')
        
        if not refresh_token:
            logger.warning("No refresh token available")
            return False
        
        if not self._client_secret:
            logger.warning("No client secret available for refresh")
            return False
        
        try:
            import aiohttp
            
            payload = {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": self._client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GOOGLE_TOKEN_URL,
                    data=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Store new access token
                        access_token = data.get('access_token')
                        expires_in = data.get('expires_in', 3600)
                        
                        self.store.set_token('access', access_token, expires_in)
                        
                        # Update refresh token if provided
                        if 'refresh_token' in data:
                            self.store.set_token(
                                'refresh',
                                data['refresh_token'],
                                expires_in=30*24*3600
                            )
                        
                        self._last_refresh = time.time()
                        logger.info("Token refreshed successfully")
                        
                        if self._on_token_refresh:
                            await self._on_token_refresh()
                        
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Token refresh failed: {response.status} - {error_text}")
                        
                        if self._on_token_error:
                            await self._on_token_error(f"Refresh failed: {response.status}")
                        
                        return False
                        
        except Exception as e:
            logger.error(f"Token refresh exception: {e}")
            
            if self._on_token_error:
                await self._on_token_error(str(e))
            
            return False
    
    async def _refresh_loop(self):
        """Background task to refresh token periodically"""
        while self._running:
            try:
                # Wait for refresh interval
                await asyncio.sleep(self.refresh_interval)
                
                if not self._running:
                    break
                
                # Check if refresh needed
                time_until_expiry = self.store.time_until_expiry('access')
                
                if time_until_expiry < self.refresh_buffer:
                    logger.info("Scheduled token refresh...")
                    await self.refresh_token()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in refresh loop: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    def set_tokens(
        self,
        access_token: str,
        refresh_token: str = None,
        client_secret: str = None,
        expires_in: int = 3600
    ):
        """
        Set tokens manually
        
        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            client_secret: Client secret for refresh
            expires_in: Access token expiry in seconds
        """
        self.store.set_token('access', access_token, expires_in)
        
        if refresh_token:
            self.store.set_token('refresh', refresh_token, expires_in=30*24*3600)
        
        if client_secret:
            self.store.set_token('client_secret', client_secret, expires_in=365*24*3600)
            self._client_secret = client_secret
        
        logger.info("Tokens set manually")
    
    def import_from_file(self, filepath: str) -> bool:
        """
        Import tokens from file
        
        Args:
            filepath: Path to token JSON file
        
        Returns:
            True if import successful
        """
        success = self.store.import_from_file(filepath)
        
        if success:
            # Update client secret reference
            self._client_secret = self.store.get_token('client_secret')
        
        return success
    
    def export_to_file(self, filepath: str) -> bool:
        """
        Export tokens to file
        
        Args:
            filepath: Output file path
        
        Returns:
            True if export successful
        """
        return self.store.export_to_file(filepath, include_secrets=True)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get token manager status
        
        Returns:
            Status dictionary
        """
        return {
            'running': self._running,
            'access_token_valid': self.is_valid(),
            'refresh_token_valid': self.store.is_valid('refresh'),
            'time_until_expiry': self.time_until_expiry(),
            'last_refresh': self._last_refresh,
            'tokens': self.store.list_tokens()
        }
    
    # Event handlers
    def on_token_refresh(self, callback: Callable):
        """Set callback for successful token refresh"""
        self._on_token_refresh = callback
    
    def on_token_error(self, callback: Callable):
        """Set callback for token errors"""
        self._on_token_error = callback
