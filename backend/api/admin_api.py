#!/usr/bin/env python3
"""
dLNk Admin API
===============
REST API สำหรับ Admin App

Endpoints:
- /api/licenses - จัดการ License Keys
- /api/tokens - จัดการ Token Pool
- /api/stats - ดูสถิติ
- /api/auth - Authentication

Author: dLNk IDE Project (AI-01 The Architect)
Date: December 25, 2025
"""

import os
import json
import functools
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import Flask, Blueprint, request, jsonify, g
import jwt
import logging

# Import modules
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from license.license_system import (
    LicenseSystem, LicenseType, LicenseStatus, 
    LicenseGenerator, get_license_system
)
from security.two_factor import TwoFactorAuth, get_two_factor_auth
from security.encryption import DataEncryptor, get_encryptor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api')

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'dlnk-admin-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


# ==================== Authentication ====================

def create_token(user_id: str, role: str = 'admin') -> str:
    """สร้าง JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """ตรวจสอบ JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator สำหรับ endpoints ที่ต้อง authenticate"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
        except IndexError:
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.user = payload
        return f(*args, **kwargs)
    
    return decorated


def require_admin(f):
    """Decorator สำหรับ endpoints ที่ต้องเป็น admin"""
    @functools.wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        if g.user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated


# ==================== Auth Endpoints ====================

# Simple admin credentials (ควรเปลี่ยนเป็น database ในการใช้งานจริง)
ADMIN_USERS = {
    'admin': {
        'password_hash': 'admin123',  # ควรเป็น hashed password
        'role': 'admin'
    }
}


@admin_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Login endpoint
    
    Request:
        {
            "username": "admin",
            "password": "admin123",
            "totp_code": "123456" (optional if 2FA enabled)
        }
    
    Response:
        {
            "success": true,
            "token": "jwt_token",
            "requires_2fa": false
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Missing request body'}), 400
    
    username = data.get('username')
    password = data.get('password')
    totp_code = data.get('totp_code')
    
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Verify credentials
    user = ADMIN_USERS.get(username)
    if not user or user['password_hash'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check 2FA
    tfa = get_two_factor_auth()
    if tfa.is_enabled(username):
        if not totp_code:
            return jsonify({
                'success': False,
                'requires_2fa': True,
                'message': '2FA code required'
            }), 200
        
        valid, method = tfa.verify(username, totp_code)
        if not valid:
            return jsonify({'error': 'Invalid 2FA code'}), 401
    
    # Generate token
    token = create_token(username, user['role'])
    
    logger.info(f"✅ User logged in: {username}")
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'username': username,
            'role': user['role']
        }
    }), 200


@admin_bp.route('/auth/2fa/setup', methods=['POST'])
@require_admin
def setup_2fa():
    """Setup 2FA for current user"""
    tfa = get_two_factor_auth()
    setup = tfa.setup(g.user['user_id'])
    
    return jsonify({
        'success': True,
        'secret': setup['secret'],
        'qr_uri': setup['qr_uri'],
        'backup_codes': setup['backup_codes']
    }), 200


@admin_bp.route('/auth/2fa/verify', methods=['POST'])
@require_admin
def verify_2fa_setup():
    """Verify and enable 2FA"""
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'Missing code'}), 400
    
    tfa = get_two_factor_auth()
    if tfa.verify_setup(g.user['user_id'], code):
        return jsonify({
            'success': True,
            'message': '2FA enabled successfully'
        }), 200
    else:
        return jsonify({'error': 'Invalid code'}), 400


@admin_bp.route('/auth/2fa/status', methods=['GET'])
@require_admin
def get_2fa_status():
    """Get 2FA status"""
    tfa = get_two_factor_auth()
    status = tfa.get_status(g.user['user_id'])
    
    return jsonify({
        'success': True,
        'status': status
    }), 200


# ==================== License Endpoints ====================

@admin_bp.route('/licenses', methods=['GET'])
@require_admin
def list_licenses():
    """
    List all licenses
    
    Query params:
        - status: Filter by status
        - type: Filter by type
        - limit: Max results
        - offset: Pagination offset
    """
    system = get_license_system()
    licenses = system.storage.list_all()
    
    # Apply filters
    status_filter = request.args.get('status')
    type_filter = request.args.get('type')
    
    if status_filter:
        licenses = [l for l in licenses if l.status.value == status_filter]
    
    if type_filter:
        licenses = [l for l in licenses if l.license_type.value == type_filter]
    
    # Pagination
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    total = len(licenses)
    licenses = licenses[offset:offset + limit]
    
    return jsonify({
        'success': True,
        'total': total,
        'limit': limit,
        'offset': offset,
        'licenses': [l.to_dict() for l in licenses]
    }), 200


@admin_bp.route('/licenses', methods=['POST'])
@require_admin
def create_license():
    """
    Create new license
    
    Request:
        {
            "type": "pro",
            "user_email": "user@example.com",
            "max_activations": 1
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Missing request body'}), 400
    
    # Parse license type
    type_str = data.get('type', 'basic')
    try:
        license_type = LicenseType(type_str)
    except ValueError:
        return jsonify({'error': f'Invalid license type: {type_str}'}), 400
    
    system = get_license_system()
    license = system.create_license(
        license_type=license_type,
        user_email=data.get('user_email'),
        max_activations=data.get('max_activations', 1)
    )
    
    logger.info(f"✅ Created license: {license.key}")
    
    return jsonify({
        'success': True,
        'license': license.to_dict()
    }), 201


@admin_bp.route('/licenses/<key>', methods=['GET'])
@require_admin
def get_license(key: str):
    """Get license by key"""
    system = get_license_system()
    license = system.storage.get(key)
    
    if not license:
        return jsonify({'error': 'License not found'}), 404
    
    return jsonify({
        'success': True,
        'license': license.to_dict()
    }), 200


@admin_bp.route('/licenses/<key>/validate', methods=['POST'])
def validate_license(key: str):
    """
    Validate license (public endpoint)
    
    Request:
        {
            "hwid": "hardware_id"
        }
    """
    data = request.get_json() or {}
    hwid = data.get('hwid')
    
    system = get_license_system()
    result = system.validate(key, hwid, online=False)
    
    return jsonify(result), 200


@admin_bp.route('/licenses/<key>/activate', methods=['POST'])
def activate_license(key: str):
    """
    Activate license (public endpoint)
    
    Request:
        {
            "hwid": "hardware_id"
        }
    """
    data = request.get_json() or {}
    hwid = data.get('hwid')
    
    system = get_license_system()
    success, message = system.activate(key, hwid)
    
    return jsonify({
        'success': success,
        'message': message
    }), 200 if success else 400


@admin_bp.route('/licenses/<key>/revoke', methods=['POST'])
@require_admin
def revoke_license(key: str):
    """Revoke license"""
    data = request.get_json() or {}
    reason = data.get('reason', '')
    
    system = get_license_system()
    if system.revoke(key, reason):
        return jsonify({
            'success': True,
            'message': 'License revoked'
        }), 200
    else:
        return jsonify({'error': 'License not found'}), 404


@admin_bp.route('/licenses/generate', methods=['POST'])
@require_admin
def generate_license_key():
    """
    Generate license key only (without creating)
    
    Request:
        {
            "type": "pro"
        }
    """
    data = request.get_json() or {}
    type_str = data.get('type', 'basic')
    
    try:
        license_type = LicenseType(type_str)
    except ValueError:
        return jsonify({'error': f'Invalid license type: {type_str}'}), 400
    
    key = LicenseGenerator.generate(license_type)
    
    return jsonify({
        'success': True,
        'key': key,
        'type': type_str
    }), 200


# ==================== Token Pool Endpoints ====================

@admin_bp.route('/tokens/status', methods=['GET'])
@require_admin
def get_token_status():
    """Get token pool status"""
    # This would connect to Token Harvester
    # For now, return mock data
    return jsonify({
        'success': True,
        'status': {
            'total_tokens': 0,
            'available_tokens': 0,
            'exhausted_tokens': 0,
            'harvester_status': 'not_connected'
        }
    }), 200


# ==================== Stats Endpoints ====================

@admin_bp.route('/stats', methods=['GET'])
@require_admin
def get_stats():
    """Get overall statistics"""
    system = get_license_system()
    license_stats = system.get_stats()
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'licenses': license_stats,
        'system': {
            'version': '1.0.0',
            'uptime': 'N/A'
        }
    }), 200


@admin_bp.route('/stats/licenses', methods=['GET'])
@require_admin
def get_license_stats():
    """Get license statistics"""
    system = get_license_system()
    stats = system.get_stats()
    
    return jsonify({
        'success': True,
        'stats': stats
    }), 200


# ==================== Health Endpoint ====================

@admin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'dLNk Admin API'
    }), 200


# ==================== Create Flask App ====================

def create_app() -> Flask:
    """สร้าง Flask application"""
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


# ==================== Test ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Testing Admin API")
    print("=" * 60)
    
    app = create_app()
    
    with app.test_client() as client:
        # Test 1: Health check
        print("\n📤 Test 1: Health check")
        response = client.get('/api/health')
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.get_json()}")
        
        # Test 2: Login
        print("\n📤 Test 2: Login")
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        print(f"  Status: {response.status_code}")
        data = response.get_json()
        print(f"  Success: {data.get('success')}")
        token = data.get('token')
        
        # Test 3: Create license (with auth)
        print("\n📤 Test 3: Create license")
        response = client.post('/api/licenses', 
            json={'type': 'pro', 'user_email': 'test@example.com'},
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"  Status: {response.status_code}")
        license_data = response.get_json()
        print(f"  License key: {license_data.get('license', {}).get('key')}")
        
        # Test 4: List licenses
        print("\n📤 Test 4: List licenses")
        response = client.get('/api/licenses',
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"  Status: {response.status_code}")
        data = response.get_json()
        print(f"  Total licenses: {data.get('total')}")
        
        # Test 5: Get stats
        print("\n📤 Test 5: Get stats")
        response = client.get('/api/stats',
            headers={'Authorization': f'Bearer {token}'}
        )
        print(f"  Status: {response.status_code}")
        stats = response.get_json()
        print(f"  License stats: {stats.get('licenses')}")
        
        # Test 6: Validate license (public)
        print("\n📤 Test 6: Validate license")
        key = license_data.get('license', {}).get('key')
        response = client.post(f'/api/licenses/{key}/validate', json={
            'hwid': 'TEST_HWID_123'
        })
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.get_json()}")
    
    print("\n✅ Admin API test completed!")
    
    # Run server
    print("\n" + "=" * 60)
    print("🚀 Starting Admin API server on http://localhost:5000")
    print("=" * 60)
    # app.run(host='0.0.0.0', port=5000, debug=True)
