"""
Models for subscription management.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SubscriptionStatus(str, Enum):
    """Subscription status enum."""
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    UNPAID = "unpaid"


class SubscriptionTier(str, Enum):
    """Subscription tier enum."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionFeatures(BaseModel):
    """Features included in a subscription tier."""
    max_characters_per_month: int = 0
    max_requests_per_day: int = 0
    custom_profiles: bool = False
    priority_processing: bool = False
    advanced_analytics: bool = False
    api_access: bool = False
    dedicated_support: bool = False
    # Additional feature flags can be dynamically added here
    feature_flags: Dict[str, bool] = Field(default_factory=dict)


class SubscriptionPlan(BaseModel):
    """Subscription plan model."""
    id: str
    name: str
    description: str
    tier: SubscriptionTier
    price_id: str
    price_amount: int
    price_currency: str = "usd"
    interval: str = "month"
    features: SubscriptionFeatures


class Subscription(BaseModel):
    """User subscription model."""
    id: str
    user_id: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    tier: SubscriptionTier = SubscriptionTier.FREE
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubscriptionCreate(BaseModel):
    """Model for creating a subscription."""
    user_id: str
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    tier: SubscriptionTier = SubscriptionTier.FREE
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubscriptionUpdate(BaseModel):
    """Model for updating a subscription."""
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    status: Optional[SubscriptionStatus] = None
    tier: Optional[SubscriptionTier] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class SubscriptionUsage(BaseModel):
    """Model for tracking subscription usage."""
    id: str
    subscription_id: str
    user_id: str
    characters_used: int = 0
    requests_made: int = 0
    period_start: datetime
    period_end: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CheckoutSessionRequest(BaseModel):
    """Model for requesting a checkout session."""
    price_id: str
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CheckoutSessionResponse(BaseModel):
    """Model for checkout session response."""
    id: str
    url: str
    status: str
    payment_status: str


class CustomerPortalRequest(BaseModel):
    """Model for requesting a customer portal session."""
    return_url: Optional[str] = None


class CustomerPortalResponse(BaseModel):
    """Model for customer portal session response."""
    id: str
    url: str


class SubscriptionResponse(BaseModel):
    """Model for subscription response."""
    id: str
    user_id: str
    status: SubscriptionStatus
    tier: SubscriptionTier
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    created_at: datetime
    updated_at: datetime
    features: SubscriptionFeatures
