"""
Feature flag service for controlling feature access based on subscription tiers,
percentage rollouts, user-specific overrides, and time-based activations.
"""
import logging
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import os
import json
from pathlib import Path
from app.models.subscription import SubscriptionTier

# Path to the feature flags database file
DB_DIR = Path(os.getenv("DB_DIR", os.path.join(os.path.dirname(__file__), "..", "db", "data")))
FEATURE_FLAGS_FILE = DB_DIR / "feature_flags.json"
FEATURE_OVERRIDES_FILE = DB_DIR / "feature_overrides.json"

# Print the paths for debugging
print(f"Feature flags file path: {FEATURE_FLAGS_FILE}")
print(f"Feature overrides file path: {FEATURE_OVERRIDES_FILE}")

# Ensure the data directory exists
DB_DIR.mkdir(parents=True, exist_ok=True)

# Initialize feature flags database if it doesn't exist
if not FEATURE_FLAGS_FILE.exists():
    with open(FEATURE_FLAGS_FILE, "w") as f:
        json.dump([], f)

# Initialize feature overrides database if it doesn't exist
if not FEATURE_OVERRIDES_FILE.exists():
    with open(FEATURE_OVERRIDES_FILE, "w") as f:
        json.dump([], f)

logger = logging.getLogger(__name__)


async def _read_feature_flags() -> List[Dict[str, Any]]:
    """Read all feature flags from the database."""
    with open(FEATURE_FLAGS_FILE, "r") as f:
        return json.load(f)


async def _write_feature_flags(flags: List[Dict[str, Any]]) -> None:
    """Write feature flags to the database."""
    with open(FEATURE_FLAGS_FILE, "w") as f:
        json.dump(flags, f, default=str)


async def _read_feature_overrides() -> List[Dict[str, Any]]:
    """Read all feature overrides from the database."""
    with open(FEATURE_OVERRIDES_FILE, "r") as f:
        return json.load(f)


async def _write_feature_overrides(overrides: List[Dict[str, Any]]) -> None:
    """Write feature overrides to the database."""
    with open(FEATURE_OVERRIDES_FILE, "w") as f:
        json.dump(overrides, f, default=str)


async def get_feature_flag(flag_key: str) -> Optional[Dict[str, Any]]:
    """
    Get a feature flag by key.
    
    Args:
        flag_key: The feature flag key
        
    Returns:
        The feature flag if found, None otherwise
    """
    flags = await _read_feature_flags()
    for flag in flags:
        if flag["key"] == flag_key:
            return flag
    return None


async def create_feature_flag(
    key: str,
    name: str,
    description: str,
    enabled: bool = True,
    min_subscription_tier: Optional[SubscriptionTier] = None,
    percentage_rollout: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new feature flag.
    
    Args:
        key: Unique identifier for the flag
        name: Display name for the flag
        description: Description of the flag
        enabled: Whether the flag is enabled globally
        min_subscription_tier: Minimum subscription tier required for the feature
        percentage_rollout: Percentage of users who should see the feature (0-100)
        start_date: Date when the feature should start being available
        end_date: Date when the feature should stop being available
        metadata: Additional metadata for the flag
        
    Returns:
        The created feature flag
    """
    flags = await _read_feature_flags()
    
    # Check if flag already exists
    for flag in flags:
        if flag["key"] == key:
            raise ValueError(f"Feature flag with key '{key}' already exists")
    
    # Create new flag
    new_flag = {
        "key": key,
        "name": name,
        "description": description,
        "enabled": enabled,
        "min_subscription_tier": min_subscription_tier.value if min_subscription_tier else None,
        "percentage_rollout": percentage_rollout,
        "start_date": start_date,
        "end_date": end_date,
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    flags.append(new_flag)
    await _write_feature_flags(flags)
    
    return new_flag


async def update_feature_flag(
    key: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    enabled: Optional[bool] = None,
    min_subscription_tier: Optional[Union[SubscriptionTier, None]] = ...,
    percentage_rollout: Optional[int] = None,
    start_date: Optional[Union[datetime, None]] = ...,
    end_date: Optional[Union[datetime, None]] = ...,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Update a feature flag.
    
    Args:
        key: The feature flag key
        name: New display name for the flag
        description: New description of the flag
        enabled: New enabled status
        min_subscription_tier: New minimum subscription tier
        percentage_rollout: New percentage rollout
        start_date: New start date
        end_date: New end date
        metadata: New metadata
        
    Returns:
        The updated feature flag if found, None otherwise
    """
    flags = await _read_feature_flags()
    
    for i, flag in enumerate(flags):
        if flag["key"] == key:
            # Update fields
            if name is not None:
                flag["name"] = name
            if description is not None:
                flag["description"] = description
            if enabled is not None:
                flag["enabled"] = enabled
            if min_subscription_tier is not ...:
                flag["min_subscription_tier"] = min_subscription_tier.value if min_subscription_tier else None
            if percentage_rollout is not None:
                flag["percentage_rollout"] = percentage_rollout
            if start_date is not ...:
                flag["start_date"] = start_date
            if end_date is not ...:
                flag["end_date"] = end_date
            if metadata is not None:
                flag["metadata"] = metadata
            
            flag["updated_at"] = datetime.utcnow()
            
            flags[i] = flag
            await _write_feature_flags(flags)
            
            return flag
    
    return None


async def delete_feature_flag(key: str) -> bool:
    """
    Delete a feature flag.
    
    Args:
        key: The feature flag key
        
    Returns:
        True if the flag was deleted, False otherwise
    """
    flags = await _read_feature_flags()
    
    for i, flag in enumerate(flags):
        if flag["key"] == key:
            flags.pop(i)
            await _write_feature_flags(flags)
            
            # Also delete any overrides for this flag
            await delete_feature_overrides_by_flag(key)
            
            return True
    
    return False


async def list_feature_flags() -> List[Dict[str, Any]]:
    """
    List all feature flags.
    
    Returns:
        List of all feature flags
    """
    return await _read_feature_flags()


async def create_feature_override(
    flag_key: str,
    user_id: str,
    enabled: bool
) -> Dict[str, Any]:
    """
    Create a user-specific override for a feature flag.
    
    Args:
        flag_key: The feature flag key
        user_id: The user ID
        enabled: Whether the feature is enabled for this user
        
    Returns:
        The created feature override
    """
    # Check if flag exists
    flag = await get_feature_flag(flag_key)
    if not flag:
        raise ValueError(f"Feature flag with key '{flag_key}' does not exist")
    
    overrides = await _read_feature_overrides()
    
    # Check if override already exists
    for override in overrides:
        if override["flag_key"] == flag_key and override["user_id"] == user_id:
            # Update existing override
            override["enabled"] = enabled
            override["updated_at"] = datetime.utcnow()
            
            await _write_feature_overrides(overrides)
            return override
    
    # Create new override
    new_override = {
        "flag_key": flag_key,
        "user_id": user_id,
        "enabled": enabled,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    overrides.append(new_override)
    await _write_feature_overrides(overrides)
    
    return new_override


async def delete_feature_override(flag_key: str, user_id: str) -> bool:
    """
    Delete a user-specific feature flag override.
    
    Args:
        flag_key: The feature flag key
        user_id: The user ID
        
    Returns:
        True if the override was deleted, False otherwise
    """
    overrides = await _read_feature_overrides()
    
    for i, override in enumerate(overrides):
        if override["flag_key"] == flag_key and override["user_id"] == user_id:
            overrides.pop(i)
            await _write_feature_overrides(overrides)
            return True
    
    return False


async def delete_feature_overrides_by_flag(flag_key: str) -> int:
    """
    Delete all overrides for a specific feature flag.
    
    Args:
        flag_key: The feature flag key
        
    Returns:
        Number of overrides deleted
    """
    overrides = await _read_feature_overrides()
    
    original_count = len(overrides)
    overrides = [o for o in overrides if o["flag_key"] != flag_key]
    
    if len(overrides) < original_count:
        await _write_feature_overrides(overrides)
        return original_count - len(overrides)
    
    return 0


async def get_feature_override(flag_key: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a user-specific feature flag override.
    
    Args:
        flag_key: The feature flag key
        user_id: The user ID
        
    Returns:
        The feature override if found, None otherwise
    """
    overrides = await _read_feature_overrides()
    
    for override in overrides:
        if override["flag_key"] == flag_key and override["user_id"] == user_id:
            return override
    
    return None


async def is_feature_enabled(
    flag_key: str,
    user_id: Optional[str] = None,
    subscription_tier: Optional[SubscriptionTier] = None
) -> bool:
    """
    Check if a feature flag is enabled for a specific user.
    
    Args:
        flag_key: The feature flag key
        user_id: The user ID (optional)
        subscription_tier: The user's subscription tier (optional)
        
    Returns:
        True if the feature is enabled, False otherwise
    """
    # Get the feature flag
    flag = await get_feature_flag(flag_key)
    
    # If flag doesn't exist, feature is disabled
    if not flag:
        logger.warning(f"Feature flag '{flag_key}' does not exist")
        return False
    
    # If flag is globally disabled, feature is disabled
    if not flag.get("enabled", False):
        return False
    
    # Check time-based activation
    now = datetime.utcnow()
    
    start_date = flag.get("start_date")
    if start_date and isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    
    end_date = flag.get("end_date")
    if end_date and isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
    
    if start_date and now < start_date:
        return False
    
    if end_date and now > end_date:
        return False
    
    # Check user-specific override if user_id is provided
    if user_id:
        override = await get_feature_override(flag_key, user_id)
        if override is not None:
            return override.get("enabled", False)
    
    # Check subscription tier if provided
    min_tier = flag.get("min_subscription_tier")
    if min_tier and subscription_tier:
        # Convert string to enum if needed
        if isinstance(subscription_tier, str):
            subscription_tier = SubscriptionTier(subscription_tier)
        
        # Convert string to enum if needed
        if isinstance(min_tier, str):
            min_tier = SubscriptionTier(min_tier)
        else:
            min_tier = SubscriptionTier(min_tier)
        
        # Check tier levels
        tier_levels = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.ENTERPRISE: 3
        }
        
        if tier_levels.get(subscription_tier, 0) < tier_levels.get(min_tier, 0):
            return False
    
    # Check percentage rollout if user_id is provided
    percentage = flag.get("percentage_rollout", 100)
    if user_id and percentage < 100:
        # Use a deterministic hash of the user_id and flag_key
        # to ensure consistent behavior for the same user
        seed = hash(f"{user_id}:{flag_key}") % 100000
        random.seed(seed)
        return random.randint(1, 100) <= percentage
    
    # If all checks pass, feature is enabled
    return True


# Create a singleton instance
feature_flag_service = {
    "get_feature_flag": get_feature_flag,
    "create_feature_flag": create_feature_flag,
    "update_feature_flag": update_feature_flag,
    "delete_feature_flag": delete_feature_flag,
    "list_feature_flags": list_feature_flags,
    "create_feature_override": create_feature_override,
    "delete_feature_override": delete_feature_override,
    "get_feature_override": get_feature_override,
    "is_feature_enabled": is_feature_enabled
}
