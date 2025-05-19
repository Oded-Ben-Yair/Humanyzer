
import redis
from typing import Optional
import time
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from humanyze_project.src.api.config import settings

# Redis connection
redis_client = None

def get_redis_client():
    """
    Get or create a Redis client instance.
    
    Returns:
        Redis client instance
    """
    global redis_client
    if redis_client is None:
        # Get Redis URL from settings or use default
        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.Redis.from_url(
            url=redis_url,
            decode_responses=True  # Automatically decode responses to strings
        )
    return redis_client

def add_token_to_blacklist(jti: str, exp_timestamp: int) -> bool:
    """
    Add a token to the blacklist.
    
    Args:
        jti: JWT ID to blacklist
        exp_timestamp: Token expiration timestamp
        
    Returns:
        True if token was added to blacklist, False otherwise
    """
    try:
        # Calculate seconds until expiry
        current_timestamp = int(time.time())
        ttl = max(0, exp_timestamp - current_timestamp)
        
        # Store token in Redis with expiration
        redis_conn = get_redis_client()
        redis_conn.setex(f"blacklist:{jti}", ttl, "true")
        return True
    except Exception as e:
        print(f"Error adding token to blacklist: {e}")
        return False

def is_token_blacklisted(jti: str) -> bool:
    """
    Check if a token is blacklisted.
    
    Args:
        jti: JWT ID to check
        
    Returns:
        True if token is blacklisted, False otherwise
    """
    try:
        redis_conn = get_redis_client()
        return redis_conn.exists(f"blacklist:{jti}") == 1
    except Exception as e:
        print(f"Error checking token blacklist: {e}")
        # In case of Redis failure, default to not blacklisted
        # This is a security trade-off - in production you might want to
        # fail closed (return True) depending on your security requirements
        return False

def revoke_all_user_tokens(user_id: str, exp_timestamp: int) -> bool:
    """
    Revoke all tokens for a specific user.
    
    Args:
        user_id: User ID whose tokens should be revoked
        exp_timestamp: Expiration timestamp for the blacklist entry
        
    Returns:
        True if user was added to blacklist, False otherwise
    """
    try:
        # Calculate seconds until expiry
        current_timestamp = int(time.time())
        ttl = max(0, exp_timestamp - current_timestamp)
        
        # Store user in Redis with expiration
        redis_conn = get_redis_client()
        redis_conn.setex(f"blacklist:user:{user_id}", ttl, "true")
        return True
    except Exception as e:
        print(f"Error revoking all user tokens: {e}")
        return False

def is_user_blacklisted(user_id: str) -> bool:
    """
    Check if all tokens for a user are blacklisted.
    
    Args:
        user_id: User ID to check
        
    Returns:
        True if user is blacklisted, False otherwise
    """
    try:
        redis_conn = get_redis_client()
        return redis_conn.exists(f"blacklist:user:{user_id}") == 1
    except Exception as e:
        print(f"Error checking user blacklist: {e}")
        # In case of Redis failure, default to not blacklisted
        return False
