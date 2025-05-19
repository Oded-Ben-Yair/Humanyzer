"""
SSO Controller for handling Single Sign-On authentication flows.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, List, Any

from backend.auth.security import create_access_token, create_refresh_token

router = APIRouter(prefix="/sso", tags=["sso"])

@router.get("/providers")
async def get_sso_providers():
    """
    Get available SSO providers.
    
    Returns:
        List of available SSO providers
    """
    # For now, return an empty list as we don't have any SSO providers configured
    return {"providers": []}

@router.get("/login/{provider_id}")
async def sso_login(provider_id: str, request: Request):
    """
    Initiate SSO login flow.
    
    Args:
        provider_id: ID of the SSO provider
        request: Request object
        
    Returns:
        Redirect to SSO provider
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"SSO provider {provider_id} not implemented"
    )

@router.get("/callback/{provider_id}")
async def sso_callback(provider_id: str, request: Request):
    """
    Handle SSO callback.
    
    Args:
        provider_id: ID of the SSO provider
        request: Request object
        
    Returns:
        Access and refresh tokens
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"SSO provider {provider_id} not implemented"
    )
