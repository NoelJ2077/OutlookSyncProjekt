# app/client_actions.py
import logging, requests, json
from app.config import ConfigVars
from app.client import GraphClient

logger = logging.getLogger(__name__)

# lambda method to check if client:
hasClient = lambda c: c if c else GraphClient()

def get_contacts(client):
    """ Get all contacts from the user. Needs to be called with a client instance. """

    client = hasClient(client)

    headers = {"Authorization": f"Bearer {client.access_token}"}
    
    try:
        response = requests.get(ConfigVars.URL_CONTACTS, headers=headers)
        response.raise_for_status()
        logger.debug(f"Received: {len(response.json().get('value', []))} contacts")
        return response.json().get("value", [])
    except requests.RequestException as e:
        logger.error(f"Failed to get contacts: {e}")
        raise

def get_contact(contact_id, client):
    """ Get a single contact by ID, used for editing. """

    client = hasClient(client)
    
    headers = {"Authorization": f"Bearer {client.access_token}"}
    try:
        response = requests.get(f"{ConfigVars.URL_CONTACTS}/{contact_id}", headers=headers)
        response.raise_for_status()
        logger.debug(f"Received contact: {contact_id[:10]}")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to get contact: {e}")
        raise

def create_contact(contact, client):
    """ Create a new contact using the globally available client """

    client = hasClient(client)
    
    headers = {
        "Authorization": f"Bearer {client.access_token}",
        "Content-Type": "application/json"
    }
    try:
        #url = f"https://graph.microsoft.com/v1.0/me/contacts/{contact_id}"
        response = requests.post(ConfigVars.URL_CONTACTS, headers=headers, json=contact)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to create contact: {e}")
        raise

def update_contact(contact_id, fields):
    """ Edit an existing contact by id, convert to json object and .patch """
    
    client = hasClient(client)

    headers = {"Authorization": f"Bearer {client.access_token}"}

    data = json.dumps(fields) # should make a 

    try:
        response = requests.patch(f"{ConfigVars.URL_CONTACTS}/{contact_id}", headers=headers, data=data)
        response.raise_for_status()
        logger.info(f"Updated contact with status: {response.status_code}")
        return response.status_code
    except requests.RequestException as e:
        logger.error(f"Failed to update contact: {e}")
        raise    

def delete_contact(contact_id, client):
    """ Delete 1 or selected contact(s). """
    
    client = hasClient(client)

    headers = {"Authorization": f"Bearer {client.access_token}"}
    #logger.debug(f"token: {client.access_token[:25]}")
    try:
        response = requests.delete(f"{ConfigVars.URL_CONTACTS}/{contact_id}", headers=headers)
        response.raise_for_status()
        logger.info(f"Deleted contact with status: {response.status_code}")
        return response.status_code
    except requests.RequestException as e:
        logger.error(f"Failed to delete contact: {e}")
        raise

