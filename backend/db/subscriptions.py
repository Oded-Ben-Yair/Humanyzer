"""
Database operations for subscription management.
This module provides functions to create, retrieve, update, and delete subscriptions.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import json
from pathlib import Path
from app.models.subscription import (
    SubscriptionStatus,
    SubscriptionTier,
    SubscriptionCreate,
    SubscriptionUpdate
)

# Path to the subscriptions database file
DB_DIR = Path(os.getenv("DB_DIR", "app/db/data"))
SUBSCRIPTIONS_FILE = DB_DIR / "subscriptions.json"
SUBSCRIPTION_USAGE_FILE = DB_DIR / "subscription_usage.json"

# Ensure the data directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

# Initialize subscriptions database if it doesn't exist
if not SUBSCRIPTIONS_FILE.exists():
    with open(SUBSCRIPTIONS_FILE, "w") as f:
        json.dump([], f)

# Initialize subscription usage database if it doesn't exist
if not SUBSCRIPTION_USAGE_FILE.exists():
    with open(SUBSCRIPTION_USAGE_FILE, "w") as f:
        json.dump([], f)


async def _read_subscriptions() -> List[Dict[str, Any]]:
    """Read all subscriptions from the database."""
    with open(SUBSCRIPTIONS_FILE, "r") as f:
        return json.load(f)


async def _write_subscriptions(subscriptions: List[Dict[str, Any]]) -> None:
    """Write subscriptions to the database."""
    with open(SUBSCRIPTIONS_FILE, "w") as f:
        json.dump(subscriptions, f, default=str)


async def _read_subscription_usage() -> List[Dict[str, Any]]:
    """Read all subscription usage from the database."""
    with open(SUBSCRIPTION_USAGE_FILE, "r") as f:
        return json.load(f)


async def _write_subscription_usage(usage: List[Dict[str, Any]]) -> None:
    """Write subscription usage to the database."""
    with open(SUBSCRIPTION_USAGE_FILE, "w") as f:
        json.dump(usage, f, default=str)


async def get_subscription_by_id(subscription_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a subscription by ID.
    
    Args:
        subscription_id: The subscription ID
        
    Returns:
        The subscription if found, None otherwise
    """
    subscriptions = await _read_subscriptions()
    for subscription in subscriptions:
        if subscription["id"] == subscription_id:
            return subscription
    return None


async def get_subscription_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a subscription by user ID.
    
    Args:
        user_id: The user ID
        
    Returns:
        The subscription if found, None otherwise
    """
    subscriptions = await _read_subscriptions()
    for subscription in subscriptions:
        if subscription["user_id"] == user_id:
            return subscription
    return None


async def get_subscription_by_stripe_id(stripe_subscription_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a subscription by Stripe subscription ID.
    
    Args:
        stripe_subscription_id: The Stripe subscription ID
        
    Returns:
        The subscription if found, None otherwise
    """
    subscriptions = await _read_subscriptions()
    for subscription in subscriptions:
        if subscription.get("stripe_subscription_id") == stripe_subscription_id:
            return subscription
    return None


async def get_subscription_by_stripe_customer_id(stripe_customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a subscription by Stripe customer ID.
    
    Args:
        stripe_customer_id: The Stripe customer ID
        
    Returns:
        The subscription if found, None otherwise
    """
    subscriptions = await _read_subscriptions()
    for subscription in subscriptions:
        if subscription.get("stripe_customer_id") == stripe_customer_id:
            return subscription
    return None


async def create_subscription(subscription_data: SubscriptionCreate) -> Dict[str, Any]:
    """
    Create a new subscription.
    
    Args:
        subscription_data: Subscription data to create
        
    Returns:
        The created subscription
    """
    subscriptions = await _read_subscriptions()
    
    # Check if user already has a subscription
    for subscription in subscriptions:
        if subscription["user_id"] == subscription_data.user_id:
            # Update existing subscription instead of creating a new one
            subscription_dict = subscription_data.model_dump(exclude_unset=True)
            for key, value in subscription_dict.items():
                subscription[key] = value
            
            subscription["updated_at"] = datetime.utcnow()
            
            await _write_subscriptions(subscriptions)
            return subscription
    
    # Create new subscription
    subscription_dict = subscription_data.model_dump()
    subscription_dict["id"] = str(uuid.uuid4())
    subscription_dict["created_at"] = datetime.utcnow()
    subscription_dict["updated_at"] = datetime.utcnow()
    subscription_dict["status"] = subscription_data.status.value
    subscription_dict["tier"] = subscription_data.tier.value
    subscription_dict["cancel_at_period_end"] = False
    
    subscriptions.append(subscription_dict)
    await _write_subscriptions(subscriptions)
    
    return subscription_dict


async def update_subscription(subscription_id: str, subscription_data: SubscriptionUpdate) -> Optional[Dict[str, Any]]:
    """
    Update a subscription.
    
    Args:
        subscription_id: The subscription ID
        subscription_data: Subscription data to update
        
    Returns:
        The updated subscription if found, None otherwise
    """
    subscriptions = await _read_subscriptions()
    
    for i, subscription in enumerate(subscriptions):
        if subscription["id"] == subscription_id:
            # Update fields
            update_data = subscription_data.model_dump(exclude_unset=True)
            
            for key, value in update_data.items():
                if key in ["status", "tier"] and value is not None:
                    subscription[key] = value.value
                else:
                    subscription[key] = value
            
            # Update timestamp
            subscription["updated_at"] = datetime.utcnow()
            
            subscriptions[i] = subscription
            await _write_subscriptions(subscriptions)
            
            return subscription
    
    return None


async def delete_subscription(subscription_id: str) -> bool:
    """
    Delete a subscription.
    
    Args:
        subscription_id: The subscription ID
        
    Returns:
        True if the subscription was deleted, False otherwise
    """
    subscriptions = await _read_subscriptions()
    
    for i, subscription in enumerate(subscriptions):
        if subscription["id"] == subscription_id:
            subscriptions.pop(i)
            await _write_subscriptions(subscriptions)
            return True
    
    return False


async def list_subscriptions() -> List[Dict[str, Any]]:
    """
    List all subscriptions.
    
    Returns:
        List of all subscriptions
    """
    return await _read_subscriptions()


async def get_subscription_usage(subscription_id: str, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
    """
    Get subscription usage for a specific period.
    
    Args:
        subscription_id: The subscription ID
        period_start: Start of the period
        period_end: End of the period
        
    Returns:
        Subscription usage data
    """
    usage_records = await _read_subscription_usage()
    
    # Find existing usage record for the period
    for record in usage_records:
        if (record["subscription_id"] == subscription_id and
            datetime.fromisoformat(record["period_start"]) == period_start and
            datetime.fromisoformat(record["period_end"]) == period_end):
            return record
    
    # Create new usage record if not found
    subscription = await get_subscription_by_id(subscription_id)
    if not subscription:
        raise ValueError(f"Subscription not found: {subscription_id}")
    
    new_record = {
        "id": str(uuid.uuid4()),
        "subscription_id": subscription_id,
        "user_id": subscription["user_id"],
        "characters_used": 0,
        "requests_made": 0,
        "period_start": period_start,
        "period_end": period_end,
        "updated_at": datetime.utcnow()
    }
    
    usage_records.append(new_record)
    await _write_subscription_usage(usage_records)
    
    return new_record


async def update_subscription_usage(
    subscription_id: str,
    period_start: datetime,
    period_end: datetime,
    characters_used: int = 0,
    requests_made: int = 0
) -> Dict[str, Any]:
    """
    Update subscription usage for a specific period.
    
    Args:
        subscription_id: The subscription ID
        period_start: Start of the period
        period_end: End of the period
        characters_used: Number of characters used to add
        requests_made: Number of requests made to add
        
    Returns:
        Updated subscription usage data
    """
    usage_records = await _read_subscription_usage()
    
    # Find existing usage record for the period
    for i, record in enumerate(usage_records):
        if (record["subscription_id"] == subscription_id and
            datetime.fromisoformat(record["period_start"]) == period_start and
            datetime.fromisoformat(record["period_end"]) == period_end):
            
            # Update usage
            record["characters_used"] += characters_used
            record["requests_made"] += requests_made
            record["updated_at"] = datetime.utcnow()
            
            usage_records[i] = record
            await _write_subscription_usage(usage_records)
            
            return record
    
    # Create new usage record if not found
    return await get_subscription_usage(subscription_id, period_start, period_end)


async def get_subscription_features(tier: SubscriptionTier) -> Dict[str, Any]:
    """
    Get features for a subscription tier.
    
    Args:
        tier: The subscription tier
        
    Returns:
        Features for the subscription tier
    """
    features = {
        SubscriptionTier.FREE: {
            "max_characters_per_month": 5000,
            "max_requests_per_day": 5,
            "custom_profiles": False,
            "priority_processing": False,
            "advanced_analytics": False,
            "api_access": False,
            "dedicated_support": False,
            "feature_flags": {}
        },
        SubscriptionTier.BASIC: {
            "max_characters_per_month": 50000,
            "max_requests_per_day": 20,
            "custom_profiles": True,
            "priority_processing": False,
            "advanced_analytics": False,
            "api_access": False,
            "dedicated_support": False,
            "feature_flags": {}
        },
        SubscriptionTier.PRO: {
            "max_characters_per_month": 200000,
            "max_requests_per_day": 100,
            "custom_profiles": True,
            "priority_processing": True,
            "advanced_analytics": True,
            "api_access": True,
            "dedicated_support": False,
            "feature_flags": {}
        },
        SubscriptionTier.ENTERPRISE: {
            "max_characters_per_month": 1000000,
            "max_requests_per_day": 500,
            "custom_profiles": True,
            "priority_processing": True,
            "advanced_analytics": True,
            "api_access": True,
            "dedicated_support": True,
            "feature_flags": {}
        }
    }
    
    # Get feature flags for this tier
    try:
        from app.services.feature_flags import feature_flag_service
        
        # Get all feature flags
        all_flags = await feature_flag_service["list_feature_flags"]()
        
        # Filter flags for this tier
        tier_level = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.ENTERPRISE: 3
        }.get(tier, 0)
        
        for flag in all_flags:
            min_tier = flag.get("min_subscription_tier")
            
            if min_tier:
                min_tier_level = {
                    "free": 0,
                    "basic": 1,
                    "pro": 2,
                    "enterprise": 3
                }.get(min_tier, 0)
                
                # Add flag to features if tier level is sufficient
                if tier_level >= min_tier_level and flag.get("enabled", False):
                    features[tier]["feature_flags"][flag["key"]] = True
            elif flag.get("enabled", False):
                # If no min_tier specified, add to all tiers if enabled
                features[tier]["feature_flags"][flag["key"]] = True
    except (ImportError, Exception) as e:
        # If feature flag service not available, continue without flags
        pass
    
    return features.get(tier, features[SubscriptionTier.FREE])


async def check_subscription_limit(user_id: str, character_count: int = 0) -> Dict[str, Any]:
    """
    Check if a user has reached their subscription limits.
    
    Args:
        user_id: The user ID
        character_count: Number of characters to check
        
    Returns:
        Dictionary with limit information
    """
    subscription = await get_subscription_by_user_id(user_id)
    
    # Default to FREE tier if no subscription found
    if not subscription:
        tier = SubscriptionTier.FREE
        features = await get_subscription_features(tier)
        return {
            "allowed": character_count <= features["max_characters_per_month"],
            "tier": tier.value,
            "limit": features["max_characters_per_month"],
            "used": character_count,
            "remaining": features["max_characters_per_month"] - character_count
        }
    
    # Check if subscription is active
    if subscription["status"] != SubscriptionStatus.ACTIVE.value:
        return {
            "allowed": False,
            "tier": subscription["tier"],
            "reason": f"Subscription status is {subscription['status']}"
        }
    
    # Get subscription features
    tier = SubscriptionTier(subscription["tier"])
    features = await get_subscription_features(tier)
    
    # Get current period
    now = datetime.utcnow()
    period_start = subscription.get("current_period_start", now)
    period_end = subscription.get("current_period_end", now)
    
    if isinstance(period_start, str):
        period_start = datetime.fromisoformat(period_start)
    if isinstance(period_end, str):
        period_end = datetime.fromisoformat(period_end)
    
    # Get usage for current period
    usage = await get_subscription_usage(subscription["id"], period_start, period_end)
    
    # Check character limit
    total_characters = usage["characters_used"] + character_count
    characters_allowed = total_characters <= features["max_characters_per_month"]
    
    # Check request limit
    requests_allowed = usage["requests_made"] < features["max_requests_per_day"]
    
    return {
        "allowed": characters_allowed and requests_allowed,
        "tier": tier.value,
        "character_limit": features["max_characters_per_month"],
        "characters_used": usage["characters_used"],
        "characters_remaining": features["max_characters_per_month"] - usage["characters_used"],
        "request_limit": features["max_requests_per_day"],
        "requests_used": usage["requests_made"],
        "requests_remaining": features["max_requests_per_day"] - usage["requests_made"]
    }
