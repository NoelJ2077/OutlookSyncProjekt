# app/client_actions.py
import logging, requests
from app.config import ConfigVars
# import client
from app import client

logger = logging.getLogger(__name__)

def get_contacts():
    """ Get all contacts using the globally available client """
    logger.debug("Calling get_contacts via actions module")
    client.ensure_valid_token()
    headers = {"Authorization": "Bearer %s" % client.access_token}
    
    try:
        response = requests.get(ConfigVars.URL_ME, headers=headers)
        response.raise_for_status()
        return response.json().get("value", [])
    except requests.RequestException as e:
        logger.error("Failed to get contacts: %s" % e)
        raise

def create_contact(contact):
    """ Create a new contact using the globally available client """
    logger.debug("Calling create_contact via actions module")
    client.ensure_valid_token()
    headers = {
        "Authorization": "Bearer %s" % client.access_token,
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(ConfigVars.URL_ME, headers=headers, json=contact)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Failed to create contact: %s" % e)
        raise
