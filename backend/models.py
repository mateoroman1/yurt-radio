"""
Database models and queries for Yurt Radio.

This file handles all database operations using SQLite.
"""

import sqlite3
from contextlib import contextmanager
import config
import os

@contextmanager
def get_db():
    """
    Context manager for database connections.

    Usage:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tracks")
    """
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    try:
        yield conn

    finally:
        conn.commit()
        conn.close()


def init_db():
    """
    Initialize the database by creating tables if they don't exist.
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)

    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tracks (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       file_path TEXT NOT NULL,
                       file_hash TEXT UNIQUE NOT NULL,
                       title TEXT, 
                       author TEXT,
                       duration INTEGER,
                       file_size INTEGER,
                       play_count INTEGER DEFAULT 0,
                       last_played DATETIME)
                       ''')


def get_random_track(exclude_ids=None):
    """
    Get a random track from the database.

    Args:
        exclude_recent: If True, exclude recently played tracks

    Returns:
        A dictionary representing a track, or None if no tracks available
    """
    with get_db() as conn:
        cursor = conn.cursor()

        if exclude_ids:
            exclude_ids_str = ','.join(map(str, exclude_ids))
            query = f"SELECT * FROM tracks WHERE id NOT IN ({exclude_ids_str}) ORDER BY RANDOM() LIMIT 1;"
        else:
            query = "SELECT * FROM tracks ORDER BY RANDOM() LIMIT 1;"
            
        cursor.execute(query)
        random_track = cursor.fetchone()
        return random_track


def get_track_by_id(track_id):
    """
    Get a specific track by its ID.

    Args:
        track_id: The ID of the track to retrieve

    Returns:
        A dictionary representing the track, or None if not found
    """
    with get_db() as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM tracks WHERE id = ?;"

        cursor.execute(query, (track_id,))
        track = cursor.fetchone()
        return track


def get_all_tracks(page=1, limit=50):
    """
    Get all tracks with pagination.

    Args:
        page: Page number (1-indexed)
        limit: Number of tracks per page

    Returns:
        A dictionary with 'tracks', 'total', 'page', and 'pages' keys
    """
    offset = (page - 1) * limit

    with get_db() as conn:
        cursor = conn.cursor()

        query_total = "SELECT COUNT(*) FROM tracks;"
        query_page = "SELECT * FROM tracks LIMIT ? OFFSET ?"

        count = cursor.execute(query_total).fetchone()[0]

        result = cursor.execute(query_page, (limit, offset))

        tracks_data = []
        rows = result.fetchall()
        for row in rows:
            tracks_data.append(dict(row))

        tracks = {
            "tracks": tracks_data,
            "total": count,
            "page": page,
            "pages": (count + limit - 1) // limit
        }

        return tracks


def update_play_count(track_id):
    """
    Increment the play count and update last_played_at for a track.

    Args:
        track_id: The ID of the track to update
    """
    with get_db() as conn:
        cursor = conn.cursor()

        statement = "UPDATE tracks SET play_count = play_count + 1, last_played = CURRENT_TIMESTAMP WHERE id = ?;"

        cursor.execute(statement, (track_id,))


def get_stats():
    """
    Get statistics about the music collection.

    Returns:
        A dictionary with stats like total_tracks, total_duration, etc.
    """
    stats = {}

    with get_db() as conn:
        cursor = conn.cursor()

        query_total = "SELECT COUNT(*) FROM tracks;"
        query_duration = "SELECT SUM(duration) FROM tracks;"
        query_most_listened = "SELECT * FROM tracks WHERE play_count = (SELECT MAX(play_count) FROM tracks);"

        total = cursor.execute(query_total).fetchone()[0]
        duration = cursor.execute(query_duration).fetchone()[0]
        most_played = cursor.execute(query_most_listened).fetchone()

        stats['total_tracks'] = total
        stats['total_duration'] = duration
        stats['most_played'] = dict(most_played)

        return stats

def insert_track(file_path, file_hash, title, author, duration, file_size):
    """
    Insert a new track into the database.

    Args:
        file_path: Relative path to the music file
        file_hash: Computed file hash, used for syncing
        title, artist, album, genre: Metadata strings
        year: Release year (int or None)
        duration: Track duration in seconds
        file_size: File size in bytes

    Returns:
        The ID of the inserted track, or None if insert failed
    """
    with get_db() as conn:
        cursor = conn.cursor()

        statement = "INSERT INTO tracks (file_path, file_hash, title, author, duration, file_size) VALUES (?, ?, ?, ?, ?, ?)"

        cursor.execute(statement, (file_path, file_hash, title, author, duration, file_size))

        return cursor.lastrowid
    
def insert_or_update_track(file_path, file_hash, title, author, duration, file_size):
    """
    Upsert with file hash.

    Args:
        file_path: Relative path to the music file
        file_hash: Computed file hash, used for syncing
        title, artist, album, genre: Metadata strings
        year: Release year (int or None)
        duration: Track duration in seconds
        file_size: File size in bytes

    Returns:
        The ID of the inserted track, or None if insert failed

    """
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tracks (file_path, file_hash, title, author, duration, file_size)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(file_hash) DO UPDATE SET
                file_path = excluded.file_path,
                title = excluded.title,
                author = excluded.author,
                duration = excluded.duration,
                file_size = excluded.file_size
        """, (file_path, file_hash, title, author, duration, file_size))

        return cursor.lastrowid

def del_by_unseen_hash(seen_hashes):
    """
    Removes hashes not present in seen_hashes

    Args:
        seen_hashes: set of hashes from the music dir

    Returns:
        number of affected rows.
    """
    with get_db() as conn:
        cursor = conn.cursor()

        db_hashes = {r['file_hash'] for r in cursor.execute("SELECT file_hash FROM tracks")}
        to_remove = db_hashes - seen_hashes

        if to_remove:
            cursor.executemany("DELETE FROM tracks WHERE file_hash = ?", [(h,) for h in to_remove])
            return cursor.rowcount
        return 0
