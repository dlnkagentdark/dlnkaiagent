"""
License API Routes
API endpoints สำหรับจัดการ License
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

import sys
sys.path.append('../..')
from license import (
    license_generator, license_validator, license_storage,
    LicenseType, LicenseStatus, LicenseData,
    get_hardware_id
)
from utils.helpers import get_client_ip

logger = logging.getLogger('dLNk-LicenseAPI')
router = APIRouter(prefix="/license", tags=["License"])


# ==================== Request/Response Models ====================

class GenerateLicenseRequest(BaseModel):
    """Request สำหรับสร้าง License"""
    user_id: str
    license_type: str = Field(default="pro", description="trial, pro, or enterprise")
    duration_days: int = Field(default=365, ge=1, le=3650)
    features: Optional[List[str]] = None
    hardware_id: Optional[str] = None
    max_devices: int = Field(default=1, ge=1, le=100)
    owner_name: str = ""
    email: str = ""


class ValidateLicenseRequest(BaseModel):
    """Request สำหรับตรวจสอบ License"""
    license_key: str
    hardware_id: Optional[str] = None


class ExtendLicenseRequest(BaseModel):
    """Request สำหรับขยายอายุ License"""
    license_key: str
    days: int = Field(ge=1, le=3650)


class RevokeLicenseRequest(BaseModel):
    """Request สำหรับเพิกถอน License"""
    license_key: str
    reason: str = ""


class LicenseResponse(BaseModel):
    """Response สำหรับ License"""
    success: bool
    message: str
    license_key: Optional[str] = None
    encrypted_data: Optional[str] = None
    license_data: Optional[dict] = None


class ValidationResponse(BaseModel):
    """Response สำหรับการตรวจสอบ"""
    valid: bool
    message: str
    features: List[str] = []
    days_remaining: int = 0
    license_type: Optional[str] = None
    warning: Optional[str] = None


# ==================== API Endpoints ====================

@router.post("/generate", response_model=LicenseResponse)
async def generate_license(request: GenerateLicenseRequest, req: Request):
    """
    สร้าง License Key ใหม่
    
    - **user_id**: ID ของผู้ใช้
    - **license_type**: ประเภท License (trial, pro, enterprise)
    - **duration_days**: จำนวนวันที่ใช้งานได้
    - **features**: รายการ features (ถ้าไม่ระบุจะใช้ค่าเริ่มต้นตามประเภท)
    - **hardware_id**: Hardware ID สำหรับผูกเครื่อง (optional)
    """
    try:
        # Generate license
        license_key, encrypted_data = license_generator.generate(
            user_id=request.user_id,
            license_type=request.license_type,
            duration_days=request.duration_days,
            features=request.features,
            hardware_id=request.hardware_id,
            max_devices=request.max_devices,
            owner_name=request.owner_name,
            email=request.email
        )
        
        # Create license data for storage
        license_data = LicenseData(
            license_id=license_key,  # Will be replaced by actual ID
            user_id=request.user_id,
            license_type=request.license_type,
            created_at="",  # Will be set by storage
            expires_at="",  # Will be set by storage
            hardware_id=request.hardware_id,
            features=request.features or [],
            max_devices=request.max_devices,
            owner_name=request.owner_name,
            email=request.email
        )
        
        # Store in database
        from datetime import datetime, timedelta
        license_data.created_at = datetime.now().isoformat()
        license_data.expires_at = (datetime.now() + timedelta(days=request.duration_days)).isoformat()
        license_data.license_id = license_key.replace("DLNK-", "")
        
        license_storage.store_license(license_key, license_data, encrypted_data)
        
        logger.info(f"License generated: {license_key} for user {request.user_id}")
        
        return LicenseResponse(
            success=True,
            message="License generated successfully",
            license_key=license_key,
            encrypted_data=encrypted_data,
            license_data={
                'license_type': request.license_type,
                'duration_days': request.duration_days,
                'features': request.features or license_generator._get_default_features(request.license_type),
                'max_devices': request.max_devices
            }
        )
        
    except Exception as e:
        logger.error(f"License generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=ValidationResponse)
async def validate_license(request: ValidateLicenseRequest, req: Request):
    """
    ตรวจสอบ License Key
    
    - **license_key**: License key หรือ encrypted license string
    - **hardware_id**: Hardware ID ของเครื่องปัจจุบัน (optional)
    """
    try:
        hardware_id = request.hardware_id or get_hardware_id()
        ip_address = get_client_ip(req)
        
        result = license_validator.validate(
            license_key=request.license_key,
            hardware_id=hardware_id,
            ip_address=ip_address
        )
        
        return ValidationResponse(
            valid=result.valid,
            message=result.error or "License is valid",
            features=result.features or [],
            days_remaining=result.days_remaining,
            license_type=result.license_data.license_type if result.license_data else None,
            warning=result.warning
        )
        
    except Exception as e:
        logger.error(f"License validation failed: {e}")
        return ValidationResponse(
            valid=False,
            message=f"Validation error: {str(e)}"
        )


@router.post("/extend", response_model=LicenseResponse)
async def extend_license(request: ExtendLicenseRequest):
    """
    ขยายอายุ License
    
    - **license_key**: License key
    - **days**: จำนวนวันที่ต้องการขยาย
    """
    try:
        success = license_storage.extend_license(request.license_key, request.days)
        
        if success:
            return LicenseResponse(
                success=True,
                message=f"License extended by {request.days} days",
                license_key=request.license_key
            )
        else:
            raise HTTPException(status_code=404, detail="License not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License extension failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revoke", response_model=LicenseResponse)
async def revoke_license(request: RevokeLicenseRequest):
    """
    เพิกถอน License
    
    - **license_key**: License key
    - **reason**: เหตุผลในการเพิกถอน
    """
    try:
        success = license_storage.revoke_license(
            license_key=request.license_key,
            reason=request.reason
        )
        
        if success:
            return LicenseResponse(
                success=True,
                message="License revoked successfully",
                license_key=request.license_key
            )
        else:
            raise HTTPException(status_code=404, detail="License not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License revocation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info/{license_key}")
async def get_license_info(license_key: str):
    """
    ดึงข้อมูล License
    """
    license_data = license_storage.get_license(license_key)
    
    if not license_data:
        raise HTTPException(status_code=404, detail="License not found")
    
    # Remove sensitive data
    license_data.pop('encrypted_data', None)
    
    return {
        "success": True,
        "license": license_data
    }


@router.get("/user/{user_id}")
async def get_user_licenses(user_id: str):
    """
    ดึง License ทั้งหมดของ user
    """
    licenses = license_storage.get_licenses_by_user(user_id)
    
    # Remove sensitive data
    for lic in licenses:
        lic.pop('encrypted_data', None)
    
    return {
        "success": True,
        "count": len(licenses),
        "licenses": licenses
    }


@router.get("/list")
async def list_licenses(status: Optional[str] = None, limit: int = 100):
    """
    ดึงรายการ License ทั้งหมด
    """
    licenses = license_storage.get_all_licenses(status)[:limit]
    
    # Remove sensitive data
    for lic in licenses:
        lic.pop('encrypted_data', None)
    
    return {
        "success": True,
        "count": len(licenses),
        "licenses": licenses
    }


@router.get("/stats")
async def get_license_stats():
    """
    ดึงสถิติ License
    """
    stats = license_storage.get_statistics()
    
    return {
        "success": True,
        "stats": stats
    }


@router.get("/activations/{license_key}")
async def get_license_activations(license_key: str):
    """
    ดึงรายการ activations ของ License
    """
    activations = license_storage.get_activations(license_key)
    
    return {
        "success": True,
        "count": len(activations),
        "activations": activations
    }


@router.get("/hardware-id")
async def get_current_hardware_id():
    """
    ดึง Hardware ID ของเครื่องปัจจุบัน
    """
    from license.hardware import HardwareID
    
    return {
        "success": True,
        "hardware_id": HardwareID.generate(),
        "hardware_id_short": HardwareID.generate_short(),
        "system_info": HardwareID.get_system_info()
    }


@router.post("/generate-encrypted")
async def generate_encrypted_license(
    days_valid: int = 30,
    owner: str = "User",
    features: Optional[List[str]] = None
):
    """
    สร้าง Encrypted License (compatible กับระบบเดิม)
    """
    from license.generator import generate_encrypted_license as gen_enc
    
    encrypted = gen_enc(days_valid=days_valid, owner=owner, features=features)
    
    return {
        "success": True,
        "encrypted_license": encrypted
    }
