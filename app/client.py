# app/client.py
import requests, logging, time
from app.config import ConfigVars


logger = logging.getLogger(__name__)

class GraphClient:
    def __init__(self, access_token=None): # can be called with a token for example from a session
        self.token_url = f"https://login.microsoftonline.com/{ConfigVars.TENANT_ID}/oauth2/v2.0/token"
        self.user_id = None
        self.client_id = ConfigVars.CLIENT_ID
        self.client_secret = ConfigVars.CLIENT_SECRET
        self.scope = "https://graph.microsoft.com/.default offline_access"  # `offline_access` für refresh_token
        self.redirect_uri = ConfigVars.REDIRECT_URI
        self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        self.access_token = access_token
        self.refresh_token_value = None
        self.token_expires_at = 0

    def get_auth_url(self):
        """ Get OAuth2 Authorization URL """
        base_url = f"https://login.microsoftonline.com/{ConfigVars.TENANT_ID}/oauth2/v2.0/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "response_mode": "query",
            "scope": self.scope,
            "state": self.user_id
        }
        auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        #logger.debug(f"Generated auth URL: {auth_url[:10]} ...")
        return auth_url

    def refresh_token(self):
        """ Refresh token, if None, raise error """
        if not self.refresh_token_value:
            raise ValueError("No refresh token available")
        data = {
            "client_id": self.client_id,
            "scope": self.scope,
            "refresh_token": self.refresh_token_value,
            "grant_type": "refresh_token",
            "client_secret": self.client_secret
        }
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token_value = token_data.get("refresh_token", self.refresh_token_value)
            self.token_expires_at = time.time() + token_data.get("expires_in", 3600)
            
        except requests.RequestException as e:
            logger.error(f"Failed to refresh token: {e}")
            raise
   
    def get_access_token(self, code):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        try:
            response = requests.post(self.token_url, data=data)
            response.raise_for_status()
            token = response.json()
            self.access_token = token.get("access_token")
            self.refresh_token_value = token.get("refresh_token")
            self.token_expires_at = time.time() + token.get("expires_in", 3600)
            #logger.debug(f"Access token: {self.access_token[:10]} ...")
            
        except requests.RequestException as e:
            logger.error(f"Failed to get access token: {e}")
            raise
   
    def get_me(self):
        """Fetch user profile from Microsoft Graph API (/me endpoint)."""
        if not self.access_token:
            raise ValueError("No access token available for /me request")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        try:
            response = requests.get(ConfigVars.URL_ME, headers=headers)
            response.raise_for_status()
            logger.debug("Got User profile after login.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch /me: {e}")
            raise



    def logout(self):
        """ Logout from Account """
        base_url = f"https://login.microsoftonline.com/{ConfigVars.TENANT_ID}/oauth2/v2.0/logout"
        params = {
            "post_logout_redirect_uri": ConfigVars.REDIRECT_URI
        }
        logout_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        #logger.debug(f"Logout URL: {logout_url}")
        return logout_url
    

