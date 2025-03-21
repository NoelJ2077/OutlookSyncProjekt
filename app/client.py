# app/client.py
import requests, logging
from app.config import Config

logger = logging.getLogger(__name__)

class GraphClient:
    """Client to interact with the Microsoft Graph API."""

    def __init__(self, user_id=None):
        self.user_id = user_id
        self.token_url = f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/v2.0/token"
        self.contacts_url = "https://graph.microsoft.com/v1.0/me/contacts"
        self.client_id = Config.CLIENT_ID
        self.client_secret = Config.CLIENT_SECRET
        self.scope = "https://graph.microsoft.com/.default"
        self.redirect_uri = Config.REDIRECT_URI
        self.access_token = None
        self.headers = None


    def get_access_token(self, authorization_code=None):
        if self.access_token:
            return self.access_token  # Reuse existing token

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
        else:
            logger.debug("Using client credentials flow.")
            payload.update({
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            })

        response = requests.post(self.token_url, data=payload)
        response.raise_for_status()
        self.access_token = response.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

        return self.access_token



    def get_auth_redirect_url(self):
        """ Get the URL to redirect the user to the Microsoft login page."""
        return (
            f"https://login.microsoftonline.com/{Config.TENANT_ID}/oauth2/v2.0/authorize?"
            f"response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scope}"
        )

    def get_contacts(self):
        """ Get contacts Outlook contacts from user_id."""
        response = requests.get(self.contacts_url, headers=self.headers)
        response.raise_for_status()
        return response.json().get("value")

    def reset(self):
        """ Reset the client, e.g. after logout."""
        logger.info("Resetting GraphClient.")
        self.access_token = None
        self.headers = None
        self.user_id = None
        # session from oauth2 is still valid!

    def export_contact(self, contacts):
        logger.debug("Exporting contact to Outlook.")
        for item in contacts:
            response = requests.post(self.contacts_url, headers=self.headers, json=item)
            if response.status_code != 201:
                logger.error(f"Failed to export contact: {response.text}")
                return False
            logger.debug(f"Exported contact {item.get('displayName')} to Outlook.")
        return True
