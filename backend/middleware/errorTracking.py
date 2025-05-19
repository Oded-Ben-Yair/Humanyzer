
"""
Middleware for capturing and reporting errors.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import traceback
import json
from typing import Callable, Dict, Any
from app.utils.monitoring.errorReporter import capture_exception

logger = logging.getLogger(__name__)

class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking and reporting errors.
    """
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        try:
            # Process the request
            return await call_next(request)
        
        except Exception as exc:
            # Capture request details for context
            context = await self._get_request_context(request)
            
            # Report the exception
            capture_exception(exc, context=context)
            
            # Re-raise the exception to let FastAPI handle the response
            raise
    
    async def _get_request_context(self, request: Request) -> Dict[str, Any]:
        """
        Extract context information from the request.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            Dictionary with request context
        """
        context = {
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else "unknown",
            "headers": dict(request.headers),
        }
        
        # Try to extract user information if available
        try:
            if hasattr(request.state, "user") and request.state.user:
                context["user_id"] = request.state.user.id
        except Exception:
            pass
        
        # Try to extract request body if available
        try:
            body = await request.body()
            if body:
                try:
                    # Try to parse as JSON
                    context["body"] = json.loads(body)
                except json.JSONDecodeError:
                    # If not JSON, store as string (truncated if too large)
                    body_str = body.decode("utf-8", errors="replace")
                    if len(body_str) > 1000:
                        body_str = body_str[:1000] + "... [truncated]"
                    context["body"] = body_str
        except Exception:
            pass
        
        return context
