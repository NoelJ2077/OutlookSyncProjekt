# login process, check db stuff etc.
# If login yes but not in Tenant, error / 403
import sqlite3, bcrypt, logging
from app.config import DB_Tables
from app.ignore.hashing import check_domain, hash_password, verify_password
from flask import session

logger = logging.getLogger(__name__)

def check_login(email, password):
    """ Check if the email exists in the database and if the password is correct. """
    try:
        if not check_domain(email):
            splitdomain = email.split("@")
            logger.debug(f"This domain is not allowed: '{splitdomain[1]}'")
            return False

        conn = sqlite3.connect(DB_Tables.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and verify_password(password, user[0]):
            logger.debug(f"Local login successful for: {email}")
            return True
        
        logger.debug(f"Local login failed for: {email}")
        return False

    except sqlite3.DatabaseError as e:
        logger.error(f"Error: {e}")
        return False
    
def check_register(username, email, password):
    """ First check if the domain is allowed, then check if the email is already in the database. If not, register the user. """
    try:
        if not check_domain(email):
            splitdomain = email.split("@")
            logger.debug(f"Domain: {splitdomain[1]} not allowed")
            return False
        
        conn = sqlite3.connect(DB_Tables.DB_PATH)
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

def get_username(email):
    """ Set username and role via email from database. """
    try:
        conn = sqlite3.connect(DB_Tables.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, role FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        if user:
            return user[0], user[1] # username, role
        else:
            return None, None
    except sqlite3.DatabaseError as e:
        logger.error(f"Error: {e}")
        return None, None

class AppMode:
    """ App modes for header. (local database, ms-exchange, logged out)"""
    # app mode will be refreshed on every / route
    localdb = "Connected to local database"
    msgraph = "Connected to Microsoft Exchange"
    nouser = "not logged in"

    