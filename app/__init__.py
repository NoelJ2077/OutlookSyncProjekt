# app/__init__.py
from flask import Flask
from .config import ConfigVars, DB_Models
from .client import GraphClient
import logging, os

logger = logging.getLogger(__name__)
logger_initialized = False
client = GraphClient() # one and only instance of GraphClient

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

        logger_initialized = True # Logger is initialized

        # Change werkzeug log level
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.WARNING)

    logger.info("App started")

    # if client initialized, true
    if not client:
        logger.debug("Error: GraphClient not initialized")
        return False
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