#!/usr/bin/env python3
"""
dLNk License System - Main Entry Point
ระบบ License และ Authentication สำหรับ dLNk IDE

Usage:
    python main.py server              # Start API server
    python main.py generate            # Generate license
    python main.py validate <key>      # Validate license
    python main.py create-user         # Create user
    python main.py hwid                # Show hardware ID
"""

import os
import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config, Config

config = get_config()


def cmd_server(args):
    """Start API server"""
    from api.server import app
    import uvicorn
    
    print(f"Starting dLNk License Server on {args.host}:{args.port}")
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )


def cmd_generate(args):
    """Generate license"""
    from license import generate_license, generate_encrypted_license
    
    if args.encrypted:
        # Generate encrypted license (compatible with old system)
        encrypted = generate_encrypted_license(
            days_valid=args.days,
            owner=args.owner,
            features=args.features.split(',') if args.features else None
        )
        print(f"\nEncrypted License Key:")
        print(encrypted)
    else:
        # Generate formatted license key
        license_key, encrypted_data = generate_license(
            user_id=args.user_id,
            license_type=args.type,
            duration_days=args.days,
            features=args.features.split(',') if args.features else None,
            owner_name=args.owner,
            email=args.email
        )
        
        print(f"\n{'='*50}")
        print(f"License Generated Successfully!")
        print(f"{'='*50}")
        print(f"License Key: {license_key}")
        print(f"Type: {args.type}")
        print(f"Duration: {args.days} days")
        print(f"Owner: {args.owner}")
        if args.email:
            print(f"Email: {args.email}")
        print(f"{'='*50}")
        
        # Store in database
        from license import license_storage, LicenseData
        from datetime import datetime, timedelta
        
        license_data = LicenseData(
            license_id=license_key.replace("DLNK-", ""),
            user_id=args.user_id,
            license_type=args.type,
            created_at=datetime.now().isoformat(),
            expires_at=(datetime.now() + timedelta(days=args.days)).isoformat(),
            features=args.features.split(',') if args.features else [],
            owner_name=args.owner,
            email=args.email or ""
        )
        
        license_storage.store_license(license_key, license_data, encrypted_data)
        print("License stored in database.")


def cmd_validate(args):
    """Validate license"""
    from license import validate_license, get_hardware_id
    
    hardware_id = args.hwid or get_hardware_id()
    result = validate_license(args.key, hardware_id)
    
    print(f"\n{'='*50}")
    print(f"License Validation Result")
    print(f"{'='*50}")
    print(f"Valid: {result.valid}")
    
    if result.valid:
        print(f"License Type: {result.license_data.license_type}")
        print(f"Features: {', '.join(result.features)}")
        print(f"Days Remaining: {result.days_remaining}")
        if result.warning:
            print(f"Warning: {result.warning}")
    else:
        print(f"Error: {result.error}")
    
    print(f"{'='*50}")


def cmd_create_user(args):
    """Create user"""
    from auth import login_manager
    
    success, message, user = login_manager.create_user(
        username=args.username,
        password=args.password,
        email=args.email,
        role=args.role,
        license_key=args.license_key
    )
    
    print(f"\n{'='*50}")
    if success:
        print("User Created Successfully!")
        print(f"User ID: {user.user_id}")
        print(f"Username: {user.username}")
        print(f"Role: {user.role}")
        if user.email:
            print(f"Email: {user.email}")
    else:
        print(f"Failed: {message}")
    print(f"{'='*50}")


def cmd_hwid(args):
    """Show hardware ID"""
    from license import HardwareID
    
    print(f"\n{'='*50}")
    print("Hardware Information")
    print(f"{'='*50}")
    
    info = HardwareID.get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"{'='*50}")


def cmd_stats(args):
    """Show license statistics"""
    from license import license_storage
    
    stats = license_storage.get_statistics()
    
    print(f"\n{'='*50}")
    print("License Statistics")
    print(f"{'='*50}")
    print(f"Total Licenses: {stats['total_licenses']}")
    print(f"Active: {stats['active_licenses']}")
    print(f"Expired: {stats['expired_licenses']}")
    print(f"Revoked: {stats['revoked_licenses']}")
    print(f"Total Activations: {stats['total_activations']}")
    print(f"\nBy Type:")
    for type_name, count in stats['by_type'].items():
        print(f"  {type_name}: {count}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(
        description='dLNk License System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start API server')
    server_parser.add_argument('--host', default=config.API_HOST, help='Host to bind')
    server_parser.add_argument('--port', type=int, default=config.API_PORT, help='Port to bind')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate license')
    gen_parser.add_argument('--user-id', default='admin', help='User ID')
    gen_parser.add_argument('--type', default='pro', choices=['trial', 'pro', 'enterprise'], help='License type')
    gen_parser.add_argument('--days', type=int, default=365, help='Duration in days')
    gen_parser.add_argument('--owner', default='User', help='Owner name')
    gen_parser.add_argument('--email', help='Email address')
    gen_parser.add_argument('--features', help='Comma-separated features')
    gen_parser.add_argument('--encrypted', action='store_true', help='Generate encrypted license only')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate license')
    val_parser.add_argument('key', help='License key to validate')
    val_parser.add_argument('--hwid', help='Hardware ID (optional)')
    
    # Create user command
    user_parser = subparsers.add_parser('create-user', help='Create user')
    user_parser.add_argument('--username', required=True, help='Username')
    user_parser.add_argument('--password', required=True, help='Password')
    user_parser.add_argument('--email', help='Email address')
    user_parser.add_argument('--role', default='user', help='User role')
    user_parser.add_argument('--license-key', help='License key to assign')
    
    # Hardware ID command
    subparsers.add_parser('hwid', help='Show hardware ID')
    
    # Stats command
    subparsers.add_parser('stats', help='Show license statistics')
    
    args = parser.parse_args()
    
    # Initialize directories
    Config.init_directories()
    
    if args.command == 'server':
        cmd_server(args)
    elif args.command == 'generate':
        cmd_generate(args)
    elif args.command == 'validate':
        cmd_validate(args)
    elif args.command == 'create-user':
        cmd_create_user(args)
    elif args.command == 'hwid':
        cmd_hwid(args)
    elif args.command == 'stats':
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
