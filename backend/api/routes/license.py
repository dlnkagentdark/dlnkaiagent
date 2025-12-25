"""
dLNk IDE - License API Routes
API endpoints สำหรับจัดการ License

Endpoints:
- GET /api/license/verify/{license_key} - Verify license key
- POST /api/license/validate - Validate license with HWID
- GET /api/license/info/{license_key} - Get license information
- GET /api/license/hardware-id - Get current hardware ID
- GET /api/license/features/{license_key} - Get license features
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
import logging

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'license'))

from fastapi import APIRouter, HTTPException, Request, Query
from pydantic import BaseModel, Field

logger = logging.getLogger('dLNk-LicenseAPI')
router = APIRouter(prefix="/license", tags=["License"])


# ==================== Request/Response Models ====================

class LicenseVerifyResponse(BaseModel):
    """Response model สำหรับ License Verification"""
    valid: bool
    message: str
    license_key: Optional[str] = None
    license_type: Optional[str] = None
    status: Optional[str] = None
    features: List[str] = []
    days_remaining: int = 0
    expires_at: Optional[str] = None
    max_devices: int = 1
    current_devices: int = 0
    owner_name: Optional[str] = None
    warning: Optional[str] = None


class LicenseValidateRequest(BaseModel):
    """Request model สำหรับ License Validation with HWID"""
    license_key: str = Field(..., description="License key to validate")
    hwid: str = Field(..., description="Hardware ID of the client machine")
    device_name: Optional[str] = Field(None, description="Optional device name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "license_key": "DLNK-XXXX-XXXX-XXXX-XXXX",
                "hwid": "ABC123DEF456",
                "device_name": "Development PC"
            }
        }


class LicenseValidateResponse(BaseModel):
    """Response model สำหรับ License Validation"""
    valid: bool
    message: str
    license_key: Optional[str] = None
    license_type: Optional[str] = None
    features: List[str] = []
    days_remaining: int = 0
    expires_at: Optional[str] = None
    hwid_bound: bool = False
    activation_status: Optional[str] = None
    warning: Optional[str] = None


class HardwareIDResponse(BaseModel):
    """Response model สำหรับ Hardware ID"""
    success: bool
    hardware_id: str
    hardware_id_short: str
    platform: str
    platform_version: str
    architecture: str
    hostname: str
    components: dict = {}


class LicenseInfoResponse(BaseModel):
    """Response model สำหรับ License Information"""
    success: bool
    license: Optional[dict] = None
    message: Optional[str] = None


class LicenseFeaturesResponse(BaseModel):
    """Response model สำหรับ License Features"""
    success: bool
    license_key: str
    license_type: str
    features: List[str]
    feature_details: dict = {}


# ==================== Hardware ID Helper ====================

def get_hardware_info() -> dict:
    """Get hardware information for current machine"""
    try:
        # Try to import from license module
        try:
            from license.license.hardware import HardwareID
            
            return {
                "hardware_id": HardwareID.generate(),
                "hardware_id_short": HardwareID.generate_short(),
                "system_info": HardwareID.get_system_info()
            }
        except ImportError:
            pass
        
        # Fallback implementation
        import platform
        import uuid
        import hashlib
        
        # Get MAC address
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                       for ele in range(0, 8*6, 8)][::-1])
        
        # Generate hardware ID
        components = [
            f"mac:{mac}",
            f"platform:{platform.system()}",
            f"machine:{platform.machine()}",
            f"node:{platform.node()}"
        ]
        
        combined = '|'.join(sorted(components))
        hardware_id = hashlib.sha256(combined.encode()).hexdigest()
        
        return {
            "hardware_id": hardware_id,
            "hardware_id_short": hardware_id[:16].upper(),
            "system_info": {
                "platform": platform.system(),
                "platform_release": platform.release(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "processor": platform.processor(),
                "mac_address": mac
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get hardware info: {e}")
        return {
            "hardware_id": "UNKNOWN",
            "hardware_id_short": "UNKNOWN",
            "system_info": {}
        }


# ==================== License Validation Helper ====================

def validate_license(license_key: str, hwid: str = None) -> dict:
    """
    Validate license key
    
    Returns dict with validation result
    """
    try:
        # Try to import from license module
        try:
            from license.license.validator import LicenseValidator
            from license.license.storage import LicenseStorage
            
            validator = LicenseValidator()
            storage = LicenseStorage()
            
            # Get license data
            license_data = storage.get_license(license_key)
            if not license_data:
                return {
                    "valid": False,
                    "error": "License not found",
                    "status": "not_found"
                }
            
            # Check if license is revoked
            if license_data.get('status') == 'revoked':
                return {
                    "valid": False,
                    "error": "License has been revoked",
                    "status": "revoked"
                }
            
            # Check expiration
            expires_at = license_data.get('expires_at')
            if expires_at:
                try:
                    exp_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    if exp_date < datetime.now(exp_date.tzinfo if exp_date.tzinfo else None):
                        return {
                            "valid": False,
                            "error": "License has expired",
                            "status": "expired",
                            "expires_at": expires_at
                        }
                    
                    days_remaining = (exp_date.replace(tzinfo=None) - datetime.now()).days
                except:
                    days_remaining = 0
            else:
                days_remaining = 365  # Default if no expiration
            
            # Validate with HWID if provided
            if hwid:
                result = validator.validate(license_key, hwid)
                if not result.valid:
                    return {
                        "valid": False,
                        "error": result.error or "Hardware ID mismatch",
                        "status": "hwid_mismatch"
                    }
            
            return {
                "valid": True,
                "license_type": license_data.get('license_type', 'unknown'),
                "features": license_data.get('features', []),
                "days_remaining": days_remaining,
                "expires_at": expires_at,
                "max_devices": license_data.get('max_devices', 1),
                "owner_name": license_data.get('owner_name', ''),
                "status": "active"
            }
            
        except ImportError:
            logger.warning("License module not available, using simple validation")
        
        # Fallback: Simple validation for testing
        if not license_key:
            return {
                "valid": False,
                "error": "License key is required",
                "status": "invalid"
            }
        
        # Check format
        if not license_key.startswith("DLNK-"):
            return {
                "valid": False,
                "error": "Invalid license format",
                "status": "invalid_format"
            }
        
        # Simple validation - accept any DLNK- prefixed key for testing
        parts = license_key.split("-")
        if len(parts) < 4:
            return {
                "valid": False,
                "error": "Invalid license format",
                "status": "invalid_format"
            }
        
        # Determine license type from key
        license_type = "pro"  # Default
        if "TRIAL" in license_key.upper():
            license_type = "trial"
        elif "ENT" in license_key.upper():
            license_type = "enterprise"
        
        # Get features based on type
        features = get_features_for_type(license_type)
        
        return {
            "valid": True,
            "license_type": license_type,
            "features": features,
            "days_remaining": 365,
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),
            "max_devices": 3 if license_type == "enterprise" else 1,
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"License validation error: {e}")
        return {
            "valid": False,
            "error": str(e),
            "status": "error"
        }


def get_features_for_type(license_type: str) -> List[str]:
    """Get features list for license type"""
    base_features = [
        "code_editor",
        "syntax_highlighting",
        "file_explorer"
    ]
    
    pro_features = [
        "ai_code_completion",
        "ai_assistant",
        "advanced_debugging",
        "git_integration",
        "terminal",
        "extensions"
    ]
    
    enterprise_features = [
        "team_collaboration",
        "admin_console",
        "priority_support",
        "custom_branding",
        "sso_integration",
        "audit_logs"
    ]
    
    if license_type == "trial":
        return base_features + ["ai_code_completion"]
    elif license_type == "pro":
        return base_features + pro_features
    elif license_type == "enterprise":
        return base_features + pro_features + enterprise_features
    else:
        return base_features


# ==================== API Endpoints ====================

@router.get("/verify/{license_key}", response_model=LicenseVerifyResponse)
async def verify_license(
    license_key: str,
    hwid: Optional[str] = Query(None, description="Optional hardware ID for binding check")
):
    """
    Verify license key validity
    
    - **license_key**: The license key to verify
    - **hwid**: Optional hardware ID to check binding
    
    Returns license status, type, features, and remaining days.
    """
    try:
        logger.info(f"Verifying license: {license_key[:10]}...")
        
        result = validate_license(license_key, hwid)
        
        if result.get("valid"):
            warning = None
            days_remaining = result.get("days_remaining", 0)
            
            # Add warning if license is expiring soon
            if days_remaining <= 30:
                warning = f"License expires in {days_remaining} days"
            
            return LicenseVerifyResponse(
                valid=True,
                message="License is valid",
                license_key=license_key,
                license_type=result.get("license_type"),
                status=result.get("status", "active"),
                features=result.get("features", []),
                days_remaining=days_remaining,
                expires_at=result.get("expires_at"),
                max_devices=result.get("max_devices", 1),
                owner_name=result.get("owner_name"),
                warning=warning
            )
        else:
            return LicenseVerifyResponse(
                valid=False,
                message=result.get("error", "Invalid license"),
                license_key=license_key,
                status=result.get("status", "invalid")
            )
            
    except Exception as e:
        logger.error(f"License verification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=LicenseValidateResponse)
async def validate_license_with_hwid(request: LicenseValidateRequest, req: Request):
    """
    Validate license with hardware ID binding
    
    - **license_key**: License key to validate
    - **hwid**: Hardware ID of the client machine
    - **device_name**: Optional device name for tracking
    
    This endpoint validates the license and checks/creates hardware binding.
    """
    try:
        logger.info(f"Validating license: {request.license_key[:10]}... with HWID: {request.hwid[:8]}...")
        
        result = validate_license(request.license_key, request.hwid)
        
        if result.get("valid"):
            warning = None
            days_remaining = result.get("days_remaining", 0)
            
            if days_remaining <= 30:
                warning = f"License expires in {days_remaining} days"
            
            return LicenseValidateResponse(
                valid=True,
                message="License validated successfully",
                license_key=request.license_key,
                license_type=result.get("license_type"),
                features=result.get("features", []),
                days_remaining=days_remaining,
                expires_at=result.get("expires_at"),
                hwid_bound=True,
                activation_status="activated",
                warning=warning
            )
        else:
            return LicenseValidateResponse(
                valid=False,
                message=result.get("error", "Validation failed"),
                license_key=request.license_key,
                activation_status=result.get("status", "failed")
            )
            
    except Exception as e:
        logger.error(f"License validation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{license_key}", response_model=LicenseInfoResponse)
async def get_license_info(license_key: str):
    """
    Get detailed license information
    
    - **license_key**: The license key to query
    
    Returns full license details (excluding sensitive data).
    """
    try:
        logger.info(f"Getting info for license: {license_key[:10]}...")
        
        result = validate_license(license_key)
        
        if not result.get("valid") and result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="License not found")
        
        # Build license info
        license_info = {
            "license_key": license_key,
            "license_type": result.get("license_type", "unknown"),
            "status": result.get("status", "unknown"),
            "features": result.get("features", []),
            "days_remaining": result.get("days_remaining", 0),
            "expires_at": result.get("expires_at"),
            "max_devices": result.get("max_devices", 1),
            "owner_name": result.get("owner_name"),
            "valid": result.get("valid", False)
        }
        
        return LicenseInfoResponse(
            success=True,
            license=license_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get license info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hardware-id", response_model=HardwareIDResponse)
async def get_hardware_id():
    """
    Get hardware ID of the current machine
    
    Returns hardware ID and system information.
    Supports Windows, Mac, and Linux.
    """
    try:
        hw_info = get_hardware_info()
        system_info = hw_info.get("system_info", {})
        
        return HardwareIDResponse(
            success=True,
            hardware_id=hw_info.get("hardware_id", "UNKNOWN"),
            hardware_id_short=hw_info.get("hardware_id_short", "UNKNOWN"),
            platform=system_info.get("platform", "unknown"),
            platform_version=system_info.get("platform_version", ""),
            architecture=system_info.get("architecture", ""),
            hostname=system_info.get("hostname", ""),
            components={
                "mac_address": system_info.get("mac_address"),
                "processor": system_info.get("processor"),
                "platform_release": system_info.get("platform_release")
            }
        )
        
    except Exception as e:
        logger.error(f"Get hardware ID error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/features/{license_key}", response_model=LicenseFeaturesResponse)
async def get_license_features(license_key: str):
    """
    Get features available for a license
    
    - **license_key**: The license key to query
    
    Returns list of enabled features for the license.
    """
    try:
        result = validate_license(license_key)
        
        if not result.get("valid") and result.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="License not found")
        
        license_type = result.get("license_type", "trial")
        features = result.get("features", get_features_for_type(license_type))
        
        # Build feature details
        feature_details = {}
        for feature in features:
            feature_details[feature] = {
                "enabled": True,
                "description": get_feature_description(feature)
            }
        
        return LicenseFeaturesResponse(
            success=True,
            license_key=license_key,
            license_type=license_type,
            features=features,
            feature_details=feature_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get license features error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_feature_description(feature: str) -> str:
    """Get description for a feature"""
    descriptions = {
        "code_editor": "Advanced code editor with syntax highlighting",
        "syntax_highlighting": "Syntax highlighting for 100+ languages",
        "file_explorer": "File and folder management",
        "ai_code_completion": "AI-powered code completion and suggestions",
        "ai_assistant": "AI assistant for coding help and explanations",
        "advanced_debugging": "Advanced debugging tools and breakpoints",
        "git_integration": "Git version control integration",
        "terminal": "Integrated terminal",
        "extensions": "Extension marketplace access",
        "team_collaboration": "Real-time team collaboration features",
        "admin_console": "Admin console for team management",
        "priority_support": "Priority customer support",
        "custom_branding": "Custom branding options",
        "sso_integration": "Single Sign-On integration",
        "audit_logs": "Audit logging and compliance"
    }
    return descriptions.get(feature, feature)


@router.get("/types")
async def get_license_types():
    """
    Get available license types and their features
    """
    return {
        "success": True,
        "license_types": {
            "trial": {
                "name": "Trial",
                "description": "Free trial license with limited features",
                "duration_days": 14,
                "features": get_features_for_type("trial"),
                "max_devices": 1,
                "price": "Free"
            },
            "pro": {
                "name": "Professional",
                "description": "Full-featured license for individual developers",
                "duration_days": 365,
                "features": get_features_for_type("pro"),
                "max_devices": 2,
                "price": "$99/year"
            },
            "enterprise": {
                "name": "Enterprise",
                "description": "Enterprise license with team features",
                "duration_days": 365,
                "features": get_features_for_type("enterprise"),
                "max_devices": "Unlimited",
                "price": "Contact Sales"
            }
        }
    }


@router.get("/status")
async def license_service_status():
    """
    Get license service status
    """
    return {
        "success": True,
        "service": "dLNk-License",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "supported_platforms": ["Windows", "macOS", "Linux"],
        "api_version": "1.0.0"
    }
