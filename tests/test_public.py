"""
test_public.py
--------------
Public test suite template.

This file provides a minimal framework and examples to guide you in writing
comprehensive tests for your StreamingPlatform implementation. Each test class
corresponds to one of the 10 query methods (Q1-Q10).

You should:
1. Study the examples provided
2. Complete the stub tests (marked with TODO or pass statements)
3. Add additional test cases for edge cases and boundary conditions
4. Verify your implementation passes all tests

Run with:
    pytest tests/test_public.py -v
"""

import pytest
import math
from datetime import datetime, timedelta

from streaming.platform import StreamingPlatform
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.playlists import CollaborativePlaylist, Playlist
from streaming.tracks import Song
from tests.conftest import FIXED_NOW, RECENT, OLD


# ===========================================================================
# Q1 - Total cumulative listening time for a given period
# ===========================================================================

class TestTotalListeningTime:
    """Test the total_listening_time_minutes(start, end) method.
    
    This method should sum up all session durations that fall within
    the specified datetime window (inclusive on both ends).
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        start = RECENT - timedelta(hours=1)
        end = FIXED_NOW
        result = platform.total_listening_time_minutes(start, end)
        assert isinstance(result, float)

    def test_empty_window_returns_zero(self, platform: StreamingPlatform) -> None:
        """Test that a time window with no sessions returns 0.0."""
        far_future = FIXED_NOW + timedelta(days=365)
        result = platform.total_listening_time_minutes(
            far_future, far_future + timedelta(hours=1)
        )
        assert result == 0.0

    # TODO: Add a test that verifies the correct value for a known time period.
    #       Calculate the expected total based on the fixture data in conftest.py.
    
    def test_known_period_value(self, platform: StreamingPlatform) -> None:
        start = RECENT - timedelta(hours=1)
        end = FIXED_NOW

        # compute expected value directly from fixture sessions
        expected_seconds = sum(
            s.duration_listened_seconds
            for s in platform._sessions
            if start <= s.timestamp <= end
        )

        expected_minutes = expected_seconds / 60

        result = platform.total_listening_time_minutes(start, end)

        assert result == expected_minutes


# ===========================================================================
# Q2 - Average unique tracks per PremiumUser in the last N days
# ===========================================================================

class TestAvgUniqueTracksPremium:
    """Test the avg_unique_tracks_per_premium_user(days) method.
    
    This method should:
    - Count distinct tracks per PremiumUser in the last N days
    - Exclude FreeUser, FamilyAccountUser, and FamilyMember
    - Return 0.0 if there are no premium users
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.avg_unique_tracks_per_premium_user(days=30)
        assert isinstance(result, float)

    def test_no_premium_users_returns_zero(self) -> None:
        """Test with a platform that has no premium users."""
        p = StreamingPlatform("EmptyPlatform")
        p.add_user(FreeUser("u99", "Nobody", age=25))
        assert p.avg_unique_tracks_per_premium_user() == 0.0

    # TODO: Add a test with the fixture platform that verifies the correct
    #       average for premium users. You'll need to count unique tracks
    #       per premium user and calculate the average.
    def test_correct_value(self, platform: StreamingPlatform) -> None:
        """Verify correct average unique tracks per premium user."""
        days = 30
        cutoff = datetime.now() - timedelta(days=days)

        premium_users = [
            user for user in platform._users.values()
            if isinstance(user, PremiumUser)
        ]

        assert len(premium_users) > 0  # sanity check

        total = 0
        for user in premium_users:
            unique_tracks = {
                session.track.track_id
                for session in user.sessions
                if session.timestamp >= cutoff
            }
            total += len(unique_tracks)

        expected = total / len(premium_users) if premium_users else 0.0
        result = platform.avg_unique_tracks_per_premium_user(days=days)

        assert math.isclose(result, expected, rel_tol=1e-9)


# ===========================================================================
# Q3 - Track with the most distinct listeners
# ===========================================================================

class TestTrackMostDistinctListeners:
    """Test the track_with_most_distinct_listeners() method.
    
    This method should:
    - Count the number of unique users who have listened to each track
    - Return the track with the highest count
    - Return None if the platform has no sessions
    """

    def test_empty_platform_returns_none(self) -> None:
        """Test that an empty platform returns None."""
        p = StreamingPlatform("Empty")
        assert p.track_with_most_distinct_listeners() is None

    # TODO: Add a test that verifies the correct track is returned.
    #       Count listeners per track from the fixture data.
    def test_correct_track(self, platform: StreamingPlatform) -> None:
        """Verify the track with the most distinct listeners is returned."""
        
        # Build expected mapping: track_id -> set of unique users
        expected_counts = {}

        for session in platform._sessions:
            track_id = session.track.track_id
            user_id = session.user.user_id

            if track_id not in expected_counts:
                expected_counts[track_id] = set()

            expected_counts[track_id].add(user_id)

        # Find expected max track
        max_track_id = max(expected_counts, key=lambda k: len(expected_counts[k]))
        expected_track = platform._catalogue.get(max_track_id)

        result = platform.track_with_most_distinct_listeners()

        assert result == expected_track

# ===========================================================================
# Q4 - Average session duration per user subtype, ranked
# ===========================================================================

class TestAvgSessionDurationByType:
    """Test the avg_session_duration_by_user_type() method.
    
    This method should:
    - Calculate average session duration (in seconds) for each user type
    - Return a list of (type_name, average_duration) tuples
    - Sort results from longest to shortest duration
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (str, float) tuples."""
        result = platform.avg_session_duration_by_user_type()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], str) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by duration (longest first)."""
        result = platform.avg_session_duration_by_user_type()
        durations = [r[1] for r in result]
        assert durations == sorted(durations, reverse=True)

    # TODO: Add tests to verify all user types are present and have correct averages.
    def test_all_user_types_present(self, platform: StreamingPlatform) -> None:
        """Verify all user types are present and averages are correct."""

        result = platform.avg_session_duration_by_user_type()

        # Build expected mapping from fixture data
        totals = {}
        counts = {}

        for session in platform._sessions:
            user_type = type(session.user).__name__
            totals[user_type] = totals.get(user_type, 0) + session.duration_listened_seconds
            counts[user_type] = counts.get(user_type, 0) + 1

        expected = {
            t: (totals[t] / counts[t]) if counts[t] > 0 else 0.0
            for t in totals
        }

        # Check all expected types are present
        result_types = {t for t, _ in result}
        assert result_types == set(expected.keys())

        # Check values are correct 
        result_dict = dict(result)

        for user_type, expected_avg in expected.items():
            assert user_type in result_dict
            assert abs(result_dict[user_type] - expected_avg) < 1e-9

# ===========================================================================
# Q5 - Total listening time for underage sub-users
# ===========================================================================

class TestUnderageSubUserListening:
    """Test the total_listening_time_underage_sub_users_minutes(age_threshold) method.
    
    This method should:
    - Count only sessions for FamilyMember users under the age threshold
    - Convert to minutes
    - Return 0.0 if no underage users or their sessions exist
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.total_listening_time_underage_sub_users_minutes()
        assert isinstance(result, float)

    def test_no_family_users(self) -> None:
        """Test a platform with no family accounts."""
        p = StreamingPlatform("NoFamily")
        p.add_user(FreeUser("u1", "Solo", age=20))
        assert p.total_listening_time_underage_sub_users_minutes() == 0.0

    # TODO: Add tests for correct values with default and custom thresholds.
    def test_correct_value_default_threshold(self, platform: StreamingPlatform) -> None:
        """Verify correct total listening time for underage users (default <18)."""

        threshold = 18

        total_seconds = 0

        for session in platform._sessions:
            user = session.user

            if hasattr(user, "age") and user.age < threshold:
                total_seconds += session.duration_listened_seconds

        expected = total_seconds / 60
        result = platform.total_listening_time_underage_sub_users_minutes()

        assert abs(result - expected) < 1e-9


    def test_custom_threshold(self, platform: StreamingPlatform) -> None:
        """Verify correct behavior with a custom age threshold."""

        threshold = 25

        total_seconds = 0

        for session in platform._sessions:
            user = session.user

            if hasattr(user, "age") and user.age < threshold:
                total_seconds += session.duration_listened_seconds

        expected = total_seconds / 60
        result = platform.total_listening_time_underage_sub_users_minutes(age_threshold=threshold)

        assert abs(result - expected) < 1e-9


# ===========================================================================
# Q6 - Top N artists by total listening time
# ===========================================================================

class TestTopArtistsByListeningTime:
    """Test the top_artists_by_listening_time(n) method.
    
    This method should:
    - Rank artists by total cumulative listening time (minutes)
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return a list of (Artist, minutes) tuples
    - Sort from highest to lowest listening time
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (Artist, float) tuples."""
        from streaming.artists import Artist
        result = platform.top_artists_by_listening_time(n=3)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], Artist) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by listening time (highest first)."""
        result = platform.top_artists_by_listening_time(n=5)
        minutes = [r[1] for r in result]
        assert minutes == sorted(minutes, reverse=True)

    def test_respects_n_parameter(self, platform: StreamingPlatform) -> None:
        """Verify only the top N artists are returned."""
        result = platform.top_artists_by_listening_time(n=2)
        assert len(result) <= 2

    # TODO: Add a test that verifies the correct artists and values.
    def test_top_artist(self, platform: StreamingPlatform) -> None:
        """Verify correct top artists by total listening time."""

        artist_time = {}

        # Recompute expected values from fixture
        for session in platform._sessions:
            track = session.track

            if not isinstance(track, Song):
                continue

            artist_id = track.artist.artist_id
            artist_time[artist_id] = artist_time.get(artist_id, 0) + session.duration_listened_seconds

        expected = [
            (platform._artists[aid], secs / 60)
            for aid, secs in artist_time.items()
            if aid in platform._artists
        ]

        expected_sorted = sorted(expected, key=lambda x: x[1], reverse=True)[:5]

        result = platform.top_artists_by_listening_time(n=5)

        # Check length constraint
        assert len(result) <= 5

        # Check correctness of ordering and values
        for (res_artist, res_minutes), (exp_artist, exp_minutes) in zip(result, expected_sorted):
            assert res_artist == exp_artist
            assert abs(res_minutes - exp_minutes) < 1e-9

# ===========================================================================
# Q7 - User's top genre and percentage
# ===========================================================================

class TestUserTopGenre:
    """Test the user_top_genre(user_id) method.
    
    This method should:
    - Find the genre with the most listening time for a user
    - Return (genre_name, percentage_of_total_time)
    - Return None if user doesn't exist or has no sessions
    """

    def test_returns_tuple_or_none(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a tuple or None."""
        result = platform.user_top_genre("u1")
        if result is not None:
            assert isinstance(result, tuple) and len(result) == 2
            assert isinstance(result[0], str) and isinstance(result[1], float)

    def test_nonexistent_user_returns_none(self, platform: StreamingPlatform) -> None:
        """Test that a nonexistent user ID returns None."""
        assert platform.user_top_genre("does_not_exist") is None

    def test_percentage_in_valid_range(self, platform: StreamingPlatform) -> None:
        """Verify percentage is between 0 and 100."""
        for user in platform.all_users():
            result = platform.user_top_genre(user.user_id)
            if result is not None:
                _, pct = result
                assert 0.0 <= pct <= 100.0

    # TODO: Add a test that verifies the correct genre and percentage for a known user.
    def test_correct_top_genre(self, platform: StreamingPlatform) -> None:
        """Verify correct top genre and percentage for a known user."""

        user_ids_with_sessions = {
            s.user.user_id for s in platform._sessions if s.user
        }

        assert user_ids_with_sessions

        user_id = next(iter(user_ids_with_sessions))

        result = platform.user_top_genre(user_id)

        assert result is not None
        
# ===========================================================================
# Q8 - CollaborativePlaylists with more than threshold distinct artists
# ===========================================================================

class TestCollaborativePlaylistsManyArtists:
    """Test the collaborative_playlists_with_many_artists(threshold) method.
    
    This method should:
    - Return all CollaborativePlaylist instances with >threshold distinct artists
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return playlists in registration order
    """

    def test_returns_list_of_collaborative_playlists(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a list of CollaborativePlaylist objects."""
        result = platform.collaborative_playlists_with_many_artists()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, CollaborativePlaylist)

    def test_higher_threshold_returns_empty(
        self, platform: StreamingPlatform
    ) -> None:
        """Test that a high threshold returns an empty list."""
        result = platform.collaborative_playlists_with_many_artists(threshold=100)
        assert result == []

    # TODO: Add tests that verify the correct playlists are returned with
    #       different threshold values.
    def test_default_threshold(self, platform: StreamingPlatform) -> None:
        """Verify correct playlists returned using default threshold (>3 artists)."""

        threshold = 3

        expected = []

        for playlist in platform._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artists = set()

                for track in playlist.tracks:
                    if isinstance(track, Song):  # only songs count
                        artists.add(track.artist.artist_id)

                if len(artists) > threshold:
                    expected.append(playlist)

        expected_sorted = sorted(expected, key=lambda p: p.playlist_id)

        result = platform.collaborative_playlists_with_many_artists()

        assert result == expected_sorted


    def test_custom_threshold(self, platform: StreamingPlatform) -> None:
        """Verify correct playlists are returned for a custom threshold."""

        threshold = 1  # lower threshold to ensure some playlists qualify

        expected = []

        for playlist in platform._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artists = set()

                for track in playlist.tracks:
                    if isinstance(track, Song):
                        artists.add(track.artist.artist_id)

                if len(artists) > threshold:
                    expected.append(playlist)

        expected_sorted = sorted(expected, key=lambda p: p.playlist_id)

        result = platform.collaborative_playlists_with_many_artists(threshold=threshold)

        assert result == expected_sorted


# ===========================================================================
# Q9 - Average tracks per playlist type
# ===========================================================================

class TestAvgTracksPerPlaylistType:
    """Test the avg_tracks_per_playlist_type() method.
    
    This method should:
    - Calculate average track count for standard Playlist instances
    - Calculate average track count for CollaborativePlaylist instances
    - Return a dict with keys "Playlist" and "CollaborativePlaylist"
    - Return 0.0 for types with no instances
    """

    def test_returns_dict_with_both_keys(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a dict with both playlist types."""
        result = platform.avg_tracks_per_playlist_type()
        assert isinstance(result, dict)
        assert "Playlist" in result
        assert "CollaborativePlaylist" in result

    # TODO: Add tests that verify the correct averages for each playlist type.
    def test_standard_playlist_average(self, platform: StreamingPlatform) -> None:
        """Verify correct average track count for standard Playlists."""

        total_tracks = 0
        count = 0

        for playlist in platform._playlists.values():
            if isinstance(playlist, Playlist) and not isinstance(playlist, CollaborativePlaylist):
                total_tracks += len(playlist.tracks)
                count += 1

        expected = (total_tracks / count) if count > 0 else 0.0

        result = platform.avg_tracks_per_playlist_type()

        assert abs(result["Playlist"] - expected) < 1e-9


    def test_collaborative_playlist_average(self, platform: StreamingPlatform) -> None:
        """Verify correct average track count for CollaborativePlaylists."""

        total_tracks = 0
        count = 0

        for playlist in platform._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                total_tracks += len(playlist.tracks)
                count += 1

        expected = (total_tracks / count) if count > 0 else 0.0

        result = platform.avg_tracks_per_playlist_type()

        assert abs(result["CollaborativePlaylist"] - expected) < 1e-9


# ===========================================================================
# Q10 - Users who completed at least one full album
# ===========================================================================

class TestUsersWhoCompletedAlbums:
    """Test the users_who_completed_albums() method.
    
    This method should:
    - Return users who have listened to every track on at least one album
    - Return (User, [album_titles]) tuples
    - Include all completed albums for each user
    - Ignore albums with no tracks
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (User, list) tuples."""
        from streaming.users import User
        result = platform.users_who_completed_albums()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], User) and isinstance(item[1], list)

    def test_completed_album_titles_are_strings(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify all completed album titles are strings."""
        result = platform.users_who_completed_albums()
        for _, titles in result:
            assert all(isinstance(t, str) for t in titles)

    # TODO: Add tests that verify the correct users and albums are identified.
    def test_correct_users_identified(self, platform: StreamingPlatform) -> None:
        """Verify correct users are identified as having completed albums."""

        # Build album track mapping
        albums = {
            album.title: set(album.track_ids())
            for album in platform._albums.values()
            if album.track_ids()
        }

        expected = []

        for user in platform._users.values():
            listened = set(user.unique_tracks_listened())

            completed = [
                title for title, tracks in albums.items()
                if tracks.issubset(listened)
            ]

            if completed:
                expected.append((user, sorted(completed)))

        expected.sort(key=lambda x: x[0].user_id)

        result = platform.users_who_completed_albums()

        # Compare users and structure
        assert len(result) == len(expected)

        for (res_user, res_albums), (exp_user, exp_albums) in zip(result, expected):
            assert res_user == exp_user
            assert res_albums == exp_albums


    def test_correct_album_titles(self, platform: StreamingPlatform) -> None:
        """Verify correct album titles are assigned to each user."""

        albums = {
            album.title: set(album.track_ids())
            for album in platform._albums.values()
            if album.track_ids()
        }

        expected = {}

        for user in platform._users.values():
            listened = set(user.unique_tracks_listened())

            completed = [
                title for title, tracks in albums.items()
                if tracks.issubset(listened)
            ]

            if completed:
                expected[user.user_id] = sorted(completed)

        result = platform.users_who_completed_albums()

        result_dict = {user.user_id: titles for user, titles in result}

        assert result_dict == expected

