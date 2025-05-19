
"""
Okta SSO Provider implementation.
"""
import httpx
from typing import Dict, Any
from urllib.parse import urlencode

class OktaProvider:
    """Okta OAuth2 provider for SSO authentication."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, okta_domain: str):
        """
        Initialize the Okta provider.
        
        Args:
            client_id: Okta OAuth client ID
            client_secret: Okta OAuth client secret
            redirect_uri: Callback URL for the OAuth flow
            okta_domain: Okta domain (e.g., dev-123456.okta.com)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.okta_domain = okta_domain
        self.auth_url = f"https://{okta_domain}/oauth2/v1/authorize"
        self.token_url = f"https://{okta_domain}/oauth2/v1/token"
        self.userinfo_url = f"https://{okta_domain}/oauth2/v1/userinfo"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Get the Okta authorization URL.
        
        Args:
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "login"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens and user info.
        
        Args:
            code: Authorization code from Okta
            
        Returns:
            User information from Okta
            
        Raises:
            Exception: If token exchange fails
        """
        # Exchange code for tokens
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(self.token_url, data=token_data)
            
            if token_response.status_code != 200:
                raise Exception(f"Failed to exchange code for token: {token_response.text}")
            
            token_json = token_response.json()
            access_token = token_json.get("access_token")
            
            if not access_token:
                raise Exception("No access token in response")
            
            # Get user info with access token
            headers = {"Authorization": f"Bearer {access_token}"}
            userinfo_response = await client.get(self.userinfo_url, headers=headers)
            
            if userinfo_response.status_code != 200:
                raise Exception(f"Failed to get user info: {userinfo_response.text}")
            
            return userinfo_response.json()
