"""
dLNk License Server
FastAPI Server สำหรับ License และ Authentication API
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from datetime import datetime

from config import get_config
from api.routes.license import router as license_router
from api.routes.auth import router as auth_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-Server')

config = get_config()

# Create FastAPI app
app = FastAPI(
    title="dLNk License & Auth Server",
    description="API Server สำหรับระบบ License และ Authentication ของ dLNk IDE",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Middleware ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.now()
    
    response = await call_next(request)
    
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
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
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500
        }
    )


# ==================== Include Routers ====================

app.include_router(license_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


# ==================== Root Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "dLNk License & Auth Server",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "license": "/api/license",
            "auth": "/api/auth"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": "dLNk License & Auth API",
        "version": "1.0.0",
        "endpoints": {
            "license": {
                "generate": "POST /api/license/generate",
                "validate": "POST /api/license/validate",
                "extend": "POST /api/license/extend",
                "revoke": "POST /api/license/revoke",
                "info": "GET /api/license/info/{license_key}",
                "list": "GET /api/license/list",
                "stats": "GET /api/license/stats"
            },
            "auth": {
                "login": "POST /api/auth/login",
                "register": "POST /api/auth/register",
                "logout": "POST /api/auth/logout",
                "me": "GET /api/auth/me",
                "change_password": "POST /api/auth/change-password",
                "sessions": "GET /api/auth/sessions"
            }
        }
    }


# ==================== Startup/Shutdown Events ====================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("=" * 50)
    logger.info("dLNk License & Auth Server Starting...")
    logger.info(f"Host: {config.API_HOST}")
    logger.info(f"Port: {config.API_PORT}")
    logger.info(f"Database: {config.DATABASE_PATH}")
    logger.info("=" * 50)
    
    # Initialize directories
    config.init_directories()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("dLNk License & Auth Server Shutting down...")


# ==================== Main ====================

def run_server(host: str = None, port: int = None):
    """Run the server"""
    host = host or config.API_HOST
    port = port or config.API_PORT
    
    uvicorn.run(
        "api.server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk License & Auth Server')
    parser.add_argument('--host', default=config.API_HOST, help='Host to bind')
    parser.add_argument('--port', type=int, default=config.API_PORT, help='Port to bind')
    
    args = parser.parse_args()
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
