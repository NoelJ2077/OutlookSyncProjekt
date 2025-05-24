# app/client_actions.py
import logging, requests
from app.config import ConfigVars
from app.client import GraphClient

logger = logging.getLogger(__name__)

# lambda method to check if client:
hasClient = lambda c: c if c else GraphClient()

def get_contacts(client):
    """ Get all contacts from the user. Needs to be called with a client instance. """

    client = hasClient(client)

    headers = {"Authorization": "Bearer %s" % client.access_token}
    
    try:
        response = requests.get(ConfigVars.URL_ME, headers=headers)
        response.raise_for_status()
        logger.debug(f"Received: {len(response.json().get('value', []))} contacts")
        return response.json().get("value", [])
    except requests.RequestException as e:
        logger.error("Failed to get contacts: %s" % e)
        raise

def get_contact(contact_id, client):
    """ Get a single contact by ID, used for editing. """

    client = hasClient(client)
    
    headers = {"Authorization": "Bearer %s" % client.access_token}
    try:
        response = requests.get(f"{ConfigVars.URL_ME}/{contact_id}", headers=headers)
        response.raise_for_status()
        logger.debug(f"Received contact: {contact_id[:10]}")
        return response.json()
    except requests.RequestException as e:
        logger.error("Failed to get contact: %s" % e)
        raise

def create_contact(contact, client):
    """ Create a new contact using the globally available client """

    client = hasClient(client)
    
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

def update_contact(contact_id):
    """ Edit an existing contact """
    logger.debug("Editing contact: %s" % contact_id)
    pass

def delete_contact(contact_id, client):
    """ Delete 1 or selected contact(s). """
    
    client = hasClient(client)

    headers = {"Authorization": "Bearer %s" % client.access_token}
    try:
        response = requests.delete(f"{ConfigVars.URL_ME}/{contact_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Failed to delete contact: %s" % e)
        raise

