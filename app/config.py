# app/config.py
import os, sqlite3
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'ignore', '.env'))

class ConfigVars:
    """ Configuration keys for Graph API """
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    TENANT_ID = os.getenv("TENANT_ID")
    SECRET_KEY = os.getenv("SECRET_KEY") # Flask secret key
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    LOG_PATH = os.path.join(os.path.dirname(__file__), 'ignore', 'app.log')
    URL_ME = os.getenv("URL_me") # /me


class DB_Models:
    """ Database configuration & tables """
    DB_NAME = "contacts.db"
    DB_PATH = os.path.join(os.path.dirname(__file__), 'ignore', DB_NAME) # dir ignore/contacts.db

    @staticmethod
    def init_db():
        """ Create database and tables """
        conn = sqlite3.connect(DB_Models.DB_PATH)
        c = conn.cursor()
        
        # TB user
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE, -- Must be unique
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user' NOT NULL, -- user or admin
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP NOT NULL
                    )''')
        
        # TB contacts -> This client as Master DB
        # Use case when this application is the master DB
        c.execute('''CREATE TABLE IF NOT EXISTS contacts (
                    id TEXT PRIMARY KEY,                     -- string (identifier)
                    assistantName TEXT,                      -- string
                    birthday TEXT,                           -- String (timestamp)
                    businessAddress TEXT,                    -- physicalAddress als JSON
                    businessHomePage TEXT,                   -- string
                    businessPhones TEXT,                     -- Array von Strings (als JSON)
                    categories TEXT,                         -- Array von Strings (als JSON)
                    changeKey TEXT,                          -- string
                    children TEXT,                           -- Array von Strings (als JSON)
                    companyName TEXT,                        -- string
                    createdDateTime TEXT,                    -- String (timestamp)
                    department TEXT,                         -- string
                    displayName TEXT,                        -- string
                    emailAddresses TEXT,                     -- Array von EmailAddress-Objekten (als JSON)
                    fileAs TEXT,                             -- string
                    generation TEXT,                         -- string
                    givenName TEXT,                          -- string
                    homeAddress TEXT,                        -- physicalAddress als JSON
                    homePhones TEXT,                         -- Array von Strings (als JSON)
                    imAddresses TEXT,                        -- Array von Strings (als JSON)
                    initials TEXT,                           -- string
                    jobTitle TEXT,                           -- string
                    lastModifiedDateTime TEXT,               -- String (timestamp)
                    manager TEXT,                            -- string
                    middleName TEXT,                         -- string
                    mobilePhone TEXT,                        -- string
                    nickName TEXT,                           -- string
                    officeLocation TEXT,                     -- string
                    otherAddress TEXT,                       -- physicalAddress als JSON
                    parentFolderId TEXT,                     -- string
                    personalNotes TEXT,                      -- string
                    photo TEXT,                              -- profilePhoto als JSON (oder BLOB, je nach Bedarf)
                    profession TEXT,                         -- string
                    spouseName TEXT,                         -- string
                    surname TEXT,                            -- string
                    title TEXT,                              -- string
                    yomiCompanyName TEXT,                    -- string
                    yomiGivenName TEXT,                      -- string
                    yomiSurname TEXT,                        -- string
                    
                    user_id INTEGER NOT NULL,                   -- self added -> key to user
                    folder_id TEXT NOT NULL,                    -- self added -> key to folder
                    FOREIGN KEY(user_id) REFERENCES users(id),  -- self added
                    FOREIGN KEY(folder_id) REFERENCES folders(id) -- self added -> key to folder duplicate for my app
                  
                    )''')


        # TB contacts -> Outlook as Master DB
        # Use case when we always load the contacts from Outlook
        #c.execute('''CREATE TABLE IF NOT EXISTS contacts (
        #            id TEXT PRIMARY KEY,
        #            folder_id TEXT NOT NULL,
        #            user_id INTEGER NOT NULL,
        #            FOREIGN KEY(user_id) REFERENCES users(id)
        #          )''')
        
        
        conn.commit() # save
        conn.close() # close connection


class Tests:
    """ Test User for local database """
    name = os.getenv("test_user_a")
    email = os.getenv("test_email_a")
    password = os.getenv("test_password_a")
    role = os.getenv("test_role_a")

    def create_user(hashed_pw):
        """ Create a user by default (needs hashed pw!) """
        conn = sqlite3.connect(DB_Models.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT email FROM users WHERE email = ?", (Tests.email,))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)", (Tests.name, Tests.email, hashed_pw, Tests.role))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False


class AppMode:
    """ App modes for header. (local database, ms-exchange, logged out)"""
    # app mode will be refreshed on every / route
    localdb = "Connected to local database"
    msgraph = "Connected to Microsoft Exchange"
    nouser = "not logged in"
        

