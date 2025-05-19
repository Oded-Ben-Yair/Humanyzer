"""
Configuration settings for the Humanyze application.
"""
import os
from typing import Dict, Tuple

class Settings:
    """Application settings."""
    
    # JWT settings
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Rate limiting
    LOGIN_RATE_LIMIT = 5  # Maximum login attempts per minute
    
    def get_active_jwt_key(self) -> Tuple[str, str]:
        """Get the active JWT key ID and secret."""
        return "default", "humanyze_secret_key"
    
    def get_jwt_keys(self) -> Dict[str, str]:
        """Get all available JWT keys."""
        return {"default": "humanyze_secret_key"}

# Create a settings instance
settings = Settings()
