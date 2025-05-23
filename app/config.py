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
                    assistantName TEXT,
                    birthday TEXT,
                    businessAddress TEXT,                  -- JSON: microsoft.graph.physicalAddress
                    businessHomePage TEXT,
                    businessPhones TEXT,                   -- JSON: list of strings
                    categories TEXT,                       -- JSON: list of strings
                    changeKey TEXT,
                    children TEXT,                         -- JSON: list of strings
                    companyName TEXT,
                    createdDateTime TEXT,
                    department TEXT,
                    displayName TEXT,
                    emailAddresses TEXT,                   -- JSON: list of microsoft.graph.emailAddress
                    fileAs TEXT,
                    generation TEXT,
                    givenName TEXT,
                    homeAddress TEXT,                      -- JSON: microsoft.graph.physicalAddress
                    homePhones TEXT,                       -- JSON: list of strings
                    id TEXT PRIMARY KEY,                   -- string (identifier)
                    imAddresses TEXT,                      -- JSON: list of strings
                    initials TEXT,
                    jobTitle TEXT,
                    lastModifiedDateTime TEXT,
                    manager TEXT,
                    middleName TEXT,
                    mobilePhone TEXT,
                    nickName TEXT,
                    officeLocation TEXT,
                    otherAddress TEXT,                     -- JSON: microsoft.graph.physicalAddress
                    parentFolderId TEXT,
                    personalNotes TEXT,
                    photo TEXT,                            -- JSON: microsoft.graph.profilePhoto
                    profession TEXT,
                    spouseName TEXT,
                    surname TEXT,
                    title TEXT,
                    yomiCompanyName TEXT,
                    yomiGivenName TEXT,
                    yomiSurname TEXT,

                    user_id INTEGER NOT NULL,                   -- foreign key to users table
                    folder_id TEXT DEFAULT 'standalone',        -- default folder
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(folder_id) REFERENCES folders(id)
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
        

