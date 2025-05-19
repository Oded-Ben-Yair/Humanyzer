"""
Configuration settings for the Humanyze application.
Loaded from environment variables and .env file.
"""
import os
from typing import Dict, Tuple, Optional

# Pydantic V2 uses pydantic-settings.
# If you have Pydantic V1, you'd use: from pydantic import BaseSettings
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    Pydantic BaseSettings automatically attempts to load values from
    environment variables. If a variable isn't set in the environment,
    it then tries to load it from a .env file (if python-dotenv is installed
    and an .env file is found).
    """

    # For Pydantic V2 to find and use the .env file.
    # It will look for a file named ".env" in the current working directory
    # or a parent directory by default.
    # Ensure your .env file is in the root of your project (e.g., ~/Desktop/ExternalDrive/humanyzer/.env)
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'  # Ignores extra variables in .env not defined in this Settings class
    )

    # Database Configuration
    # This corresponds to: DATABASE_URL=your_db_connection_string in your .env file
    DATABASE_URL: str

    # AWS Configuration (defaults provided if not in .env or environment)
    # Corresponds to: AWS_REGION=us-east-1
    AWS_REGION: str = "us-east-1"
    # Corresponds to: AWS_PROFILE=humanyzer (can be optional)
    AWS_PROFILE: Optional[str] = None

    # API Configuration
    # Corresponds to: API_HOST=0.0.0.0
    API_HOST: str = "0.0.0.0"
    # Corresponds to: API_PORT=8002
    API_PORT: int = 8002

    # JWT settings
    # These should also be in your .env file for security and flexibility.
    # Example .env entries:
    # JWT_SECRET=your_strong_secret_key_here
    # JWT_ALGORITHM=HS256
    # ACCESS_TOKEN_EXPIRE_MINUTES=30
    # REFRESH_TOKEN_EXPIRE_DAYS=7
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Rate limiting (from your original class)
    LOGIN_RATE_LIMIT: int = 5  # Maximum login attempts per minute

    # Feature Flags (example based on your .env from the guide)
    # Assuming your .env has: ENABLE_PREMIUM_FEATURES=true (or false)
    ENABLE_PREMIUM_FEATURES: bool = False # Default to False

    # --- Methods related to JWT ---
    # These methods can now use the JWT_SECRET loaded from the environment.
    # If you plan to support multiple rotating JWT keys, this logic would need
    # to be more sophisticated (e.g., loading a dictionary of keys).
    # For a single key as defined by JWT_SECRET, it's simpler.

    def get_active_jwt_secret(self) -> str:
        """Returns the currently active JWT secret key."""
        return self.JWT_SECRET

    # The following methods imply a system with multiple named keys.
    # If you only have one JWT_SECRET, these might be overly complex.
    # Consider if you truly need a dictionary of keys vs. just using self.JWT_SECRET.
    # For now, I'm adapting them to use the single loaded JWT_SECRET.
    def get_active_jwt_key_tuple(self) -> Tuple[str, str]:
        """Get the active JWT key ID and secret (adapted for single secret)."""
        # "default" is an arbitrary key_id if you only have one main secret
        return "default", self.JWT_SECRET

    def get_jwt_keys_dict(self) -> Dict[str, str]:
        """Get all available JWT keys (adapted for single secret)."""
        return {"default": self.JWT_SECRET}

# Create a single, global settings instance to be imported by other modules
settings = Settings()

# You can add a simple check here for debugging if DATABASE_URL is loaded:
# if __name__ == "__main__":
# print(f"Attempting to load settings...")
# print(f"Loaded DATABASE_URL: {settings.DATABASE_URL}")
# print(f"Loaded JWT_SECRET: {settings.JWT_SECRET}")
# print(f"All settings: {settings.model_dump()}")
