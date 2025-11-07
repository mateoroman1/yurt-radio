"""
Utility functions for Yurt Radio.

Helper functions for metadata extraction, file validation, etc.
"""

from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from mutagen.mp4 import MP4
import os
import config


def extract_metadata(file_path):
    """
    Extract metadata from an audio file using mutagen.

    Args:
        file_path: Full path to the audio file

    Returns:
        Dictionary with metadata:
    """
    metadata = {
        'title': None,
        'author': None,
        'duration': 0,
        'file_size': 0
    }

    if file_path.lower().endswith('.mp3'):
        audio = MP3(file_path)
        

    elif file_path.lower().endswith('.wav'):
        audio = WAVE(file_path)

    
    elif file_path.lower().endswith('.m4a'):
        audio = MP4(file_path)
    
    metadata['title'] = os.path.basename(file_path).split('.')[0]
    metadata['author'] = "Unknown"
    metadata['duration'] = int(audio.info.length)
    metadata['file_size'] = os.path.getsize(file_path)

    return metadata


def is_supported_format(file_path):
    """
    Check if a file is a supported audio format.

    Args:
        file_path: Path to the file

    Returns:
        Boolean: True if supported, False otherwise

    TODO: Implement this function
    Hints:
    - Get the file extension: os.path.splitext(file_path)[1].lower()
    - Check if extension is in config.SUPPORTED_FORMATS
    """
    # YOUR CODE HERE
    pass


def get_mimetype(file_path):
    """
    Get the MIME type for an audio file.

    Args:
        file_path: Path to the file

    Returns:
        String: MIME type (e.g., 'audio/mpeg' for mp3)
    """
    mimetype_map = {
        '.mp3': 'audio/mpeg',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg',
        '.m4a': 'audio/mp4',
        '.wav': 'audio/wav'
    }

    extension = os.path.splitext(file_path)[1]

    if extension in config.SUPPORTED_FORMATS:
        return mimetype_map[extension]

    return 'audio/mpeg'  # default


def format_duration(seconds):
    """
    Format duration in seconds to MM:SS or HH:MM:SS format.

    Args:
        seconds: Duration in seconds

    Returns:
        String: Formatted duration

    Examples:
        format_duration(65) -> "1:05"
        format_duration(3665) -> "1:01:05"

    TODO: Implement this function
    Hints:
    - Calculate hours: seconds // 3600
    - Calculate minutes: (seconds % 3600) // 60
    - Calculate remaining seconds: seconds % 60
    - Use string formatting: f"{minutes}:{seconds:02d}"
    - Only include hours if > 0
    """
    # YOUR CODE HERE
    pass
