#app/routes.py
from app.helpermethods import * # Methods before client interacctions. (converte data etc.)
from app.client_actions import get_contacts, create_contact, update_contact, get_contact, delete_contact
from app.client import GraphClient
import logging
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify

main = Blueprint('main', __name__)
user = Blueprint('user', __name__)

logger = logging.getLogger(__name__)

def login_required(f):
    """ Decorator to check if user is logged in via session """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #logger.debug(f"Session: {session}")
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
        # set all to None via lambda
        username, email, role = map(lambda x: None, range(3))

    mode = get_app_mode()
    #logger.debug(f"Index page: {username}, {email}, {role}, /{mode}")

    return render_template("index.html", username=username, email=email, db_role=role, app_mode=mode)


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """ Dashboard page """
    logger.debug(f"/main.dashboard")

    user_d = get_user_data(session['user_id'])
    username = user_d['username']
    email = user_d['email']
    role = user_d['role']
    created_at = user_d['created_at']
    mode = get_app_mode()
    schema = load_schema()
    
    try:
        #logger.debug(f"Session: {session}")
        client = GraphClient(session.get('access_token'))
        if not client:
            logger.error("Client not found in session")
            return redirect(url_for('user.login'))
        contacts_list = get_contacts(client)
        contacts = [format_contact(c) for c in contacts_list]

    except Exception as e:
        # error logging already done in methods.
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
    client = GraphClient(session.get('access_token'))

    if action == "create":
        pass
    elif action == "update":
        
        contact_id = request.form.get("contact_id")
        fields = get_con_fields()# todo: alle request.form.get da rein

        resp_code = update_contact(contact_id, client)
        if resp_code == 204:
            flash('Updated 1 contact!', 'info')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Failed to update 1 contact!', 'danger')
            return redirect(url_for('main.index'))
        
    elif action == "delete":
        # contact_id is passed with action.
        contact_id = request.form.get("contact_id")
        #logger.debug(f"ID: {contact_id}") # ok
        resp_code = delete_contact(contact_id, client)
        if resp_code == 204:
            flash('Deleted 1 contact!', 'info')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Failed to delete 1 contact!', 'danger')
            return redirect(url_for('main.index'))
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
        client = GraphClient(session.get('access_token'))
        
        contacts_list = get_contacts(client)
        if not contacts_list:
            flash('You have no contacts to backup.', 'info')
            return redirect(url_for('main.dashboard'))
        
        # call method with list
        backup_contacts_to_db(contacts_list, session['user_id'])
        flash('Contacts backed up successfully', 'success')
        return redirect(url_for('main.dashboard'))
    
    except Exception as e:
        logger.error(f"Backup contacts failed: {e}")
        flash('Failed to backup contacts', 'danger')
        return redirect(url_for('main.dashboard'))

# --- JavaScript Routes --- 
@main.route("/get_contact/<contact_id>")
def get_contact_js(contact_id):
    
    client = GraphClient(session.get('access_token'))

    contact = get_contact(contact_id, client)

    return contact

# --- User Routes ---
@user.route("/login", methods=["GET", "POST"])
def login():
    """ Login page -> get_auth_url() -> redirect back to /callback """
    logger.debug(f"/user.login")

    if 'user_id' in session:
        flash('You are already logged in', 'info')
        logger.debug("User already logged in, redirecting to dashboard")
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user_id = check_login(email, password)
        
        if user_id:
            session['user_id'] = user_id
            logger.debug(f"DB Login successful: {email}")
            client = GraphClient()
            client.user_id = user_id
            return redirect(client.get_auth_url())
        else:
            logger.debug(f"DB Login failed: {email}")
            flash('Login failed, invalid email or password', 'danger')
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

        # create client
        client = GraphClient()
        client.user_id = user_id
        client.get_access_token(code)

        # check both logins!
        ms_user = client.get_me()
        ms_email = ms_user.get("userPrincipalName") or ms_user.get("mail")
        if not ms_email:
            flash("Unable to get Email from Microsoft Graph!", "danger")
            return redirect(url_for('main.index'))
        # Check logins 
        user_d = get_user_data(user_id) # Problem, wurde bereits im callback überschrieben glaube ich!!!
        local_mail = user_d['email']

        if not local_mail or ms_email.lower() != local_mail:
            logger.warning(f"Email mismatch: local={local_mail}, ms={ms_email}")
            session.clear()
            logout_url = client.logout()

            # Render mismatch page with auto-redirect
            return render_template("modals/nonmodal_err.html",
                                   ms_email=ms_email,
                                   local_email=local_mail,
                                   logout_url=logout_url)

        # success
        session['user_id'] = user_id
        session['access_token'] = client.access_token
        session['refresh_token'] = client.refresh_token_value
        session['token_expires_at'] = client.token_expires_at

        return redirect(url_for('main.dashboard'))

    else:
        return redirect(url_for('user.login'))

@user.route("/register", methods=["GET", "POST"])
def register():
    """ Register page """
    logger.debug(f"/user.register")

    if 'user_id' in session:
        flash('You are already logged in', 'info')
        logger.debug("User already logged in, redirecting to dashboard")
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
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
    """ Logout user incl. from Microsoft account. """
    logger.debug(f"/user.logout")

    try:
        client = GraphClient(session.get('access_token'))
        session.clear()
        return redirect(client.logout())

    except Exception as e:
        logger.error(f"Logout failed: {e}")
        flash('Logout failed', 'danger')
        return redirect(url_for('main.index'))
    
