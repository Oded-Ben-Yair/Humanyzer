"""
API routes for feature flag management.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from app.auth.dependencies import get_current_user, require_admin
from app.services.feature_flags import feature_flag_service
from app.models.feature_flag import (
    FeatureFlag,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureOverride,
    FeatureOverrideCreate,
    FeatureFlagResponse,
    FeatureFlagListResponse,
    FeatureOverrideResponse,
    FeatureStatusResponse
)
from app.db.subscriptions import get_subscription_by_user_id
from app.models.subscription import SubscriptionTier
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

router = APIRouter(prefix="/feature-flags", tags=["feature-flags"])
logger = logging.getLogger(__name__)


@router.get("", response_model=FeatureFlagListResponse)
async def list_feature_flags(
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(require_admin)
):
    """
    List all feature flags.
    
    Args:
        current_user: Current authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        List of feature flags
    """
    try:
        flags = await feature_flag_service["list_feature_flags"]()
        return FeatureFlagListResponse(flags=flags)
    except Exception as e:
        logger.error(f"Error listing feature flags: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing feature flags: {str(e)}"
        )


@router.get("/{flag_key}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    flag_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(require_admin)
):
    """
    Get a feature flag by key.
    
    Args:
        flag_key: Feature flag key
        current_user: Current authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        Feature flag details
    """
    try:
        flag = await feature_flag_service["get_feature_flag"](flag_key)
        
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{flag_key}' not found"
            )
        
        return FeatureFlagResponse(**flag)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature flag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting feature flag: {str(e)}"
        )


@router.post("", response_model=FeatureFlagResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(require_admin)
):
    """
    Create a new feature flag.
    
    Args:
        flag_data: Feature flag data
        current_user: Current authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        Created feature flag
    """
    try:
        flag = await feature_flag_service["create_feature_flag"](
            key=flag_data.key,
            name=flag_data.name,
            description=flag_data.description,
            enabled=flag_data.enabled,
            min_subscription_tier=flag_data.min_subscription_tier,
            percentage_rollout=flag_data.percentage_rollout,
            start_date=flag_data.start_date,
            end_date=flag_data.end_date,
            metadata=flag_data.metadata
        )
        
        return FeatureFlagResponse(**flag)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating feature flag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating feature flag: {str(e)}"
        )


@router.put("/{flag_key}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_key: str,
    flag_data: FeatureFlagUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(require_admin)
):
    """
    Update a feature flag.
    
    Args:
        flag_key: Feature flag key
        flag_data: Feature flag data to update
        current_user: Current authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        Updated feature flag
    """
    try:
        # Check if flag exists
        existing_flag = await feature_flag_service["get_feature_flag"](flag_key)
        
        if not existing_flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{flag_key}' not found"
            )
        
        # Update flag
        flag = await feature_flag_service["update_feature_flag"](
            key=flag_key,
            name=flag_data.name,
            description=flag_data.description,
            enabled=flag_data.enabled,
            min_subscription_tier=flag_data.min_subscription_tier,
            percentage_rollout=flag_data.percentage_rollout,
            start_date=flag_data.start_date,
            end_date=flag_data.end_date,
            metadata=flag_data.metadata
        )
        
        return FeatureFlagResponse(**flag)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature flag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating feature flag: {str(e)}"
        )


@router.delete("/{flag_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_flag(
    flag_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(require_admin)
):
    """
    Delete a feature flag.
    
    Args:
        flag_key: Feature flag key
        current_user: Current authenticated user
        is_admin: Whether the user is an admin
    """
    try:
        # Check if flag exists
        existing_flag = await feature_flag_service["get_feature_flag"](flag_key)
        
        if not existing_flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{flag_key}' not found"
            )
        
        # Delete flag
        deleted = await feature_flag_service["delete_feature_flag"](flag_key)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete feature flag '{flag_key}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature flag: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting feature flag: {str(e)}"
        )


@router.post("/overrides", response_model=FeatureOverrideResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_override(
    override_data: FeatureOverrideCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(require_admin)
):
    """
    Create a user-specific feature flag override.
    
    Args:
        override_data: Feature override data
        current_user: Current authenticated user
        is_admin: Whether the user is an admin
        
    Returns:
        Created feature override
    """
    try:
        # Check if flag exists
        flag = await feature_flag_service["get_feature_flag"](override_data.flag_key)
        
        if not flag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature flag '{override_data.flag_key}' not found"
            )
        
        # Create override
        override = await feature_flag_service["create_feature_override"](
            flag_key=override_data.flag_key,
            user_id=override_data.user_id,
            enabled=override_data.enabled
        )
        
        return FeatureOverrideResponse(**override)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating feature override: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating feature override: {str(e)}"
        )


@router.delete("/overrides/{flag_key}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_override(
    flag_key: str,
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    is_admin: bool = Depends(require_admin)
):
    """
    Delete a user-specific feature flag override.
    
    Args:
        flag_key: Feature flag key
        user_id: User ID
        current_user: Current authenticated user
        is_admin: Whether the user is an admin
    """
    try:
        # Check if override exists
        override = await feature_flag_service["get_feature_override"](flag_key, user_id)
        
        if not override:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Feature override for flag '{flag_key}' and user '{user_id}' not found"
            )
        
        # Delete override
        deleted = await feature_flag_service["delete_feature_override"](flag_key, user_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete feature override for flag '{flag_key}' and user '{user_id}'"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature override: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting feature override: {str(e)}"
        )


@router.get("/status/{flag_key}", response_model=FeatureStatusResponse)
async def check_feature_status(
    flag_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Check if a feature flag is enabled for the current user.
    
    Args:
        flag_key: Feature flag key
        current_user: Current authenticated user
        
    Returns:
        Feature status
    """
    try:
        # Get user's subscription tier
        subscription = await get_subscription_by_user_id(current_user["id"])
        tier = SubscriptionTier.FREE
        
        if subscription:
            tier = SubscriptionTier(subscription["tier"])
        
        # Check if feature is enabled
        enabled = await feature_flag_service["is_feature_enabled"](
            flag_key=flag_key,
            user_id=current_user["id"],
            subscription_tier=tier
        )
        
        return FeatureStatusResponse(
            flag_key=flag_key,
            enabled=enabled,
            user_id=current_user["id"],
            subscription_tier=tier.value
        )
    except Exception as e:
        logger.error(f"Error checking feature status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking feature status: {str(e)}"
        )
