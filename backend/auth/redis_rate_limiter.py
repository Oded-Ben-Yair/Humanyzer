"""
Rate limiting utilities for authentication endpoints.
"""
from functools import wraps
from fastapi import HTTPException, status
import time

# Simple in-memory rate limiter
rate_limit_store = {}

def limit_login_attempts(max_attempts):
    """
    Decorator to limit login attempts.
    
    Args:
        max_attempts: Maximum number of attempts allowed per minute
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get client IP (in a real app, this would come from the request)
            client_ip = "127.0.0.1"
            
            # Get current timestamp
            current_time = int(time.time())
            
            # Initialize or get client's rate limit data
            if client_ip not in rate_limit_store:
                rate_limit_store[client_ip] = {
                    "attempts": 0,
                    "reset_time": current_time + 60  # Reset after 1 minute
                }
            
            # Check if reset time has passed
            if current_time > rate_limit_store[client_ip]["reset_time"]:
                # Reset attempts
                rate_limit_store[client_ip] = {
                    "attempts": 0,
                    "reset_time": current_time + 60
                }
            
            # Check if max attempts reached
            if rate_limit_store[client_ip]["attempts"] >= max_attempts:
                # Calculate time remaining until reset
                time_remaining = rate_limit_store[client_ip]["reset_time"] - current_time
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many login attempts. Try again in {time_remaining} seconds."
                )
            
            # Increment attempts
            rate_limit_store[client_ip]["attempts"] += 1
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
