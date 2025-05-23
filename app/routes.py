#app/routes.py
from app.helpermethods import * # Methods before client interacctions. (converte data etc.)
from app.client_actions import get_contacts, create_contact, update_contact, get_contact, delete_contact
from app.client import get_client_from_session
import logging
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, session, flash

main = Blueprint('main', __name__)
user = Blueprint('user', __name__)

logger = logging.getLogger(__name__)

def login_required(f):
    """ Decorator to check if user is logged in via session """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Session: {session}")
        if 'user_id' not in session:
            flash('You need to log in first', 'danger') # problem hier. login hat geklappt, aber session ist leer
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Main Routes ---
@main.route("/", methods=["GET"])
def index():
    """ Index page """
    logger.debug(f"/main.index")

    #logger.debug(f"Session: {session}")
    user_d = get_user_data(session.get('user_id'))
    if user_d:
        username = user_d['username']
        email = user_d['email']
        role = user_d['role']
    else:
        # set all to Guest via lambda
        username, email, role = map(lambda x: None, range(3))

    mode = get_app_mode()
    #logger.debug(f"Index page: {username}, {email}, {role}, /{mode}")

    return render_template("index.html", username=username, email=email, db_role=role, app_mode=mode)


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """ Dashboard page """
    logger.debug(f"/main.dasboard")

    user_d = get_user_data(session['user_id'])
    username = user_d['username']
    email = user_d['email']
    role = user_d['role']
    created_at = user_d['created_at']
    mode = get_app_mode()
    schema = load_schema()
    
    try:
        client = get_client_from_session()
        if not client:
            logger.error("Client not found in session")
            return redirect(url_for('user.login'))
        contacts_list = get_contacts(client)
        contacts = [format_contact(c) for c in contacts_list]

    except Exception as e:
        logger.error(f"d/ Error: {e}")
        return redirect(url_for('main.index'))
    
    return render_template("dashboard.html", username=username, email=email, user_role=role, app_mode=mode, contacts=contacts, schema=schema)

# contact/<action> routes
@main.route("/contact/<action>", methods=["POST"])
@login_required
def contact(action):
    """ create, update, delete 1 or multiple contacts
    - using 1 main modal for all actions. 
    """
    logger.debug(f"/main.contact{action}")

    if action == "create":
        pass
    elif action == "update":
        pass
    elif action == "delete":
        pass
    else:
        logger.error(f"Invalid action: {action}")
        flash('Invalid action', 'danger')
        return redirect(url_for('main.dashboard'))
    
@main.route("/backup_contacts", methods=["GET"])
@login_required
def backup_contacts():
    """ Backup contacts to local database """
    logger.debug(f"/main.backup_contacts")

    try:
        #client.get_token_from_session(session)
        #client.ensure_valid_token()
        contacts = get_contacts()
        
        # make a backup of contacts locally. 
        for con in contacts:
            create_backup(con)
        logger.info(f"{len(contacts)} contacts backed up")

        flash('Contacts backed up successfully', 'success')
        logger.debug(f"Contacts backed up successfully")
    except Exception as e:
        logger.error(f"Failed to backup contacts: {e}")
        flash('Failed to backup contacts', 'danger')
    return redirect(url_for('main.dashboard'))


# --- User Routes ---
@user.route("/login", methods=["GET", "POST"])
def login():
    """ Login page -> get_auth_url() -> redirect back to /callback """
    logger.debug(f"/user.login")
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_id = check_login(email, password)
        session['user_id'] = user_id
        if user_id:
            logger.debug(f"DB Login successful: {email}")
            client = GraphClient() # neu so?
            client.set_user_id(user_id) # sets email, used as key for all requests
            return redirect(client.get_auth_url())
        else:
            logger.debug(f"DB Login failed: {email}")
            return redirect(url_for('main.index'))
        
    
    app_mode = get_app_mode()
    return render_template('login.html', app_mode=app_mode, role=session.get('db_role', 'guest'))

@user.route("/callback", methods=["GET"])
def callback():
    """ Callback from /login -> get_auth_url() -> redirect back to /callback """
    logger.debug(f"/user.callback")

    code = request.args.get('code')
    user_id = request.args.get('state')
    if code and user_id:
        #logger.debug(f"Callback with code: {code[:10]}")
        client = GraphClient() # neu so?
        client.user_id = user_id
        session['user_id'] = user_id
        client.get_access_token(code)
        
        
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('user.login'))

@user.route("/register", methods=["GET", "POST"])
def register():
    """ Register page """
    logger.debug(f"/user.register")

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        logger.debug(f"Register attempt: {email}")
        if check_register(username, email, password):
            flash('Registration successful', 'success')
            logger.debug(f"Registration successful: {email}")
            return redirect(url_for('user.login'))
        else:
            flash('Registration failed', 'danger')
            logger.debug(f"Registration failed: {email}")
            return redirect(url_for('user.register'))
    
    app_mode = get_app_mode()
    return render_template('register.html', app_mode=app_mode)

@user.route("/logout", methods=["GET"])
def logout():
    """ Logout user """
    logger.debug(f"/user.logout")

    session.clear() # clear all session data
    
    flash('Logout successful', 'success')
    return redirect(url_for('main.index'))
