"""
Models for feature flag management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.models.subscription import SubscriptionTier


class FeatureFlag(BaseModel):
    """Feature flag model."""
    key: str
    name: str
    description: str
    enabled: bool = True
    min_subscription_tier: Optional[SubscriptionTier] = None
    percentage_rollout: int = 100
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FeatureFlagCreate(BaseModel):
    """Model for creating a feature flag."""
    key: str
    name: str
    description: str
    enabled: bool = True
    min_subscription_tier: Optional[SubscriptionTier] = None
    percentage_rollout: int = 100
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeatureFlagUpdate(BaseModel):
    """Model for updating a feature flag."""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    min_subscription_tier: Optional[SubscriptionTier] = None
    percentage_rollout: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class FeatureOverride(BaseModel):
    """Feature flag override model."""
    flag_key: str
    user_id: str
    enabled: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FeatureOverrideCreate(BaseModel):
    """Model for creating a feature flag override."""
    flag_key: str
    user_id: str
    enabled: bool


class FeatureFlagResponse(BaseModel):
    """Model for feature flag response."""
    key: str
    name: str
    description: str
    enabled: bool
    min_subscription_tier: Optional[str] = None
    percentage_rollout: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class FeatureFlagListResponse(BaseModel):
    """Model for feature flag list response."""
    flags: List[Dict[str, Any]]


class FeatureOverrideResponse(BaseModel):
    """Model for feature override response."""
    flag_key: str
    user_id: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


class FeatureStatusResponse(BaseModel):
    """Model for feature status response."""
    flag_key: str
    enabled: bool
    user_id: str
    subscription_tier: str
