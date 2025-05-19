
"""
Microsoft SSO Provider implementation.
"""
import httpx
from typing import Dict, Any
from urllib.parse import urlencode

class MicrosoftProvider:
    """Microsoft OAuth2 provider for SSO authentication."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant: str = "common"):
        """
        Initialize the Microsoft provider.
        
        Args:
            client_id: Microsoft OAuth client ID
            client_secret: Microsoft OAuth client secret
            redirect_uri: Callback URL for the OAuth flow
            tenant: Microsoft tenant (default: common)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.tenant = tenant
        self.auth_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
        self.graph_url = "https://graph.microsoft.com/v1.0/me"
    
    def get_authorization_url(self, state: str) -> str:
        """
        Get the Microsoft authorization URL.
        
        Args:
            state: State parameter for CSRF protection
            
        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile User.Read",
            "state": state,
            "prompt": "select_account"
        }
        
        return f"{self.auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens and user info.
        
        Args:
            code: Authorization code from Microsoft
            
        Returns:
            User information from Microsoft Graph API
            
        Raises:
            Exception: If token exchange fails
        """
        # Exchange code for tokens
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile User.Read"
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
            userinfo_response = await client.get(self.graph_url, headers=headers)
            
            if userinfo_response.status_code != 200:
                raise Exception(f"Failed to get user info: {userinfo_response.text}")
            
            user_data = userinfo_response.json()
            
            # Map Microsoft Graph API response to standard format
            return {
                "sub": user_data.get("id"),
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "name": user_data.get("displayName"),
                "given_name": user_data.get("givenName"),
                "family_name": user_data.get("surname"),
                "preferred_username": user_data.get("userPrincipalName")
            }
