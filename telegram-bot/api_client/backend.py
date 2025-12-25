"""
dLNk Telegram Bot - Backend API Client

This module provides a client for communicating with the dLNk backend API.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

import httpx

from config import APIConfig

logger = logging.getLogger(__name__)


class BackendAPIClient:
    """
    Client for dLNk Backend API.
    
    Provides methods for:
    - User management
    - License management
    - System status
    - Logs retrieval
    - Statistics
    """
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        timeout: int = None
    ):
        """
        Initialize the API client.
        
        Args:
            base_url: Backend API base URL
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = (base_url or APIConfig.BACKEND_URL).rstrip('/')
        self.api_key = api_key or APIConfig.API_KEY
        self.timeout = timeout or APIConfig.API_TIMEOUT
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "dLNk-TelegramBot/1.0"
                }
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            Response data as dict
        """
        client = await self._get_client()
        
        try:
            response = await client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise APIError(f"API request failed: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise APIError(f"Request failed: {e}")
    
    # ==========================================
    # System Status
    # ==========================================
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status.
        
        Returns:
            System status dict
        """
        try:
            return await self._request("GET", "/api/status")
        except APIError:
            # Return mock data if API unavailable
            return {
                "status": "unknown",
                "services": {
                    "ai_bridge": "unknown",
                    "license_server": "unknown",
                    "admin_console": "unknown"
                },
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_health(self) -> Dict[str, Any]:
        """
        Get system health metrics.
        
        Returns:
            Health metrics dict
        """
        try:
            return await self._request("GET", "/api/health")
        except APIError:
            return {
                "healthy": False,
                "message": "Unable to connect to backend"
            }
    
    # ==========================================
    # User Management
    # ==========================================
    
    async def get_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: str = None
    ) -> Dict[str, Any]:
        """
        Get list of users.
        
        Args:
            page: Page number
            limit: Items per page
            search: Search query
            
        Returns:
            Users list with pagination
        """
        params = {"page": page, "limit": limit}
        if search:
            params["search"] = search
        
        try:
            return await self._request("GET", "/api/users", params=params)
        except APIError:
            return {"users": [], "total": 0, "page": page}
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user details.
        
        Args:
            user_id: User ID
            
        Returns:
            User details or None
        """
        try:
            return await self._request("GET", f"/api/users/{user_id}")
        except APIError:
            return None
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Returns:
            User statistics dict
        """
        try:
            return await self._request("GET", "/api/users/stats")
        except APIError:
            return {
                "total": 0,
                "active_7d": 0,
                "active_30d": 0,
                "new_7d": 0
            }
    
    async def ban_user(self, user_id: str, reason: str = None) -> bool:
        """
        Ban a user.
        
        Args:
            user_id: User ID to ban
            reason: Ban reason
            
        Returns:
            True if successful
        """
        try:
            await self._request(
                "POST",
                f"/api/users/{user_id}/ban",
                json={"reason": reason}
            )
            return True
        except APIError:
            return False
    
    async def unban_user(self, user_id: str) -> bool:
        """
        Unban a user.
        
        Args:
            user_id: User ID to unban
            
        Returns:
            True if successful
        """
        try:
            await self._request("POST", f"/api/users/{user_id}/unban")
            return True
        except APIError:
            return False
    
    # ==========================================
    # License Management
    # ==========================================
    
    async def get_licenses(
        self,
        page: int = 1,
        limit: int = 20,
        status: str = None,
        search: str = None
    ) -> Dict[str, Any]:
        """
        Get list of licenses.
        
        Args:
            page: Page number
            limit: Items per page
            status: Filter by status
            search: Search query
            
        Returns:
            Licenses list with pagination
        """
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        
        try:
            return await self._request("GET", "/api/licenses", params=params)
        except APIError:
            return {"licenses": [], "total": 0, "page": page}
    
    async def get_license(self, license_key: str) -> Optional[Dict[str, Any]]:
        """
        Get license details.
        
        Args:
            license_key: License key
            
        Returns:
            License details or None
        """
        try:
            return await self._request("GET", f"/api/licenses/{license_key}")
        except APIError:
            return None
    
    async def get_license_stats(self) -> Dict[str, Any]:
        """
        Get license statistics.
        
        Returns:
            License statistics dict
        """
        try:
            return await self._request("GET", "/api/licenses/stats")
        except APIError:
            return {
                "total": 0,
                "active": 0,
                "expired": 0,
                "revoked": 0
            }
    
    async def create_license(
        self,
        license_type: str,
        owner: str,
        duration_days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new license.
        
        Args:
            license_type: License type (trial, basic, pro, enterprise)
            owner: Owner name/ID
            duration_days: License duration in days
            
        Returns:
            Created license details or None
        """
        try:
            return await self._request(
                "POST",
                "/api/licenses",
                json={
                    "type": license_type,
                    "owner": owner,
                    "duration_days": duration_days
                }
            )
        except APIError:
            return None
    
    async def verify_license(self, license_key: str) -> Dict[str, Any]:
        """
        Verify a license.
        
        Args:
            license_key: License key to verify
            
        Returns:
            Verification result
        """
        try:
            return await self._request(
                "POST",
                "/api/licenses/verify",
                json={"key": license_key}
            )
        except APIError:
            return {"valid": False, "message": "Verification failed"}
    
    async def revoke_license(self, license_key: str, reason: str = None) -> bool:
        """
        Revoke a license.
        
        Args:
            license_key: License key to revoke
            reason: Revocation reason
            
        Returns:
            True if successful
        """
        try:
            await self._request(
                "POST",
                f"/api/licenses/{license_key}/revoke",
                json={"reason": reason}
            )
            return True
        except APIError:
            return False
    
    async def extend_license(self, license_key: str, days: int = 30) -> bool:
        """
        Extend a license.
        
        Args:
            license_key: License key to extend
            days: Number of days to extend
            
        Returns:
            True if successful
        """
        try:
            await self._request(
                "POST",
                f"/api/licenses/{license_key}/extend",
                json={"days": days}
            )
            return True
        except APIError:
            return False
    
    async def get_expiring_licenses(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get licenses expiring soon.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of expiring licenses
        """
        try:
            result = await self._request(
                "GET",
                "/api/licenses/expiring",
                params={"days": days}
            )
            return result.get("licenses", [])
        except APIError:
            return []
    
    # ==========================================
    # Logs
    # ==========================================
    
    async def get_logs(
        self,
        limit: int = 50,
        level: str = None,
        search: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent logs.
        
        Args:
            limit: Maximum number of logs
            level: Filter by log level
            search: Search query
            
        Returns:
            List of log entries
        """
        params = {"limit": limit}
        if level:
            params["level"] = level
        if search:
            params["search"] = search
        
        try:
            result = await self._request("GET", "/api/logs", params=params)
            return result.get("logs", [])
        except APIError:
            return []
    
    async def get_alerts(
        self,
        limit: int = 20,
        acknowledged: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Args:
            limit: Maximum number of alerts
            acknowledged: Filter by acknowledged status
            
        Returns:
            List of alerts
        """
        params = {"limit": limit}
        if acknowledged is not None:
            params["acknowledged"] = acknowledged
        
        try:
            result = await self._request("GET", "/api/alerts", params=params)
            return result.get("alerts", [])
        except APIError:
            return []
    
    # ==========================================
    # Statistics
    # ==========================================
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get dashboard statistics.
        
        Returns:
            Dashboard statistics dict
        """
        try:
            return await self._request("GET", "/api/stats/dashboard")
        except APIError:
            return {
                "users": {"total": 0, "active": 0, "new": 0},
                "licenses": {"total": 0, "active": 0, "expired": 0},
                "requests": {"total": 0, "today": 0},
                "alerts": {"total": 0, "unread": 0}
            }
    
    async def get_ai_stats(self) -> Dict[str, Any]:
        """
        Get AI usage statistics.
        
        Returns:
            AI statistics dict
        """
        try:
            return await self._request("GET", "/api/stats/ai")
        except APIError:
            return {
                "total_requests": 0,
                "requests_today": 0,
                "tokens_used": 0,
                "average_latency_ms": 0
            }


class APIError(Exception):
    """Exception for API errors."""
    pass
