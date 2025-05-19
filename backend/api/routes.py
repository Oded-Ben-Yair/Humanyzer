from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

router = APIRouter(tags=["general"])

@router.get("/status", response_model=Dict[str, Any])
async def get_status():
    """
    Get the current status of the API.
    """
    return {
        "status": "operational",
        "version": "1.0.0",
        "message": "Humanyze API is running"
    }

@router.get("/info", response_model=Dict[str, Any])
async def get_info():
    """
    Get information about the API.
    """
    return {
        "name": "Humanyze API",
        "description": "API for humanizing AI-generated content",
        "version": "1.0.0",
        "endpoints": [
            "/api/status",
            "/api/info",
            "/api/auth/login",
            "/api/auth/register"
        ]
    }
