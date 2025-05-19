
"""
Google SSO Provider implementation.
"""
import httpx
from typing import Dict, Any
from urllib.parse import urlencode

class GoogleProvider:
    """Google OAuth2 provider for SSO authentication."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize the Google provider.
        
        Args:
            client_id: Google OAuth client ID
            client_secret: Google OAuth client secret
            redirect_uri: Callback URL for the OAuth flow
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Get the Google authorization URL.
        
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
            "prompt": "select_account",
            "access_type": "offline"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens and user info.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            User information from Google
            
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
