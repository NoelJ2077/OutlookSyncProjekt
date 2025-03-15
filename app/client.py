# app/client.py
import requests, logging
from app.config import Config

logger = logging.getLogger(__name__)

class GraphClient:
    """Client to interact with the Microsoft Graph API."""

    _instance = None

    def __new__(cls, user_id=None):
        """ Singleton to ensure only one instance of the class is created. """
        if cls._instance is None:
            cls._instance = super(GraphClient, cls).__new__(cls)
            cls._instance._initialize(user_id)
        elif user_id and cls._instance.user_id != user_id:
            cls._instance.user_id = user_id # update user_id if different
        return cls._instance

    def _initialize(self, user_id):
        self.token_url = f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/v2.0/token"
        self.contacts_url = "https://graph.microsoft.com/v1.0/me/contacts" # get contacts from any user within the tenant
        self.client_id = Config.CLIENT_ID
        self.client_secret = Config.CLIENT_SECRET
        #self.scope = "User.Read Contacts.ReadWrite"
        self.scope = "https://graph.microsoft.com/.default" # for multi tenant use
        self.redirect_uri = Config.REDIRECT_URI
        self.user_id = user_id
        self.access_token = None
        self.headers = None

    def get_access_token(self, authorization_code=None):
        """ Get access token if authorization code is provided (OAuth 2.0 Flow), else use client credentials flow first."""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
        }

        if authorization_code:
            logger.debug("Using authorization code flow.")
            payload.update({
                "scope": self.scope,
                "code": authorization_code,
                "grant_type": "authorization_code"
            })
        else: # should never be the case ?
            logger.debug("Using client credentials flow.")
            payload.update({
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            })

        response = requests.post(self.token_url, data=payload)
        response.raise_for_status()
        self.access_token = response.json().get("access_token")
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        return self.access_token

    def get_auth_redirect_url(self):
        """ Get the URL to redirect the user to the Microsoft login page."""
        return (
            f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/v2.0/authorize?"
            f"response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scope}"
        )

    def get_contacts(self):
        """ Get contacts Outlook contacts from user_id."""
        if not self.access_token:
            return False
        response = requests.get(self.contacts_url, headers=self.headers)
        response.raise_for_status()
        logger.debug(f"Received {len(response.json().get('value', []))} contacts ")
        return response.json().get("value", [])

    def reset(self):
        """ Reset the client, e.g. after logout."""
        logger.info("Resetting GraphClient.")
        self.access_token = None
        self.headers = None
        self.user_id = None
        # session from oauth2 is still valid!