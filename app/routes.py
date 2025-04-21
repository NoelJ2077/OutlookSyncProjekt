#app/routes.py
from app.helpermethods import * # check_login, get_username, get_current_app_mode
from app import client
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
        if session.get('user_id') is None:
            flash('Login required', 'danger')
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- User Routes ---
@user.route("/login", methods=["GET", "POST"])
def login():
    """ Login page -> get_auth_url() -> redirect back to /callback """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        logger.debug(f"Login attempt: {email}")
        user_id = check_login(email, password)
        session['user_id'] = user_id
        if user_id:
            # set user data from method set_user() -> dict(4)
            session['username'], session['email'], session['db_role'], session['created_at'] = set_user(user_id).values()
            flash('DB Login successful', 'success')
            logger.debug(f"DB Login successful: {email}")
            client.set_user_id(session['email']) # set email for /users/{email}/contacts
            return redirect(client.get_auth_url())
        else:
            flash('Login failed', 'danger')
            logger.debug(f"DB Login failed: {email}")
            return redirect(url_for('main.index'))
        
    
    app_mode = get_app_mode()
    return render_template('login.html', app_mode=app_mode, role=session.get('db_role', 'guest'))

@user.route("/callback", methods=["GET"])
def callback():
    """ Callback from /login -> get_auth_url() -> redirect back to /callback """
    code = request.args.get('code')
    if code:
        logger.debug(f"Callback with code: {code[:10]}")
        client.get_access_token(code)
        session['access_token'] = client.access_token
        session['refresh_token'] = client.refresh_token_value  # Update this
        session['token_expires_at'] = client.token_expires_at
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('user.login'))

@user.route("/register", methods=["GET", "POST"])
def register():
    """ Register page """
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
    session.clear() # clear all session data
    client.access_token = None
    client.refresh_token_value = None
    client.token_expires_at = None

    flash('Logout successful', 'success')
    return redirect(url_for('main.index'))


# --- Main Routes ---
@main.route("/", methods=["GET"])
def index():
    """ Index page """
    username = session.get('username', '/Guest')
    email = session.get('email', '/Guest')
    role = session.get('db_role', '/guest')
    mode = get_app_mode()
    logger.debug(f"Index page: {username}, {email}, {role}, /{mode}")

    return render_template("index.html", username=username, email=email, db_role=role, app_mode=mode)


@main.route("/refresh", methods=["GET"])
@login_required
def refresh_page():
    try:
        client.get_token_from_session(session)
        client.ensure_valid_token()
    except Exception as e:
        logger.error(f"/r Error: {e}")
        return redirect(url_for('main.index'))
    return redirect(url_for('main.dashboard'))


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """ Dashboard page """
    username = session.get('username', '/Guest')
    email = session.get('email', '/Guest')
    role = session.get('db_role', '/guest')
    mode = get_app_mode()
    logger.debug(f"Dashboard page: {username}, {email}, {role}, {mode}")
    try:
        client.get_token_from_session(session)
        # get all contacts 
        contacts_list = client.get_contacts()
        contacts = [format_contact(c) for c in contacts_list]
        logger.info(f"Found {len(contacts)} contacts for: {email}")
    except Exception as e:
        logger.error(f"d/ Error: {e}")
        return redirect(url_for('main.index'))
    
    return render_template("dashboard.html", username=username, email=email, user_role=role, app_mode=mode, contacts=contacts)


# contact/<action> routes
@main.route("/contact/<action>", methods=["POST"])
@login_required
def contact_action(action):
    """ Crreate, update, delete contact """
    action = request.form.get('action')
    logger.debug(f"Contact action: {action}")
    
    if action == 'create':
        pass
    elif action == 'update':
        pass
    elif action == 'delete':
        pass
    else:
        logger.error(f"Invalid action: {action}")
        return redirect(url_for('main.dashboard'))
    
