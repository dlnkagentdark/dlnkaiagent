"""
dLNk Telegram Bot - API Client Package

This package provides API client implementations for communicating
with the dLNk backend services.

Modules:
    backend: Client for the main dLNk Backend API
    
Classes:
    BackendAPIClient: Main API client for backend communication
    APIError: Exception class for API errors

Example:
    >>> from api_client import BackendAPIClient
    >>> 
    >>> async def main():
    ...     client = BackendAPIClient()
    ...     status = await client.get_system_status()
    ...     print(status)
    ...     await client.close()
"""

from .backend import BackendAPIClient, APIError

__all__ = ['BackendAPIClient', 'APIError']
__version__ = '1.0.0'
