
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging

# Configure logger
logger = logging.getLogger("rate_limiter")

# Initialize rate limiter with IP-based key function
limiter = Limiter(key_func=get_remote_address)

# Rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded exceptions.
    
    Args:
        request: The FastAPI request
        exc: The rate limit exceeded exception
        
    Returns:
        JSON response with 429 status code
    """
    logger.warning(f"Rate limit exceeded for IP: {get_remote_address(request)}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many login attempts. Please try again later.",
            "limit": str(exc.limit),
            "reset_at": exc.reset_at.isoformat() if exc.reset_at else None
        }
    )

# Rate limiting middleware class
class RateLimitMiddleware(SlowAPIMiddleware):
    """
    Middleware for applying rate limits to FastAPI routes.
    Extends SlowAPIMiddleware with custom configuration.
    """
    pass

# Decorator for applying rate limits to specific endpoints
def limit_login_attempts(rate_limit="5/minute"):
    """
    Decorator to apply rate limiting to login endpoints.
    
    Args:
        rate_limit: Rate limit string in format "number/period"
                   Examples: "5/minute", "100/hour", "1000/day"
    
    Returns:
        Decorator function
    """
    def decorator(func):
        return limiter.limit(rate_limit)(func)
    return decorator
