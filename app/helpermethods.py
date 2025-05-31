# login process, check db stuff etc.
# If login yes but not in Tenant, error / 403
import sqlite3, logging, json, datetime
from app.config import DB_Models, AppMode
from app.ignore.hashing import check_domain, hash_password, verify_password
from flask import session

logger = logging.getLogger(__name__)

get_app_mode = lambda: AppMode.msgraph if 'access_token' in session else AppMode.localdb if 'user_id' in session else AppMode.nouser

def check_login(email, password):
    """ Check if the email exists in the database and if the password is correct. 
    - returns the user_id (int)
    """
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
            logger.debug(f"Local login successful for: {email}", "success")
            # return email
            return email
        
        logger.debug(f"Local login failed for: {email}", "danger")
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

def get_user_data(email):
    """ Gets user data from user_id(mail) in database and return a dict.  
    - username
    - email
    - role
    - created_at
    """
    try:
        conn = sqlite3.connect(DB_Models.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, email, role, created_at FROM users WHERE email = ?", (email,))
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
            data = {
                "username": None,
                "email": None,
                "role": None,
                "created_at": None
            }
            return data
            
    except sqlite3.DatabaseError as e:
        logger.error(f"Error: {e}")
        return False

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

def format_date(date_str):
    """ Formats a date from ISO 8601 to a swiss date format: 'dd Month YYYY'. """
    if not date_str:
        return None
    try:
        date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date.strftime("%d %B %Y")
    except ValueError:
        logger.error(f"Invalid date format: {date_str}")
        return None

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
        contact["customAddressList"] = [{"address": a} for a in addresses] if addresses else []

        # company fallback
        contact["companyName"] = contact.get("companyName") or "—"
        
        contact["extra_fields"] = []
        # veraltet als dict
        extra_fields = [
            ("MiddleName", contact.get("middleName")),
            ("Nickname", contact.get("nickName")),
            ("Initials", contact.get("initials")),
            ("Birthday", format_date(contact.get("birthday"))),
            ("Department", contact.get("department")),
            ("Job title", contact.get("jobTitle")),
            ("Manager", contact.get("manager")),
            ("Assistant", contact.get("assistantName")),
            ("Spouse", contact.get("spouseName")),
            ("Profession", contact.get("profession")),
            ("Title", contact.get("title")),
        ]
        # Nur füllen, wenn nicht leere Felder
        for key, value in extra_fields:
            if value:
                contact["extra_fields"].append({"name": key, "value": value})
            
        return contact

    except Exception as e:
        logger.error(f"Fehler beim Formatieren eines Kontakts: {e}")
        return contact

def load_schema():
    """ Gets contact schema from JSON file, returns a dict. """
    with open("app/static/ressource.json", "r") as f:
        schema = json.load(f)
        #logger.debug(f"Contact schema loaded with {len(schema)} fields.")
    return schema

def serialize_fields(fields):
    """Convert dicts/lists to JSON strings, leave others as-is. Used to store other data types in TEXT fields."""
    serialized = {}
    for k, v in fields.items():
        if isinstance(v, (list, dict)):
            serialized[k] = json.dumps(v)
        else:
            serialized[k] = v
    return serialized

def backup_contacts_to_db(contacts_list, user_id):
    """ Create a local backup of all Outlook contacts."""
    try:
        conn = sqlite3.connect(DB_Models.DB_PATH)
        c = conn.cursor()
        #logger.debug(f"first contact all data: {contacts_list[0] if contacts_list else 'No contacts to backup'}")
        
        for con in contacts_list:
            # filter out metadata fields starting with '@'
            c_fields = {k: v for k, v in con.items() if not k.startswith('@')}
            # convert dicts/lists (metadata) fields to JSON strings for type TEXT
            c_fields = serialize_fields(c_fields)

            fields = ", ".join(c_fields.keys())
            placeholders = ", ".join(["?"] * len(c_fields))
            # udd user_id (email) 
            query = f"INSERT OR REPLACE INTO contacts ({fields}, user_id) VALUES ({placeholders}, ?)"
            values = list(c_fields.values()) + [user_id]
            c.execute(query, values)

        conn.commit()
        conn.close()
        return True

    except sqlite3.DatabaseError as e:
        logger.error(f"Error connecting to database: {e}")
        return False


