"""
Performance monitoring middleware.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring request performance."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and measure performance.
        
        Args:
            request: The request
            call_next: The next middleware or route handler
            
        Returns:
            The response
        """
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests (more than 1 second)
        if process_time > 1:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s"
            )
        
        return response
