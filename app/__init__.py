from flask import Flask
from .config import Config, DB_Config
import logging
import os

# Globaler Logger (wird nur einmal initialisiert)
logger = logging.getLogger(__name__)
logger_initialized = False

def create_app():
    global logger_initialized

    app = Flask(__name__)  # Flask App erstellen
    app.config.from_object(Config)  # Konfiguration laden (Graph credentials)
    app.secret_key = Config.SECRET_KEY  # Secret Key für die Session
    log_path = Config.LOG_PATH  # Log-Datei Pfad
    DB_Config.create_tables()  # Datenbank-Tabellen erstellen falls neu
    
    timeformat = '%H:%M:%S %d.%m.%Y'

    # Logger nur einmal konfigurieren
    if not logger_initialized:
        logger.setLevel(logging.DEBUG)

        # File log
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt=timeformat))

        # Console log
        console_handler = logging.StreamHandler()  # Konsole
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s', datefmt=timeformat))

        # Bestehende Handler entfernen und neue hinzufügen
        logger.handlers.clear()  # Nur ein Satz von Handlern
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger_initialized = True  # Markiere Logger als initialisiert

    logger.debug("App created 'debug'")  # Log-Debug
    logger.info("App started 'info'")  # Log-Info

    # Werkzeug-Logger anpassen (optional, um dessen Spam zu reduzieren)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)

    from .routes import main, user  # Importieren der Routen
    app.register_blueprint(main)
    app.register_blueprint(user)

    return app