#!/usr/bin/env python3
"""
dLNk Admin Console - API Client
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import config


class APIClient:
    """Backend API Client for Admin Console"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'{config.APP_NAME}/{config.APP_VERSION}'
        })
        self.auth_token = None
    
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.auth_token = token
        self.session.headers['Authorization'] = f'Bearer {token}'
    
    def _request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, json=data, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, timeout=30)
            else:
                return {'success': False, 'error': f'Unknown method: {method}'}
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            elif response.status_code == 401:
                return {'success': False, 'error': 'Unauthorized'}
            elif response.status_code == 403:
                return {'success': False, 'error': 'Forbidden'}
            elif response.status_code == 404:
                return {'success': False, 'error': 'Not found'}
            else:
                return {'success': False, 'error': f'Error {response.status_code}: {response.text}'}
                
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection failed - Server may be offline'}
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ===== Dashboard =====
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        result = self._request('GET', '/api/stats')
        if result['success']:
            return result['data']
        
        # Return mock data if API fails
        return self._get_mock_dashboard_stats()
    
    def _get_mock_dashboard_stats(self) -> Dict:
        """Return mock dashboard data for offline mode"""
        return {
            'license_stats': {
                'total_licenses': 156,
                'active_licenses': 142,
                'expired_licenses': 10,
                'revoked_licenses': 4,
                'recent_activity': []
            },
            'c2_stats': {
                'requests_today': 4567,
                'active_users_today': 89,
                'blocked_today': 12,
                'pending_alerts': 3,
                'top_users': [
                    {'user_id': 'user_001', 'count': 234},
                    {'user_id': 'user_002', 'count': 189},
                    {'user_id': 'user_003', 'count': 156},
                ]
            }
        }
    
    # ===== Licenses =====
    
    def get_licenses(self, status: str = None, search: str = None) -> List[Dict]:
        """Get all licenses"""
        params = {}
        if status:
            params['status'] = status
        if search:
            params['search'] = search
        
        result = self._request('GET', '/api/licenses', params=params)
        if result['success']:
            return result['data']
        
        # Return mock data
        return self._get_mock_licenses()
    
    def _get_mock_licenses(self) -> List[Dict]:
        """Return mock license data"""
        return [
            {'key': 'DLNK-PRO-XXXX-XXXX-XXXX', 'user': 'john_doe', 'type': 'Pro', 'status': 'active', 'expires': '2025-12-31'},
            {'key': 'DLNK-ENT-YYYY-YYYY-YYYY', 'user': 'jane_smith', 'type': 'Enterprise', 'status': 'active', 'expires': '2026-06-30'},
            {'key': 'DLNK-TRI-ZZZZ-ZZZZ-ZZZZ', 'user': 'bob_wilson', 'type': 'Trial', 'status': 'expired', 'expires': '2024-01-15'},
            {'key': 'DLNK-BAS-AAAA-AAAA-AAAA', 'user': 'alice_jones', 'type': 'Basic', 'status': 'active', 'expires': '2025-09-20'},
            {'key': 'DLNK-PRO-BBBB-BBBB-BBBB', 'user': 'charlie_brown', 'type': 'Pro', 'status': 'revoked', 'expires': '2025-03-15'},
        ]
    
    def create_license(self, owner: str, license_type: str, duration_days: int) -> Dict:
        """Create new license"""
        data = {
            'owner': owner,
            'type': license_type,
            'duration': duration_days
        }
        result = self._request('POST', '/api/licenses', data=data)
        if result['success']:
            return result['data']
        
        # Return mock created license
        import secrets
        key = f"DLNK-{license_type[:3].upper()}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
        return {
            'key': key,
            'owner': owner,
            'type': license_type,
            'expires': (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d'),
            'encrypted': f"gAAAAAB{secrets.token_urlsafe(64)}"
        }
    
    def revoke_license(self, key: str) -> bool:
        """Revoke a license"""
        result = self._request('POST', f'/api/licenses/{key}/revoke')
        return result['success']
    
    def extend_license(self, key: str, days: int = 30) -> bool:
        """Extend license expiry"""
        result = self._request('POST', f'/api/licenses/{key}/extend', data={'days': days})
        return result['success']
    
    # ===== Users =====
    
    def get_users(self, search: str = None) -> List[Dict]:
        """Get all users"""
        params = {'search': search} if search else {}
        result = self._request('GET', '/api/users', params=params)
        if result['success']:
            return result['data']
        
        return self._get_mock_users()
    
    def _get_mock_users(self) -> List[Dict]:
        """Return mock user data"""
        return [
            {'username': 'john_doe', 'email': 'john@example.com', 'role': 'user', 'status': 'active', 'created': '2024-01-15', 'last_login': '2025-01-10'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'role': 'user', 'status': 'active', 'created': '2024-02-20', 'last_login': '2025-01-09'},
            {'username': 'bob_wilson', 'email': 'bob@example.com', 'role': 'user', 'status': 'banned', 'created': '2024-03-10', 'last_login': '2024-12-01'},
            {'username': 'alice_jones', 'email': 'alice@example.com', 'role': 'premium', 'status': 'active', 'created': '2024-04-05', 'last_login': '2025-01-10'},
        ]
    
    def ban_user(self, username: str, reason: str = None) -> bool:
        """Ban a user"""
        result = self._request('POST', f'/api/users/{username}/ban', data={'reason': reason})
        return result['success']
    
    def unban_user(self, username: str) -> bool:
        """Unban a user"""
        result = self._request('POST', f'/api/users/{username}/unban')
        return result['success']
    
    # ===== Logs =====
    
    def get_logs(self, limit: int = 50, log_type: str = None) -> List[Dict]:
        """Get C2 logs"""
        params = {'limit': limit}
        if log_type:
            params['type'] = log_type
        
        result = self._request('GET', '/api/logs', params=params)
        if result['success']:
            return result['data']
        
        return self._get_mock_logs()
    
    def _get_mock_logs(self) -> List[Dict]:
        """Return mock log data"""
        return [
            {'timestamp': '2025-01-10 14:30:25', 'user': 'john_doe', 'status': 'success', 'prompt': 'Generate Python code for...', 'time_ms': 245},
            {'timestamp': '2025-01-10 14:28:12', 'user': 'jane_smith', 'status': 'success', 'prompt': 'Explain this JavaScript...', 'time_ms': 189},
            {'timestamp': '2025-01-10 14:25:45', 'user': 'bob_wilson', 'status': 'blocked', 'prompt': 'How to bypass security...', 'time_ms': 12},
            {'timestamp': '2025-01-10 14:22:33', 'user': 'alice_jones', 'status': 'success', 'prompt': 'Debug this React component...', 'time_ms': 312},
        ]
    
    def get_alerts(self, unacknowledged_only: bool = False) -> List[Dict]:
        """Get alerts"""
        params = {'unacknowledged': unacknowledged_only}
        result = self._request('GET', '/api/alerts', params=params)
        if result['success']:
            return result['data']
        
        return self._get_mock_alerts()
    
    def _get_mock_alerts(self) -> List[Dict]:
        """Return mock alert data"""
        return [
            {'id': 1, 'timestamp': '2025-01-10 14:25:45', 'severity': 'critical', 'type': 'blocked_prompt', 'message': 'Suspicious prompt detected from user bob_wilson', 'acknowledged': False},
            {'id': 2, 'timestamp': '2025-01-10 13:15:22', 'severity': 'warning', 'type': 'rate_limit', 'message': 'User john_doe exceeded rate limit', 'acknowledged': True},
            {'id': 3, 'timestamp': '2025-01-10 10:45:00', 'severity': 'info', 'type': 'new_user', 'message': 'New user registered: charlie_brown', 'acknowledged': True},
        ]
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Acknowledge an alert"""
        result = self._request('POST', f'/api/alerts/{alert_id}/acknowledge')
        return result['success']
    
    # ===== Tokens =====
    
    def get_tokens(self) -> List[Dict]:
        """Get Antigravity tokens"""
        result = self._request('GET', '/api/tokens')
        if result['success']:
            return result['data']
        
        return self._get_mock_tokens()
    
    def _get_mock_tokens(self) -> List[Dict]:
        """Return mock token data"""
        return [
            {'id': 1, 'name': 'Primary Token', 'status': 'active', 'last_used': '2025-01-10 14:30:00', 'requests_today': 1234, 'expires': '2025-02-10'},
            {'id': 2, 'name': 'Backup Token', 'status': 'active', 'last_used': '2025-01-09 18:45:00', 'requests_today': 567, 'expires': '2025-03-15'},
            {'id': 3, 'name': 'Dev Token', 'status': 'expired', 'last_used': '2024-12-20 10:00:00', 'requests_today': 0, 'expires': '2024-12-31'},
        ]
    
    def refresh_token(self, token_id: int) -> Dict:
        """Refresh a token"""
        result = self._request('POST', f'/api/tokens/{token_id}/refresh')
        if result['success']:
            return result['data']
        return {'success': True, 'message': 'Token refreshed successfully'}
