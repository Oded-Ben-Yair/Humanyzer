"""
Stripe client service for handling Stripe API interactions.
"""
import stripe
import os
import logging
from typing import Dict, Any, List, Optional

# Try to import the secrets manager
try:
    from app.config.secrets import secrets_manager
    # Get Stripe API key from secrets manager
    stripe.api_key = secrets_manager.get_secret("STRIPE_API_KEY")
except ImportError:
    # Fallback to settings if secrets manager not available
    from app.config import settings
    stripe.api_key = settings.STRIPE_API_KEY

logger = logging.getLogger(__name__)

class StripeService:
    """Service for interacting with Stripe API."""
    
    @staticmethod
    def create_checkout_session(
        customer_email: str,
        price_id: str,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for a subscription or one-time payment.
        
        Args:
            customer_email: Customer's email address
            price_id: Stripe Price ID for the product
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect after cancelled payment
            metadata: Additional metadata to include with the checkout session
            
        Returns:
            Checkout session details including the URL
        """
        try:
            if not success_url:
                success_url = f"{settings.FRONTEND_URL}/payment_success"
            if not cancel_url:
                cancel_url = f"{settings.FRONTEND_URL}/payment_cancel"
                
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=customer_email,
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {}
            )
            
            return {
                "id": session.id,
                "url": session.url,
                "status": session.status,
                "payment_status": session.payment_status
            }
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise
    
    @staticmethod
    def create_customer_portal_session(
        customer_id: str,
        return_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe customer portal session for managing subscriptions.
        
        Args:
            customer_id: Stripe Customer ID
            return_url: URL to return to after using the portal
            
        Returns:
            Portal session details including the URL
        """
        try:
            if not return_url:
                return_url = settings.FRONTEND_URL
                
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            
            return {
                "id": session.id,
                "url": session.url
            }
        except Exception as e:
            logger.error(f"Error creating customer portal session: {str(e)}")
            raise
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details.
        
        Args:
            subscription_id: Stripe Subscription ID
            
        Returns:
            Subscription details
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except Exception as e:
            logger.error(f"Error retrieving subscription: {str(e)}")
            raise
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Stripe Subscription ID
            
        Returns:
            Cancelled subscription details
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return subscription
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            raise
    
    @staticmethod
    def list_products() -> List[Dict[str, Any]]:
        """
        List all active products.
        
        Returns:
            List of products
        """
        try:
            products = stripe.Product.list(active=True)
            return products.data
        except Exception as e:
            logger.error(f"Error listing products: {str(e)}")
            raise
    
    @staticmethod
    def list_prices(product_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all active prices, optionally filtered by product.
        
        Args:
            product_id: Optional Stripe Product ID to filter by
            
        Returns:
            List of prices
        """
        try:
            params = {"active": True}
            if product_id:
                params["product"] = product_id
                
            prices = stripe.Price.list(**params)
            return prices.data
        except Exception as e:
            logger.error(f"Error listing prices: {str(e)}")
            raise
    
    @staticmethod
    def create_customer(email: str, name: Optional[str] = None, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new Stripe customer.
        
        Args:
            email: Customer's email address
            name: Customer's name
            metadata: Additional metadata
            
        Returns:
            Created customer details
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise
    
    @staticmethod
    def get_customer(customer_id: str) -> Dict[str, Any]:
        """
        Get customer details.
        
        Args:
            customer_id: Stripe Customer ID
            
        Returns:
            Customer details
        """
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return customer
        except Exception as e:
            logger.error(f"Error retrieving customer: {str(e)}")
            raise
    
    @staticmethod
    def update_customer(customer_id: str, **kwargs) -> Dict[str, Any]:
        """
        Update a customer.
        
        Args:
            customer_id: Stripe Customer ID
            **kwargs: Fields to update
            
        Returns:
            Updated customer details
        """
        try:
            customer = stripe.Customer.modify(customer_id, **kwargs)
            return customer
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            raise
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, sig_header: str, webhook_secret: Optional[str] = None) -> stripe.Event:
        """
        Verify Stripe webhook signature and construct the event.
        
        Args:
            payload: Request body
            sig_header: Stripe-Signature header
            webhook_secret: Webhook secret key (defaults to secret from secrets manager or settings)
            
        Returns:
            Constructed Stripe event
            
        Raises:
            ValueError: If payload is invalid
            stripe.error.SignatureVerificationError: If signature verification fails
        """
        try:
            # Try to get webhook secret from parameter first
            secret = webhook_secret
            
            # If not provided, try to get from secrets manager
            if not secret:
                try:
                    from app.config.secrets import secrets_manager
                    secret = secrets_manager.get_secret("STRIPE_WEBHOOK_SECRET")
                except ImportError:
                    # Fallback to settings
                    from app.config import settings
                    secret = settings.STRIPE_WEBHOOK_SECRET
            
            if not secret:
                raise ValueError("Webhook secret is not configured")
                
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=secret
            )
            
            return event
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            raise

# Create a singleton instance
stripe_service = StripeService()
