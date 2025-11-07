"""
Business logic for Yurt Radio.

This file contains the core logic for track selection, randomization, etc.
"""

from backend.models import get_random_track, update_play_count
import config


class TrackService:
    """
    Service class for track-related business logic.
    """

    # Class variable to store recently played track IDs
    # This prevents the same song from playing twice in a row
    recently_played = []

    @staticmethod
    def get_next_track():
        """
        Get the next random track with smart randomization.

        This function:
        1. Gets a random track from the database
        2. Ensures it's not a recently played track
        3. Updates the play count
        4. Adds it to the recently played list

        Returns:
            A track dictionary, or None if no tracks available
        """
        track = get_random_track(TrackService.get_recently_played())

        update_play_count(track['id'])

        TrackService.recently_played.append(track['id'])

        if len(TrackService.get_recently_played()) > config.MAX_RECENT_TRACKS:
            TrackService.recently_played.pop(0)

        return track

    @staticmethod
    def clear_recent_tracks():
        """
        Clear the recently played tracks list.

        This is useful for testing or if you want to reset the anti-repeat logic.
        """
        TrackService.recently_played.clear()

    @staticmethod
    def get_recently_played():
        """
        Get the list of recently played track IDs.

        Returns:
            List of track IDs
        """
        return TrackService.recently_played
