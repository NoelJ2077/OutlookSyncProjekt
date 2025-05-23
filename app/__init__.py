# app/__init__.py
from flask import Flask
from .config import ConfigVars, DB_Models
import logging, os, socket

logger = logging.getLogger(__name__)
logger_initialized = False
# client = GraphClient() # global client instance (leads to problems when logging in with different accounts)

def create_app():
    """ Create Flask App including Database and Logger. """
    global logger_initialized
    timeformat = '%H:%M:%S %d.%m.%Y' # 15:45:10 20.03.2025

    app = Flask(__name__)
    log_path = ConfigVars.LOG_PATH # log file path

    if not logger_initialized:
        logger.setLevel(logging.DEBUG)

        # File log
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt=timeformat))

        # Console log
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt=timeformat))

        # Clear all handlers
        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # get local host IPv4 address
        host_ipv4 = socket.gethostbyname(socket.gethostname())
        logger.info(f"Local host IPv4 address: {host_ipv4}")

        logger_initialized = True # Logger is initialized

        # Change werkzeug log level
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)
    
    app.config.from_object(ConfigVars)
    app.secret_key = ConfigVars.SECRET_KEY
    logger.debug("Client, ConfigVars and Secret Key set / initialized")
    
    # conditional:
    if not os.path.exists(DB_Models.DB_PATH):
        DB_Models.init_db()
        logger.debug("Database initialized")
    else:
        logger.debug("Found existing database")

    from .routes import main, user
    app.register_blueprint(main)
    app.register_blueprint(user)

    return app
