
"""
Secrets Manager for secure handling of sensitive configuration values.
"""
import os
import logging
import json
from typing import Dict, Any, Optional, Union
from functools import lru_cache
import base64

from .vaultClient import vault_client

logger = logging.getLogger(__name__)

class SecretsManager:
    """
    Secrets Manager for secure handling of sensitive configuration values.
    Provides a unified interface for accessing secrets from Vault or environment variables.
    """
    
    def __init__(self, vault_enabled: bool = True):
        """
        Initialize Secrets Manager.
        
        Args:
            vault_enabled: Whether to use Vault for secrets (if available)
        """
        self.vault_enabled = vault_enabled and os.getenv("VAULT_ADDR") and os.getenv("VAULT_TOKEN")
        self._env_prefix = "HUMANYZE_"  # Prefix for environment variables
    
    def get_secret(
        self, 
        name: str, 
        default: Any = None, 
        vault_path: Optional[str] = None,
        vault_key: Optional[str] = None
    ) -> Any:
        """
        Get a secret from the secrets manager.
        
        Args:
            name: Secret name (used for environment variable name)
            default: Default value if secret not found
            vault_path: Custom Vault path (defaults to "humanyze/{name}")
            vault_key: Specific key to retrieve from Vault secret
            
        Returns:
            Secret value or default
        """
        # Try to get from Vault first if enabled
        if self.vault_enabled:
            # Determine Vault path
            if vault_path is None:
                # Default path structure: humanyze/{name}
                vault_path = f"humanyze/{name.lower()}"
            
            # Get from Vault
            vault_value = vault_client.get_secret(
                path=vault_path,
                key=vault_key,
                default=None
            )
            
            if vault_value is not None:
                return vault_value
        
        # Fallback to environment variables
        # Try with prefix first
        env_var_name = f"{self._env_prefix}{name}"
        env_value = os.getenv(env_var_name)
        
        # If not found with prefix, try without prefix
        if env_value is None:
            env_value = os.getenv(name)
        
        return env_value if env_value is not None else default
    
    def set_secret(
        self, 
        name: str, 
        value: Any, 
        vault_path: Optional[str] = None,
        vault_key: Optional[str] = None
    ) -> bool:
        """
        Set a secret in the secrets manager.
        
        Args:
            name: Secret name
            value: Secret value
            vault_path: Custom Vault path (defaults to "humanyze/{name}")
            vault_key: Specific key to set in Vault secret
            
        Returns:
            True if successful, False otherwise
        """
        if not self.vault_enabled:
            logger.warning("Vault not enabled, cannot store secret")
            return False
        
        # Determine Vault path
        if vault_path is None:
            # Default path structure: humanyze/{name}
            vault_path = f"humanyze/{name.lower()}"
        
        # Prepare data
        if vault_key:
            # Get existing secret first
            existing_data = vault_client.get_secret(path=vault_path, default={})
            if not isinstance(existing_data, dict):
                existing_data = {}
            
            # Update specific key
            existing_data[vault_key] = value
            data = existing_data
        else:
            # Set entire secret
            if isinstance(value, dict):
                data = value
            else:
                data = {name: value}
        
        # Store in Vault
        return vault_client.put_secret(path=vault_path, data=data)
    
    def delete_secret(self, name: str, vault_path: Optional[str] = None) -> bool:
        """
        Delete a secret from the secrets manager.
        
        Args:
            name: Secret name
            vault_path: Custom Vault path (defaults to "humanyze/{name}")
            
        Returns:
            True if successful, False otherwise
        """
        if not self.vault_enabled:
            logger.warning("Vault not enabled, cannot delete secret")
            return False
        
        # Determine Vault path
        if vault_path is None:
            # Default path structure: humanyze/{name}
            vault_path = f"humanyze/{name.lower()}"
        
        # Delete from Vault
        return vault_client.delete_secret(path=vault_path)
    
    def get_database_credentials(self) -> Dict[str, str]:
        """
        Get database credentials.
        
        Returns:
            Dictionary with database credentials
        """
        return {
            "user": self.get_secret("DB_USER", "humanyze_user"),
            "password": self.get_secret("DB_PASSWORD", "humanyze_password"),
            "host": self.get_secret("DB_HOST", "localhost"),
            "port": self.get_secret("DB_PORT", "5432"),
            "name": self.get_secret("DB_NAME", "humanyze_db")
        }
    
    def get_database_url(self) -> str:
        """
        Get database URL.
        
        Returns:
            Database URL string
        """
        # Try to get complete URL first
        db_url = self.get_secret("DATABASE_URL")
        if db_url:
            return db_url
        
        # Otherwise construct from components
        creds = self.get_database_credentials()
        return f"postgresql://{creds['user']}:{creds['password']}@{creds['host']}:{creds['port']}/{creds['name']}"
    
    def get_jwt_keys(self) -> Dict[str, str]:
        """
        Get JWT keys.
        
        Returns:
            Dictionary mapping key IDs to their secret values
        """
        # Try to get from Vault first
        if self.vault_enabled:
            jwt_keys = vault_client.get_secret(path="humanyze/jwt_keys")
            if jwt_keys and isinstance(jwt_keys, dict):
                return jwt_keys
        
        # Fallback to environment variable
        jwt_keys_str = os.getenv("JWT_KEYS", "")
        if jwt_keys_str:
            try:
                # Try to parse as JSON
                return json.loads(jwt_keys_str)
            except json.JSONDecodeError:
                # Try comma-separated format
                keys = {}
                for key_pair in jwt_keys_str.split(','):
                    if ':' in key_pair:
                        kid, secret = key_pair.split(':', 1)
                        keys[kid.strip()] = secret.strip()
                if keys:
                    return keys
        
        # Fallback to single key
        jwt_secret = os.getenv("JWT_SECRET_KEY", "temporary_secret_key_for_development")
        return {"key1": jwt_secret}
    
    def get_active_jwt_key(self) -> tuple:
        """
        Get the currently active JWT key for signing new tokens.
        
        Returns:
            Tuple of (key_id, secret)
        """
        keys = self.get_jwt_keys()
        active_kid = os.getenv("JWT_ACTIVE_KID", "key1")
        
        # Ensure the active key exists
        if active_kid not in keys:
            # Fallback to first key if active key not found
            active_kid = next(iter(keys.keys()), "key1")
        
        return active_kid, keys.get(active_kid, "temporary_secret_key_for_development")
    
    def get_sso_credentials(self, provider: str) -> Dict[str, str]:
        """
        Get SSO provider credentials.
        
        Args:
            provider: SSO provider name (google, microsoft, okta)
            
        Returns:
            Dictionary with client ID and secret
        """
        provider = provider.lower()
        return {
            "client_id": self.get_secret(f"{provider.upper()}_CLIENT_ID"),
            "client_secret": self.get_secret(f"{provider.upper()}_CLIENT_SECRET")
        }
    
    def get_stripe_credentials(self) -> Dict[str, str]:
        """
        Get Stripe credentials.
        
        Returns:
            Dictionary with Stripe API keys
        """
        return {
            "api_key": self.get_secret("STRIPE_API_KEY"),
            "webhook_secret": self.get_secret("STRIPE_WEBHOOK_SECRET"),
            "publishable_key": self.get_secret("STRIPE_PUBLISHABLE_KEY")
        }

# Create a singleton instance
secrets_manager = SecretsManager()
