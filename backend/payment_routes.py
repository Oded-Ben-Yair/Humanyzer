"""
API routes for payment and subscription management.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status, Body
from app.auth.dependencies import get_current_user
from app.services.stripe_client import stripe_service
from app.models.subscription import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    CustomerPortalRequest,
    CustomerPortalResponse,
    SubscriptionResponse,
    SubscriptionFeatures,
    SubscriptionTier,
    SubscriptionStatus,
    SubscriptionCreate,
    SubscriptionUpdate
)
from app.db.subscriptions import (
    get_subscription_by_user_id,
    create_subscription,
    update_subscription,
    get_subscription_features,
    check_subscription_limit,
    get_subscription_by_stripe_id
)
from app.config import settings
from typing import Dict, Any, List
import logging
from datetime import datetime
import stripe

router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a Stripe checkout session for subscription.
    
    Args:
        request: Checkout session request
        current_user: Current authenticated user
        
    Returns:
        Checkout session details
    """
    try:
        # Get or create subscription record
        subscription = await get_subscription_by_user_id(current_user["id"])
        
        # Create metadata for the checkout session
        metadata = {
            "user_id": current_user["id"],
            **request.metadata
        }
        
        # Create checkout session
        checkout_session = stripe_service.create_checkout_session(
            customer_email=current_user["email"],
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata=metadata
        )
        
        return CheckoutSessionResponse(
            id=checkout_session["id"],
            url=checkout_session["url"],
            status=checkout_session["status"],
            payment_status=checkout_session["payment_status"]
        )
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout session: {str(e)}"
        )


@router.post("/create-customer-portal", response_model=CustomerPortalResponse)
async def create_customer_portal(
    request: CustomerPortalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a Stripe customer portal session for managing subscriptions.
    
    Args:
        request: Customer portal request
        current_user: Current authenticated user
        
    Returns:
        Customer portal session details
    """
    try:
        # Get subscription to get Stripe customer ID
        subscription = await get_subscription_by_user_id(current_user["id"])
        if not subscription or not subscription.get("stripe_customer_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        # Create customer portal session
        portal_session = stripe_service.create_customer_portal_session(
            customer_id=subscription["stripe_customer_id"],
            return_url=request.return_url
        )
        
        return CustomerPortalResponse(
            id=portal_session["id"],
            url=portal_session["url"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating customer portal session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating customer portal session: {str(e)}"
        )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user's subscription.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Subscription details
    """
    try:
        # Get subscription
        subscription = await get_subscription_by_user_id(current_user["id"])
        
        # If no subscription found, return free tier
        if not subscription:
            features = await get_subscription_features(SubscriptionTier.FREE)
            now = datetime.utcnow()
            
            return SubscriptionResponse(
                id="free",
                user_id=current_user["id"],
                status=SubscriptionStatus.ACTIVE,
                tier=SubscriptionTier.FREE,
                current_period_start=now,
                current_period_end=now,
                cancel_at_period_end=False,
                created_at=now,
                updated_at=now,
                features=SubscriptionFeatures(**features)
            )
        
        # Get features for the subscription tier
        tier = SubscriptionTier(subscription["tier"])
        features = await get_subscription_features(tier)
        
        return SubscriptionResponse(
            id=subscription["id"],
            user_id=subscription["user_id"],
            status=SubscriptionStatus(subscription["status"]),
            tier=tier,
            current_period_start=subscription.get("current_period_start"),
            current_period_end=subscription.get("current_period_end"),
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
            created_at=subscription["created_at"],
            updated_at=subscription["updated_at"],
            features=SubscriptionFeatures(**features)
        )
    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting subscription: {str(e)}"
        )


@router.get("/subscription/check-limit")
async def check_subscription_limits(
    character_count: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Check if user has reached subscription limits.
    
    Args:
        character_count: Number of characters to check
        current_user: Current authenticated user
        
    Returns:
        Limit information
    """
    try:
        limit_info = await check_subscription_limit(current_user["id"], character_count)
        return limit_info
    except Exception as e:
        logger.error(f"Error checking subscription limits: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking subscription limits: {str(e)}"
        )


@router.get("/plans")
async def get_subscription_plans():
    """
    Get available subscription plans.
    
    Returns:
        List of subscription plans
    """
    try:
        # Define subscription plans
        plans = [
            {
                "id": "free",
                "name": "Free",
                "description": "Basic access with limited features",
                "tier": SubscriptionTier.FREE.value,
                "price_id": None,
                "price_amount": 0,
                "price_currency": "usd",
                "interval": "month",
                "features": await get_subscription_features(SubscriptionTier.FREE)
            },
            {
                "id": "basic",
                "name": "Basic",
                "description": "Essential features for casual users",
                "tier": SubscriptionTier.BASIC.value,
                "price_id": settings.BASIC_PLAN_PRICE_ID,
                "price_amount": 999,  # $9.99
                "price_currency": "usd",
                "interval": "month",
                "features": await get_subscription_features(SubscriptionTier.BASIC)
            },
            {
                "id": "pro",
                "name": "Professional",
                "description": "Advanced features for power users",
                "tier": SubscriptionTier.PRO.value,
                "price_id": settings.PRO_PLAN_PRICE_ID,
                "price_amount": 1999,  # $19.99
                "price_currency": "usd",
                "interval": "month",
                "features": await get_subscription_features(SubscriptionTier.PRO)
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "description": "Complete solution for businesses",
                "tier": SubscriptionTier.ENTERPRISE.value,
                "price_id": settings.ENTERPRISE_PLAN_PRICE_ID,
                "price_amount": 4999,  # $49.99
                "price_currency": "usd",
                "interval": "month",
                "features": await get_subscription_features(SubscriptionTier.ENTERPRISE)
            }
        ]
        
        return {"plans": plans}
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting subscription plans: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    Args:
        request: HTTP request
        
    Returns:
        Success message
    """
    try:
        # Get request body and signature header
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        if not sig_header:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing Stripe signature header"
            )
        
        # Verify webhook signature
        try:
            event = stripe_service.verify_webhook_signature(payload, sig_header)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload: {str(e)}"
            )
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid signature: {str(e)}"
            )
        
        # Handle different event types
        if event.type == "checkout.session.completed":
            await handle_checkout_session_completed(event.data.object)
        elif event.type == "customer.subscription.created":
            await handle_subscription_created(event.data.object)
        elif event.type == "customer.subscription.updated":
            await handle_subscription_updated(event.data.object)
        elif event.type == "customer.subscription.deleted":
            await handle_subscription_deleted(event.data.object)
        elif event.type == "invoice.paid":
            await handle_invoice_paid(event.data.object)
        elif event.type == "invoice.payment_failed":
            await handle_invoice_payment_failed(event.data.object)
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error handling webhook: {str(e)}"
        )


async def handle_checkout_session_completed(session):
    """
    Handle checkout.session.completed event.
    
    Args:
        session: Checkout session object
    """
    try:
        logger.info(f"Handling checkout.session.completed: {session.id}")
        
        # Get metadata
        metadata = session.metadata
        user_id = metadata.get("user_id")
        
        if not user_id:
            logger.error(f"No user_id in metadata for session {session.id}")
            return
        
        # Get subscription
        subscription = await get_subscription_by_user_id(user_id)
        
        # Create or update subscription
        if not subscription:
            # Create new subscription
            subscription_data = SubscriptionCreate(
                user_id=user_id,
                stripe_customer_id=session.customer,
                tier=SubscriptionTier.FREE,  # Will be updated when subscription is created
                status=SubscriptionStatus.ACTIVE
            )
            
            await create_subscription(subscription_data)
        else:
            # Update existing subscription
            subscription_update = SubscriptionUpdate(
                stripe_customer_id=session.customer
            )
            
            await update_subscription(subscription["id"], subscription_update)
    except Exception as e:
        logger.error(f"Error handling checkout.session.completed: {str(e)}")


async def handle_subscription_created(subscription):
    """
    Handle customer.subscription.created event.
    
    Args:
        subscription: Subscription object
    """
    try:
        logger.info(f"Handling customer.subscription.created: {subscription.id}")
        
        # Get customer ID
        customer_id = subscription.customer
        
        # Get subscription from database by customer ID
        db_subscription = await get_subscription_by_stripe_customer_id(customer_id)
        
        if not db_subscription:
            logger.error(f"No subscription found for customer {customer_id}")
            return
        
        # Determine subscription tier based on price
        tier = SubscriptionTier.FREE
        if subscription.items.data:
            price_id = subscription.items.data[0].price.id
            
            if price_id == settings.BASIC_PLAN_PRICE_ID:
                tier = SubscriptionTier.BASIC
            elif price_id == settings.PRO_PLAN_PRICE_ID:
                tier = SubscriptionTier.PRO
            elif price_id == settings.ENTERPRISE_PLAN_PRICE_ID:
                tier = SubscriptionTier.ENTERPRISE
        
        # Update subscription
        subscription_update = SubscriptionUpdate(
            stripe_subscription_id=subscription.id,
            status=SubscriptionStatus(subscription.status),
            tier=tier,
            current_period_start=datetime.fromtimestamp(subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(subscription.current_period_end),
            cancel_at_period_end=subscription.cancel_at_period_end
        )
        
        await update_subscription(db_subscription["id"], subscription_update)
    except Exception as e:
        logger.error(f"Error handling customer.subscription.created: {str(e)}")


async def handle_subscription_updated(subscription):
    """
    Handle customer.subscription.updated event.
    
    Args:
        subscription: Subscription object
    """
    try:
        logger.info(f"Handling customer.subscription.updated: {subscription.id}")
        
        # Get subscription from database
        db_subscription = await get_subscription_by_stripe_id(subscription.id)
        
        if not db_subscription:
            logger.error(f"No subscription found for Stripe subscription {subscription.id}")
            return
        
        # Determine subscription tier based on price
        tier = None
        if subscription.items.data:
            price_id = subscription.items.data[0].price.id
            
            if price_id == settings.BASIC_PLAN_PRICE_ID:
                tier = SubscriptionTier.BASIC
            elif price_id == settings.PRO_PLAN_PRICE_ID:
                tier = SubscriptionTier.PRO
            elif price_id == settings.ENTERPRISE_PLAN_PRICE_ID:
                tier = SubscriptionTier.ENTERPRISE
        
        # Update subscription
        subscription_update = SubscriptionUpdate(
            status=SubscriptionStatus(subscription.status),
            tier=tier,
            current_period_start=datetime.fromtimestamp(subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(subscription.current_period_end),
            cancel_at_period_end=subscription.cancel_at_period_end
        )
        
        await update_subscription(db_subscription["id"], subscription_update)
    except Exception as e:
        logger.error(f"Error handling customer.subscription.updated: {str(e)}")


async def handle_subscription_deleted(subscription):
    """
    Handle customer.subscription.deleted event.
    
    Args:
        subscription: Subscription object
    """
    try:
        logger.info(f"Handling customer.subscription.deleted: {subscription.id}")
        
        # Get subscription from database
        db_subscription = await get_subscription_by_stripe_id(subscription.id)
        
        if not db_subscription:
            logger.error(f"No subscription found for Stripe subscription {subscription.id}")
            return
        
        # Update subscription
        subscription_update = SubscriptionUpdate(
            status=SubscriptionStatus.CANCELED,
            tier=SubscriptionTier.FREE
        )
        
        await update_subscription(db_subscription["id"], subscription_update)
    except Exception as e:
        logger.error(f"Error handling customer.subscription.deleted: {str(e)}")


async def handle_invoice_paid(invoice):
    """
    Handle invoice.paid event.
    
    Args:
        invoice: Invoice object
    """
    try:
        logger.info(f"Handling invoice.paid: {invoice.id}")
        
        # Get subscription ID
        subscription_id = invoice.subscription
        
        if not subscription_id:
            logger.info(f"No subscription associated with invoice {invoice.id}")
            return
        
        # Get subscription from database
        db_subscription = await get_subscription_by_stripe_id(subscription_id)
        
        if not db_subscription:
            logger.error(f"No subscription found for Stripe subscription {subscription_id}")
            return
        
        # Update subscription status to active if it's not already
        if db_subscription["status"] != SubscriptionStatus.ACTIVE.value:
            subscription_update = SubscriptionUpdate(
                status=SubscriptionStatus.ACTIVE
            )
            
            await update_subscription(db_subscription["id"], subscription_update)
    except Exception as e:
        logger.error(f"Error handling invoice.paid: {str(e)}")


async def handle_invoice_payment_failed(invoice):
    """
    Handle invoice.payment_failed event.
    
    Args:
        invoice: Invoice object
    """
    try:
        logger.info(f"Handling invoice.payment_failed: {invoice.id}")
        
        # Get subscription ID
        subscription_id = invoice.subscription
        
        if not subscription_id:
            logger.info(f"No subscription associated with invoice {invoice.id}")
            return
        
        # Get subscription from database
        db_subscription = await get_subscription_by_stripe_id(subscription_id)
        
        if not db_subscription:
            logger.error(f"No subscription found for Stripe subscription {subscription_id}")
            return
        
        # Update subscription status to past_due
        subscription_update = SubscriptionUpdate(
            status=SubscriptionStatus.PAST_DUE
        )
        
        await update_subscription(db_subscription["id"], subscription_update)
    except Exception as e:
        logger.error(f"Error handling invoice.payment_failed: {str(e)}")
