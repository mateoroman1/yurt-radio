"""
Main Flask application for Yurt Radio.

This is the entry point for the backend server.
Run this file to start the server: python app.py
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
from backend.routes import api_bp
from backend.models import init_db
from scripts.scan_music import rescan_music_directory
import config
import os


app = Flask(__name__, static_folder='static') 

app.config.from_object(config)

CORS(app)

# This will create the database file and tables if they don't exist
init_db()

# This connects all the API routes from backend/routes.py
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/', methods=['POST', 'GET'])
def index():
    """
    Serve the main frontend page.
    """
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """
    Serve static files (CSS, JS, images, etc.)
    """
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Only rescan in development mode
    if config.DEBUG:
        rescan_music_directory()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

