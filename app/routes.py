#app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from app.client import GraphClient
from app.core import check_register, check_login, get_username, AppMode
from functools import wraps
import logging

# Blueprints erstellen
main = Blueprint('main', __name__)
user = Blueprint('user', __name__)
logger = logging.getLogger(__name__)

# Login-Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session or 'username' not in session:
            logger.warning("User not logged in, redirecting to login")
            return redirect(url_for('user.login'))
        return f(*args, **kwargs)
    return decorated_function

# Hilfsfunktion zum Berechnen des App-Modes
def get_current_app_mode():
    """Berechnet den aktuellen App-Mode basierend auf der Session."""

    if 'access_token' in session:
        return AppMode.msgraph
    elif 'username' in session:
        return AppMode.localdb
    else:
        return AppMode.nouser

# --- Main Routes ---
@main.route("/", methods=["GET"])
def index():
    """Index-Seite."""
    username = session.get('username', 'Guest')
    email = session.get('email', 'Guest')
    app_mode = get_current_app_mode()  
    logger.debug(f"Rendering index with app_mode: {app_mode}")
    
    return render_template("index.html", username=username, email=email, app_mode=app_mode)

@main.route('/home', methods=['GET'])
def home():
    """Weiterleitung zur Index-Seite."""
    return redirect(url_for('main.index'))

@main.route('/profile', methods=['GET'])
@login_required
def profile():
    """Dashboard-Seite, lädt Kontakte aus der Graph API."""
    client = GraphClient(session.get('email'))
    if not session.get('access_token'):
        logger.warning("No access token found, redirecting to login")
        return redirect(url_for('user.login'))
    try:
        contacts = client.get_contacts() # if false, empty app_mode
         
        app_mode = get_current_app_mode()
    except Exception as e:
        logger.error(f"Error: {e}") 
        return redirect(url_for('main.index'))
    return render_template(
        "profile.html",
        username=session.get('username'),
        email=session.get('email'),
        contacts=contacts,
        app_mode=app_mode
    ) 

# --- User Routes ---
@user.route('/login', methods=['GET', 'POST'])
def login():
    """Login first local, then oauth2. (Graph API)"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_login(email, password):
            session['email'] = email
            session['username'] = get_username(email)
            client = GraphClient(email)
            logger.info(f"Local login for '{email}' Ok, redirecting to {client.get_auth_redirect_url()}")
            redirect_url = client.get_auth_redirect_url()
            # redirect to Microsoft login
            return redirect(redirect_url)
        else:
            logger.warning(f"Local login for '{email}' failed, redirecting to login")
            flash("Login failed, wrong credentials", "danger")
            return redirect(url_for('user.login'))

    app_mode = get_current_app_mode()  
    logger.debug("Rendering login page")
    return render_template("login.html", app_mode=app_mode)

@user.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user locally."""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if check_register(username, email, password):
            logger.info(f"User '{email}' registered, redirecting to login")
            flash("Registration successful", "success")
            return redirect(url_for('main.index'))
        else:
            logger.warning(f"User '{email}' could not be registered, redirecting to register")
            flash("Registration failed, email already exists", "danger")
            return redirect(url_for('user.register'))

    app_mode = get_current_app_mode()  
    logger.debug("Rendering register page")
    return render_template("register.html", app_mode=app_mode)

@user.route('/logout', methods=['GET'])
def logout():
    """Benutzer abmelden."""
    flash("Logout successful", "success")
    logger.info(f"Logging out user '{session.get('email', 'Guest')}'")
    session.pop('email', None)
    session.pop('username', None)
    session.pop('access_token', None)
    session.pop('app_mode', None)

    client = GraphClient()
    client.reset()
    
    app_mode = get_current_app_mode()  
    return render_template("logout.html", app_mode=app_mode)

# --- unknown routes return to index ---
@main.route('/<path:path>', methods=['GET'])
def unknown_route(path):
    """Unbekannte Route -> Index."""
    flash(f"Unknown route '{path}', redirecting to index", "warning")
    app_mode = get_current_app_mode()  
    return redirect(url_for('main.index', app_mode=app_mode))

# get here from /login -> redirect
@user.route('/callback', methods=['GET'])
def callback():
    """Callback-Route nach erfolgreichem Microsoft-Login."""
    authorization_code = request.args.get('code')
    if authorization_code and 'email' in session:
        logger.info(f"Authorization code received, getting access token.")
        client = GraphClient(session.get('email'))
        access_token = client.get_access_token(authorization_code=authorization_code)
        # save access token in session
        session['access_token'] = access_token

        # still need to validate access token
        logger.debug(f"Access token for '{session.get('email')}' received, redirecting to profile")
        app_mode = get_current_app_mode()  
        return redirect(url_for('main.profile', app_mode=app_mode))
    app_mode = get_current_app_mode()  
    return redirect(url_for('user.login', app_mode=app_mode))