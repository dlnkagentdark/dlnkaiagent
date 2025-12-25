"""
dLNk IDE - Auth & License API Server
FastAPI Application สำหรับระบบยืนยันตัวตนและ License

Version: 1.0.0
Author: AI-06 Auth & License API Developer
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'license'))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

# Import routers
from routes.auth import router as auth_router
from routes.license import router as license_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-API')


# ==================== Configuration ====================

class APIConfig:
    """API Configuration"""
    HOST: str = os.getenv('API_HOST', '0.0.0.0')
    PORT: int = int(os.getenv('API_PORT', '8000'))
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dlnk-ide-secret-key-change-in-production')
    JWT_ALGORITHM: str = 'HS256'
    JWT_EXPIRATION_HOURS: int = 24
    
    # Database
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', './data/licenses.db')
    
    # Admin notification
    ADMIN_EMAIL: str = os.getenv('ADMIN_EMAIL', 'admin@dlnk-ide.com')
    ADMIN_TELEGRAM_CHAT_ID: str = os.getenv('ADMIN_TELEGRAM_CHAT_ID', '')


config = APIConfig()


# ==================== Lifespan Events ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 dLNk IDE - Auth & License API Server Starting...")
    logger.info(f"   Host: {config.HOST}")
    logger.info(f"   Port: {config.PORT}")
    logger.info(f"   Debug: {config.DEBUG}")
    logger.info("=" * 60)
    
    # Initialize data directory
    data_dir = Path(config.DATABASE_PATH).parent
    data_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("🛑 dLNk IDE - Auth & License API Server Shutting down...")


# ==================== Create FastAPI App ====================

app = FastAPI(
    title="dLNk IDE - Auth & License API",
    description="""
## dLNk IDE Authentication & License Management API

API Server สำหรับระบบยืนยันตัวตนและจัดการ License ของ dLNk IDE

### Features:
- **Authentication**: Login, Register, JWT Token management
- **License Management**: Verify, Generate, Extend licenses
- **Hardware ID**: Cross-platform HWID support (Windows, Mac, Linux)

### Authentication Flow:
1. Client sends `license_key` and `hwid` to `/api/auth/login`
2. Server validates license and returns JWT token
3. Client uses JWT token for subsequent requests

### License Verification:
- Supports both online and offline verification
- Hardware binding for license protection
- Multi-device support for enterprise licenses
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)


# ==================== CORS Middleware ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Allow all origins in development
        "vscode-webview://*",
        "file://*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Request Logging Middleware ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = datetime.now()
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    
    # Log request details
    logger.info(
        f"[{client_ip}] {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Time: {process_time:.3f}s"
    )
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# ==================== Exception Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )


# ==================== Include Routers ====================

app.include_router(auth_router, prefix="/api")
app.include_router(license_router, prefix="/api")


# ==================== Root Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - Server information
    """
    return {
        "name": "dLNk IDE - Auth & License API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "auth": "/api/auth",
            "license": "/api/license"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "dLNk-Auth-License-API",
        "timestamp": datetime.now().isoformat(),
        "uptime": "OK"
    }


@app.get("/api", tags=["API Info"])
async def api_info():
    """
    API endpoints information
    """
    return {
        "name": "dLNk IDE - Auth & License API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "login": {
                    "method": "POST",
                    "path": "/api/auth/login",
                    "description": "Login with license_key and hwid, returns JWT token"
                },
                "register": {
                    "method": "POST",
                    "path": "/api/auth/register",
                    "description": "Register new user, sends notification to admin"
                },
                "verify_token": {
                    "method": "GET",
                    "path": "/api/auth/verify",
                    "description": "Verify JWT token validity"
                },
                "refresh_token": {
                    "method": "POST",
                    "path": "/api/auth/refresh",
                    "description": "Refresh JWT token"
                }
            },
            "license": {
                "verify": {
                    "method": "GET",
                    "path": "/api/license/verify/{license_key}",
                    "description": "Verify license key validity"
                },
                "validate": {
                    "method": "POST",
                    "path": "/api/license/validate",
                    "description": "Validate license with hardware ID"
                },
                "info": {
                    "method": "GET",
                    "path": "/api/license/info/{license_key}",
                    "description": "Get license information"
                },
                "hardware_id": {
                    "method": "GET",
                    "path": "/api/license/hardware-id",
                    "description": "Get current hardware ID"
                }
            }
        }
    }


# ==================== Main Entry Point ====================

def run_server(host: str = None, port: int = None, reload: bool = False):
    """Run the API server"""
    host = host or config.HOST
    port = port or config.PORT
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk IDE - Auth & License API Server')
    parser.add_argument('--host', default=config.HOST, help='Host to bind')
    parser.add_argument('--port', type=int, default=config.PORT, help='Port to bind')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
