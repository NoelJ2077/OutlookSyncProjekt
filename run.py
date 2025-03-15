# run.py: Startpunkt der Anwendung
from app import create_app
from app.client import GraphClient
import logging
from flask import Flask, redirect, session, request, jsonify

# Flask-Anwendung erstellen
app = create_app()


if __name__ == '__main__':

    # Produktion (Flask-Server starten)
    app.run(host='0.0.0.0', port=5000, debug=True)
