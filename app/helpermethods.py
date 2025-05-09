# login process, check db stuff etc.
# If login yes but not in Tenant, error / 403
import sqlite3, logging, requests
from app.config import DB_Models, AppMode
from app.ignore.hashing import check_domain, hash_password, verify_password
from flask import session
from app.client import GraphClient

logger = logging.getLogger(__name__)

def check_login(email, password):
    """ Check if the email exists in the database and if the password is correct. """
    try:
        if not check_domain(email):
            splitdomain = email.split("@")
            logger.debug(f"This domain is not allowed: '{splitdomain[1]}'")
            return False

        conn = sqlite3.connect(DB_Models.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT password, id FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and verify_password(password, user[0]):
            logger.debug(f"Local login successful for: {email}")
            return user[1] # user_id
        
        logger.debug(f"Local login failed for: {email}")
        return False
    except sqlite3.DatabaseError as e:
        logger.error(f"Error: {e}")

def check_register(username, email, password):
    """ First check if the domain is allowed, then check if the email is already in the database. If not, register the user. """
    try:
        if not check_domain(email):
            splitdomain = email.split("@")
            logger.debug(f"Domain: {splitdomain[1]} not allowed")
            return False
        
        conn = sqlite3.connect(DB_Models.DB_PATH)
        c = conn.cursor()

        # check if email exists
        c.execute("SELECT email FROM users WHERE email = ?", (email,))
        user = c.fetchone()

        if user:
            logger.debug(f"Email '{email}' already exists")
            conn.close()
            return False
        else:
            hashed_pw = hash_password(password)
            c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_pw))
            conn.commit()
            conn.close()
            
            return True
    except sqlite3.DatabaseError as e:
        logger.error(f"Error: {e}")
        return False

def set_user(u_id):
    """ Set user session variables. (username, role, login time)"""
    try:
        conn = sqlite3.connect(DB_Models.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, email, role, created_at FROM users WHERE id = ?", (u_id,))
        user = c.fetchone()
        conn.close()

        if user:
            data = {
                "username": user[0],
                "email": user[1],
                "role": user[2],
                "created_at": user[3]
            }
            return data
        else:
            return False
    except sqlite3.DatabaseError as e:
        logger.error(f"Error: {e}")
        return False

def get_app_mode():
    """Get current API Status."""

    if 'access_token' in session:
        return AppMode.msgraph
    elif 'user_id' in session:
        return AppMode.localdb
    else:
        return AppMode.nouser

def format_address(prefix, c_address):
    if not c_address:
        return None

    street = c_address.get("street")
    city = c_address.get("city")
    postal_code = c_address.get("postalCode")
    country = c_address.get("countryOrRegion")

    parts = []
    if street:
        parts.append(street)
    if city or postal_code:
        parts.append(", ".join(filter(None, [city, postal_code])))
    if country:
        parts.append(country)

    # HTML-Zeilenumbrüche statt \n
    formatted = "<br>".join(parts)
    return f"<strong>{prefix}:</strong><br>{formatted}" if formatted else None

def format_contact(contact):
    """Render each contact in a custom format."""
    try:
        contact["displayName"] = contact.get("displayName") or "—"
        # mails
        email = None
        if contact.get("emailAddresses") and contact["emailAddresses"]:
            email = contact["emailAddresses"][0].get("address")
        contact["primaryEmail"] = email or "—"

        # phones example output: <strong>Mobile:</strong>+number<\t><strong>Business:</strong>+number
        phones = [] 
        phone_types = [
            ("Business phone", contact.get("businessPhones")),
            ("Mobile phone", contact.get("mobilePhone")),
            ("Home phone", contact.get("homePhones"))
        ]
        for prefix, c_phone in phone_types:
            if c_phone:
                if isinstance(c_phone, list):
                    for number in c_phone:
                        phones.append(f"<strong>{prefix}:</strong> {number}")
                else:
                    phones.append(f"<strong>{prefix}:</strong> {c_phone}")
        #contact["customPhoneList"] = phones if phones else []
        contact["customPhoneList"] = [{"phone": p} for p in phones] if phones else []

        # addresses
        addresses = []
        adr_types = [
            ("Business Address", contact.get("businessAddress")),
            ("Home Address", contact.get("homeAddress")),
            ("Other Address", contact.get("otherAddress"))
        ]
        for prefix, c_address in adr_types:
            formatted_address = format_address(prefix, c_address)
            if formatted_address:
                addresses.append(formatted_address)
        #contact["customAddressList"] = addresses if addresses else []
        contact["customAddressList"] = [{"address": a} for a in addresses] if addresses else []

        
        
        # Firma-Fallback
        contact["companyName"] = contact.get("companyName") or "—"

        return contact

    except Exception as e:
        logger.error("Fehler beim Formatieren eines Kontakts: %s", e)
        return contact
