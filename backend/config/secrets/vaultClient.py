
"""
HashiCorp Vault client for secure secrets management.
"""
import os
import logging
import hvac
import json
from typing import Dict, Any, Optional
import time
from functools import lru_cache

logger = logging.getLogger(__name__)

class VaultClient:
    """Client for interacting with HashiCorp Vault."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        mount_point: str = "secret",
        cache_ttl: int = 300  # Cache TTL in seconds
    ):
        """
        Initialize Vault client.
        
        Args:
            url: Vault server URL (defaults to VAULT_ADDR env var)
            token: Vault authentication token (defaults to VAULT_TOKEN env var)
            mount_point: Secret engine mount point
            cache_ttl: Cache time-to-live in seconds
        """
        self.url = url or os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.token = token or os.getenv("VAULT_TOKEN")
        self.mount_point = mount_point
        self.cache_ttl = cache_ttl
        self._client = None
        self._last_connect_attempt = 0
        self._connect_retry_interval = 60  # Retry connection every 60 seconds
        self._secret_cache = {}
        self._cache_timestamps = {}
    
    @property
    def client(self) -> hvac.Client:
        """Get or create Vault client with connection retry logic."""
        current_time = time.time()
        
        # If client exists and is authenticated, return it
        if self._client and self._client.is_authenticated():
            return self._client
        
        # If we recently tried to connect and failed, don't retry too frequently
        if self._last_connect_attempt > 0 and current_time - self._last_connect_attempt < self._connect_retry_interval:
            logger.warning("Vault connection recently failed, using fallback values")
            return None
        
        # Try to connect
        self._last_connect_attempt = current_time
        try:
            if not self.token:
                logger.warning("Vault token not provided, secrets will not be available")
                return None
            
            self._client = hvac.Client(url=self.url, token=self.token)
            
            # Verify authentication
            if not self._client.is_authenticated():
                logger.error("Vault authentication failed")
                self._client = None
            else:
                logger.info("Successfully connected to Vault")
            
            return self._client
        except Exception as e:
            logger.error(f"Error connecting to Vault: {str(e)}")
            self._client = None
            return None
    
    def get_secret(self, path: str, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a secret from Vault with caching.
        
        Args:
            path: Secret path
            key: Specific key to retrieve (if secret is a dictionary)
            default: Default value if secret not found
            
        Returns:
            Secret value or default
        """
        # Check cache first
        cache_key = f"{path}:{key}" if key else path
        current_time = time.time()
        
        # Return from cache if valid
        if cache_key in self._secret_cache and current_time - self._cache_timestamps.get(cache_key, 0) < self.cache_ttl:
            return self._secret_cache[cache_key]
        
        # If no client or not authenticated, return default
        if not self.client:
            return default
        
        try:
            # Get secret from Vault
            secret_response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point=self.mount_point
            )
            
            # Extract data
            secret_data = secret_response.get("data", {}).get("data", {})
            
            # Get specific key or entire secret
            result = secret_data.get(key) if key else secret_data
            
            # Cache the result
            self._secret_cache[cache_key] = result
            self._cache_timestamps[cache_key] = current_time
            
            return result if result is not None else default
        except Exception as e:
            logger.error(f"Error retrieving secret {path}: {str(e)}")
            return default
    
    def put_secret(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Store a secret in Vault.
        
        Args:
            path: Secret path
            data: Secret data
            
        Returns:
            True if successful, False otherwise
        """
        # If no client or not authenticated, return False
        if not self.client:
            return False
        
        try:
            # Store secret in Vault
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data,
                mount_point=self.mount_point
            )
            
            # Invalidate cache for this path
            for cache_key in list(self._secret_cache.keys()):
                if cache_key.startswith(f"{path}:") or cache_key == path:
                    self._secret_cache.pop(cache_key, None)
                    self._cache_timestamps.pop(cache_key, None)
            
            return True
        except Exception as e:
            logger.error(f"Error storing secret {path}: {str(e)}")
            return False
    
    def delete_secret(self, path: str) -> bool:
        """
        Delete a secret from Vault.
        
        Args:
            path: Secret path
            
        Returns:
            True if successful, False otherwise
        """
        # If no client or not authenticated, return False
        if not self.client:
            return False
        
        try:
            # Delete secret from Vault
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=path,
                mount_point=self.mount_point
            )
            
            # Invalidate cache for this path
            for cache_key in list(self._secret_cache.keys()):
                if cache_key.startswith(f"{path}:") or cache_key == path:
                    self._secret_cache.pop(cache_key, None)
                    self._cache_timestamps.pop(cache_key, None)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting secret {path}: {str(e)}")
            return False
    
    def list_secrets(self, path: str) -> list:
        """
        List secrets at a path.
        
        Args:
            path: Secret path
            
        Returns:
            List of secret names
        """
        # If no client or not authenticated, return empty list
        if not self.client:
            return []
        
        try:
            # List secrets at path
            list_response = self.client.secrets.kv.v2.list_secrets(
                path=path,
                mount_point=self.mount_point
            )
            
            return list_response.get("data", {}).get("keys", [])
        except Exception as e:
            logger.error(f"Error listing secrets at {path}: {str(e)}")
            return []

# Create a singleton instance
vault_client = VaultClient()
