"""
Middleware for checking feature flag access.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Callable, Dict, Any, Optional, List
import logging
from app.services.feature_flags import is_feature_enabled
from app.db.subscriptions import get_subscription_by_user_id
from app.models.subscription import SubscriptionTier
import functools
import time

logger = logging.getLogger(__name__)

# Cache for feature flag checks to improve performance
_feature_flag_cache = {}
_cache_ttl = 60  # Cache TTL in seconds


async def _get_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extract user information from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User information if available, None otherwise
    """
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user"):
        return request.state.user
    
    # If not available, try to get from session
    if "user" in request.session:
        return request.session["user"]
    
    return None


async def _get_subscription_tier(user_id: str) -> SubscriptionTier:
    """
    Get subscription tier for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Subscription tier
    """
    subscription = await get_subscription_by_user_id(user_id)
    
    if not subscription:
        return SubscriptionTier.FREE
    
    return SubscriptionTier(subscription["tier"])


def require_feature(flag_key: str):
    """
    Decorator to require a feature flag for an endpoint.
    
    Args:
        flag_key: Feature flag key
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                for _, arg in kwargs.items():
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                logger.error(f"No request object found for {func.__name__}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
            
            # Get user from request
            user = await _get_user_from_request(request)
            
            # If no user, feature is disabled
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Feature not available"}
                )
            
            user_id = user.get("id")
            
            # Check cache first
            cache_key = f"{flag_key}:{user_id}"
            cache_entry = _feature_flag_cache.get(cache_key)
            
            if cache_entry:
                timestamp, is_enabled = cache_entry
                if time.time() - timestamp < _cache_ttl:
                    if not is_enabled:
                        return JSONResponse(
                            status_code=status.HTTP_403_FORBIDDEN,
                            content={"detail": "Feature not available"}
                        )
                    return await func(*args, **kwargs)
            
            # Get subscription tier
            subscription_tier = await _get_subscription_tier(user_id)
            
            # Check if feature is enabled
            enabled = await is_feature_enabled(
                flag_key=flag_key,
                user_id=user_id,
                subscription_tier=subscription_tier
            )
            
            # Update cache
            _feature_flag_cache[cache_key] = (time.time(), enabled)
            
            if not enabled:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Feature not available"}
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


def clear_feature_flag_cache():
    """Clear the feature flag cache."""
    global _feature_flag_cache
    _feature_flag_cache = {}


def set_cache_ttl(ttl: int):
    """
    Set the cache TTL.
    
    Args:
        ttl: Cache TTL in seconds
    """
    global _cache_ttl
    _cache_ttl = ttl
