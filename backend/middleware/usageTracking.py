
"""
Middleware for tracking API usage.

This module provides middleware to track API usage for analytics
and rate limiting purposes.
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.analytics.usageTracker import usage_tracker
from app.config import settings

# Configure logger
logger = logging.getLogger("usage_tracking_middleware")

class UsageTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking API usage.
    
    This middleware records API calls and their latency for
    analytics and billing purposes.
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
        """
        super().__init__(app)
        self.enabled = getattr(settings, "ENABLE_USAGE_TRACKING", True)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and track usage.
        
        Args:
            request: The FastAPI request
            call_next: The next middleware in the chain
            
        Returns:
            The response from the next middleware
        """
        if not self.enabled:
            return await call_next(request)
        
        # Record start time
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate request latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Get customer ID from request
        customer_id = self._get_customer_id(request)
        
        if customer_id:
            # Track the request asynchronously
            # We don't await this to avoid blocking the response
            usage_tracker.track_request(request, customer_id, latency_ms)
        
        return response
    
    def _get_customer_id(self, request: Request) -> str:
        """
        Extract customer ID from the request.
        
        Args:
            request: The FastAPI request
            
        Returns:
            Customer identifier or default value
        """
        # Try to get from authentication
        if hasattr(request.state, "user") and hasattr(request.state.user, "customer_id"):
            return request.state.user.customer_id
        
        # Try to get from JWT token
        if hasattr(request.state, "token_data") and hasattr(request.state.token_data, "customer_id"):
            return request.state.token_data.customer_id
        
        # Try to get from header
        customer_id = request.headers.get("X-Customer-ID")
        if customer_id:
            return customer_id
        
        # Default to IP address if no customer ID found
        return request.client.host if request.client else "anonymous"
