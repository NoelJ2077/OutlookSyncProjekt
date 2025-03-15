from flask import Flask
from .config import Config, DB_Config
import logging
import os

logger = logging.getLogger(__name__)
logger_initialized = False

def create_app():
    global logger_initialized

    app = Flask(__name__)
    app.config.from_object(Config)  # get Graph values
    app.secret_key = Config.SECRET_KEY  # Flask Session Key
    log_path = Config.LOG_PATH  # Log file path
    DB_Config.create_tables() # Create DB with tables
    
    timeformat = '%H:%M:%S %d.%m.%Y'

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

    logger.debug("App created 'debug'")  # Log-Debug
    logger.info("App started 'info'")  # Log-Info

    # Change werkzeug log level
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)

    from .routes import main, user
    app.register_blueprint(main)
    app.register_blueprint(user)

    return app