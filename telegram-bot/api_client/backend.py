"""
dLNk Telegram Bot - Backend API Client

This module provides a client for communicating with the dLNk backend API.
It handles all HTTP communication with proper error handling and retry logic.
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
    - Registration approval/rejection
    - System status
    - Logs retrieval
    - Statistics
    
    Attributes:
        base_url: The base URL of the backend API
        api_key: API key for authentication
        timeout: Request timeout in seconds
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
            base_url: Backend API base URL. Defaults to APIConfig.BACKEND_URL
            api_key: API key for authentication. Defaults to APIConfig.API_KEY
            timeout: Request timeout in seconds. Defaults to APIConfig.API_TIMEOUT
        """
        self.base_url = (base_url or APIConfig.BACKEND_URL).rstrip('/')
        self.api_key = api_key or APIConfig.API_KEY
        self.timeout = timeout or APIConfig.API_TIMEOUT
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client.
        
        Returns:
            httpx.AsyncClient: The HTTP client instance
        """
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
        """
        Close the HTTP client and release resources.
        
        Should be called when the client is no longer needed.
        """
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
        Make an API request with error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional request arguments (json, params, etc.)
            
        Returns:
            Dict[str, Any]: Response data as dictionary
            
        Raises:
            APIError: If the request fails
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
            Dict[str, Any]: System status containing service health and metrics
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
            Dict[str, Any]: Health metrics including CPU, memory, and service status
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
        Get list of users with pagination.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page (max 100)
            search: Optional search query for filtering
            
        Returns:
            Dict[str, Any]: Users list with pagination metadata
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
        Get user details by ID.
        
        Args:
            user_id: The user's unique identifier
            
        Returns:
            Optional[Dict[str, Any]]: User details or None if not found
        """
        try:
            return await self._request("GET", f"/api/users/{user_id}")
        except APIError:
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user details by email address.
        
        Args:
            email: The user's email address
            
        Returns:
            Optional[Dict[str, Any]]: User details or None if not found
        """
        try:
            result = await self._request("GET", "/api/users", params={"search": email})
            users = result.get("users", [])
            for user in users:
                if user.get("email", "").lower() == email.lower():
                    return user
            return None
        except APIError:
            return None
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Returns:
            Dict[str, Any]: Statistics including total, active, and new users
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
        Ban a user from the system.
        
        Args:
            user_id: User ID to ban
            reason: Optional reason for the ban
            
        Returns:
            bool: True if successful, False otherwise
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
        Unban a previously banned user.
        
        Args:
            user_id: User ID to unban
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._request("POST", f"/api/users/{user_id}/unban")
            return True
        except APIError:
            return False
    
    # ==========================================
    # Registration Management (Admin)
    # ==========================================
    
    async def get_pending_registrations(self) -> List[Dict[str, Any]]:
        """
        Get list of pending registration requests.
        
        Returns:
            List[Dict[str, Any]]: List of pending registration requests
        """
        try:
            result = await self._request(
                "GET",
                "/api/auth/registrations/pending"
            )
            return result.get("registrations", [])
        except APIError:
            # Fallback: try to get from users with pending status
            try:
                result = await self._request(
                    "GET",
                    "/api/users",
                    params={"status": "pending"}
                )
                return result.get("users", [])
            except APIError:
                return []
    
    async def approve_registration(
        self,
        email: str,
        license_type: str = "trial",
        duration_days: int = 30,
        approved_by: str = None
    ) -> Dict[str, Any]:
        """
        Approve a pending registration request.
        
        This will create a user account and generate a license key.
        
        Args:
            email: Email of the user to approve
            license_type: Type of license to grant (trial, pro, enterprise)
            duration_days: License duration in days
            approved_by: Admin who approved the request
            
        Returns:
            Dict[str, Any]: Result containing success status and license info
        """
        try:
            # First, try the dedicated approval endpoint
            result = await self._request(
                "POST",
                "/api/auth/registrations/approve",
                json={
                    "email": email,
                    "license_type": license_type,
                    "duration_days": duration_days,
                    "approved_by": approved_by
                }
            )
            return result
        except APIError:
            # Fallback: Generate license directly
            try:
                # Get user info first
                user = await self.get_user_by_email(email)
                if not user:
                    return {
                        "success": False,
                        "message": f"User with email {email} not found"
                    }
                
                # Generate license for the user
                license_result = await self.create_license(
                    license_type=license_type,
                    owner=user.get("username", email),
                    duration_days=duration_days,
                    email=email
                )
                
                if license_result:
                    # Update user status to approved
                    await self._request(
                        "POST",
                        f"/api/users/{user.get('user_id')}/approve",
                        json={"approved_by": approved_by}
                    )
                    
                    return {
                        "success": True,
                        "message": "Registration approved",
                        "license_key": license_result.get("license_key"),
                        "user": user
                    }
                else:
                    return {
                        "success": False,
                        "message": "Failed to create license"
                    }
            except APIError as e:
                return {
                    "success": False,
                    "message": str(e)
                }
    
    async def reject_registration(
        self,
        email: str,
        reason: str = None,
        rejected_by: str = None
    ) -> Dict[str, Any]:
        """
        Reject a pending registration request.
        
        Args:
            email: Email of the user to reject
            reason: Reason for rejection
            rejected_by: Admin who rejected the request
            
        Returns:
            Dict[str, Any]: Result containing success status
        """
        try:
            result = await self._request(
                "POST",
                "/api/auth/registrations/reject",
                json={
                    "email": email,
                    "reason": reason,
                    "rejected_by": rejected_by
                }
            )
            return result
        except APIError:
            # Fallback: Update user status directly
            try:
                user = await self.get_user_by_email(email)
                if not user:
                    return {
                        "success": False,
                        "message": f"User with email {email} not found"
                    }
                
                await self._request(
                    "POST",
                    f"/api/users/{user.get('user_id')}/reject",
                    json={
                        "reason": reason,
                        "rejected_by": rejected_by
                    }
                )
                
                return {
                    "success": True,
                    "message": "Registration rejected"
                }
            except APIError as e:
                return {
                    "success": False,
                    "message": str(e)
                }
    
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
        Get list of licenses with pagination and filtering.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page
            status: Filter by status (active, expired, revoked)
            search: Search query for license key or owner
            
        Returns:
            Dict[str, Any]: Licenses list with pagination metadata
        """
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        
        try:
            return await self._request("GET", "/api/license/list", params=params)
        except APIError:
            return {"licenses": [], "total": 0, "page": page}
    
    async def get_license(self, license_key: str) -> Optional[Dict[str, Any]]:
        """
        Get license details by key.
        
        Args:
            license_key: The license key to look up
            
        Returns:
            Optional[Dict[str, Any]]: License details or None if not found
        """
        try:
            result = await self._request("GET", f"/api/license/info/{license_key}")
            return result.get("license")
        except APIError:
            return None
    
    async def get_license_stats(self) -> Dict[str, Any]:
        """
        Get license statistics.
        
        Returns:
            Dict[str, Any]: Statistics including total, active, expired counts
        """
        try:
            result = await self._request("GET", "/api/license/stats")
            return result.get("stats", {})
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
        duration_days: int = 30,
        email: str = None,
        features: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new license.
        
        Args:
            license_type: License type (trial, pro, enterprise)
            owner: Owner name or username
            duration_days: License duration in days
            email: Owner's email address
            features: Optional list of features to enable
            
        Returns:
            Optional[Dict[str, Any]]: Created license details or None on failure
        """
        try:
            return await self._request(
                "POST",
                "/api/license/generate",
                json={
                    "user_id": owner,
                    "license_type": license_type,
                    "duration_days": duration_days,
                    "owner_name": owner,
                    "email": email or "",
                    "features": features
                }
            )
        except APIError:
            return None
    
    async def verify_license(self, license_key: str) -> Dict[str, Any]:
        """
        Verify a license key.
        
        Args:
            license_key: License key to verify
            
        Returns:
            Dict[str, Any]: Verification result with validity and features
        """
        try:
            return await self._request(
                "POST",
                "/api/license/validate",
                json={"license_key": license_key}
            )
        except APIError:
            return {"valid": False, "message": "Verification failed"}
    
    async def revoke_license(self, license_key: str, reason: str = None) -> bool:
        """
        Revoke a license.
        
        Args:
            license_key: License key to revoke
            reason: Reason for revocation
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._request(
                "POST",
                "/api/license/revoke",
                json={
                    "license_key": license_key,
                    "reason": reason or ""
                }
            )
            return True
        except APIError:
            return False
    
    async def extend_license(self, license_key: str, days: int = 30) -> bool:
        """
        Extend a license's expiration date.
        
        Args:
            license_key: License key to extend
            days: Number of days to extend
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._request(
                "POST",
                "/api/license/extend",
                json={
                    "license_key": license_key,
                    "days": days
                }
            )
            return True
        except APIError:
            return False
    
    async def get_expiring_licenses(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get licenses expiring within specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List[Dict[str, Any]]: List of expiring licenses
        """
        try:
            result = await self._request(
                "GET",
                "/api/license/expiring",
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
        Get recent system logs.
        
        Args:
            limit: Maximum number of logs to return
            level: Filter by log level (info, warning, error)
            search: Search query for log content
            
        Returns:
            List[Dict[str, Any]]: List of log entries
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
            limit: Maximum number of alerts to return
            acknowledged: Filter by acknowledged status
            
        Returns:
            List[Dict[str, Any]]: List of alerts
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
        Get dashboard statistics for overview display.
        
        Returns:
            Dict[str, Any]: Comprehensive dashboard statistics
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
            Dict[str, Any]: AI usage metrics including requests and tokens
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
    """
    Exception for API errors.
    
    Raised when an API request fails due to network issues,
    authentication errors, or server-side problems.
    """
    pass
