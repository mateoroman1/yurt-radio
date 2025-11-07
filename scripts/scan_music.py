"""
Music Scanner Script for Yurt Radio.

This script scans the music directory and populates the database
with track metadata.

Usage: python scripts/scan_music.py
"""

import os
import sys
import hashlib

# Add parent directory to path so we can import from backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import insert_track, insert_or_update_track, init_db, del_by_unseen_hash
from backend.utils import extract_metadata, is_supported_format
import config

def hash_file(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def scan_music_directory():
    """
    Scan the music directory and populate the database.

    This function:
    1. Walks through the music directory recursively
    2. Finds all supported audio files
    3. Extracts metadata from each file
    4. Inserts the track into the database
    """

    init_db()
    print(f"Scanning music directory: {config.MUSIC_DIRECTORY}")
    print(f"Supported formats: {', '.join(config.SUPPORTED_FORMATS)}")
    print("-" * 50)

    total_scanned = 0
    total_added = 0

    files = os.listdir(config.MUSIC_DIRECTORY)
    for filename in files:
        total_scanned += 1
        if os.path.splitext(filename)[1] in config.SUPPORTED_FORMATS:
            metadata = extract_metadata(f"{config.MUSIC_DIRECTORY}/{filename}")
            filehash = hash_file(f"{config.MUSIC_DIRECTORY}/{filename}")
            insert_track(filename, filehash, metadata['title'], metadata['author'], metadata['duration'], metadata['file_size'])
            total_added += 1

    print("-" * 50)
    print("Scan complete!")
    print(f"Files scanned: {total_scanned}")
    print(f"Tracks added to database: {total_added}")


def rescan_music_directory():
    """
    Rescan the music directory and update the database.

    This is similar to scan_music_directory() but can be used to
    update metadata for existing tracks or add new ones.
    """
    print(f"Scanning music directory: {config.MUSIC_DIRECTORY}")
    print(f"Supported formats: {', '.join(config.SUPPORTED_FORMATS)}")
    print("-" * 50)

    total_scanned = 0
    total_added = 0

    seen_hashes = set()

    files = os.listdir(config.MUSIC_DIRECTORY)
    for filename in files:
        total_scanned += 1
        if os.path.splitext(filename)[1] in config.SUPPORTED_FORMATS:
            metadata = extract_metadata(f"{config.MUSIC_DIRECTORY}/{filename}")
            filehash = hash_file(f"{config.MUSIC_DIRECTORY}/{filename}")
            seen_hashes.add(filehash)
            insert_or_update_track(filename, filehash, metadata['title'], metadata['author'], metadata['duration'], metadata['file_size'])
            total_added += 1

    total_removed = del_by_unseen_hash(seen_hashes)

    print("-" * 50)
    print("Scan complete!")
    print(f"Files scanned: {total_scanned}")
    print(f"Tracks added to database: {total_added}")
    print(f"Tracks removed: {total_removed}")


if __name__ == '__main__':
    """
    Main entry point for the script.

    TODO: Add command line argument parsing (optional)
    For now, just call scan_music_directory()
    """
    # Check if music directory exists
    if not os.path.exists(config.MUSIC_DIRECTORY):
        print(f"Error: Music directory not found: {config.MUSIC_DIRECTORY}")
        print("Please create the directory and add some music files.")
        sys.exit(1)

    rescan_music_directory()
