"""
Configuration file for Yurt Radio backend.

TODO: Set up your configuration values below.
You can use environment variables or hardcode values for now.
"""

import os

# Example: MUSIC_DIRECTORY = 'E:\\yurt-radio\\music'
MUSIC_DIRECTORY = os.getenv('MUSIC_DIR', './music')

# This will be created automatically when you run the app
DATABASE_PATH = os.getenv('DB_PATH', './data/yurt_radio.db')

# Add or remove formats as needed
SUPPORTED_FORMATS = ['.mp3', '.flac', '.ogg', '.m4a', '.wav']

# Higher number = less repetition, but requires more memory
MAX_RECENT_TRACKS = 10

# Flask configuration
DEBUG = True
HOST = '127.0.0.1'
PORT = 5000
