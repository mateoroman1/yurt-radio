"""
API routes for Yurt Radio.

This file defines all the HTTP endpoints for the backend API.
"""

from flask import Blueprint, jsonify, send_file, request
from backend.services import TrackService
from backend.models import get_track_by_id, get_all_tracks, get_stats
from backend.utils import get_mimetype
import config
import os

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)


@api_bp.route('/track/random', methods=['GET'])
def random_track():
    """
    Get a random track.

    Returns:
        JSON: Track metadata including stream URL

    Example response:
        {
            "id": 42,
            "title": "Song Title",
            "author": "Artist Name",
            "duration": 245,
            "stream_url": "/api/stream/42",
            ...
        }
    """
    track = TrackService.get_next_track()
    if track:
        return jsonify({
            "id": track['id'],
            "title": track['title'],
            "author": track['author'],
            "duration": track['duration'],
            "file_path": track['file_path'],
            "stream_url": f"/api/stream/{track['id']}"
        })
    else:
        return {"error": "Not found"}, 404


@api_bp.route('/stream/<int:track_id>', methods=['GET'])
def stream_track(track_id):
    """
    Stream an audio file.

    Args:
        track_id: The ID of the track to stream

    Returns:
        Audio file with proper headers for streaming
    """
    track = get_track_by_id(track_id)
    if track:
        track_path = os.path.join(config.MUSIC_DIRECTORY, track['file_path'])
        if os.path.exists(track_path):
            return send_file(track_path, mimetype=get_mimetype(track_path), conditional=True)
        else:
            return {"error": "Track Not Found"}, 404
    else:
        return {"error": "Track ID Invalid"}, 404


@api_bp.route('/tracks', methods=['GET'])
def list_tracks():
    """
    List all tracks with pagination.

    Query parameters:
        page: Page number (default: 1)
        limit: Tracks per page (default: 50)

    Returns:
        JSON: Paginated list of tracks

    Example response:
        {
            "tracks": [...],
            "total": 150,
            "page": 1,
            "pages": 3
        }
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)

    tracks = get_all_tracks(page, limit)
    return jsonify(tracks)


@api_bp.route('/track/<int:track_id>', methods=['GET'])
def get_track(track_id):
    """
    Get a specific track by ID.

    Args:
        track_id: The ID of the track

    Returns:
        JSON: Track metadata
    """
    track = get_track_by_id(track_id)
    if track:
            return jsonify(track)
    else:
        return {"error": "Track ID Not Found"}, 404


@api_bp.route('/stats', methods=['GET'])
def get_collection_stats():
    """
    Get statistics about the music collection.

    Returns:
        JSON: Collection statistics
    """
    return jsonify(get_stats())


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON: {"status": "ok"}
    """
    return jsonify({"status": "ok"})

@api_bp.route('/', methods=['GET', 'POST'])
def root():
    """
    Base Endpoint.

    Returns:
        JSON: {"message": "Yurt Radio API", "health": "/api/health"}
    """
    return {"message": "Yurt Radio API", "health": "/api/health"}