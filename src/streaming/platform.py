"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""

from datetime import datetime, timedelta
from .users import PremiumUser
from .users import FamilyMember
from .tracks import Song
from .playlists import Playlist, CollaborativePlaylist
from .tracks import Song



class StreamingPlatform:
    def __init__(self, name):
        self.name = name
        self._catalogue = {}
        self._users = {}
        self._artists = {}
        self._albums = {}
        self._playlists = {}
        self._sessions = []

    def add_track(self, track):
        self._catalogue[track.track_id] = track

    def add_user(self, user):
        self._users[user.user_id] = user

    def add_artist(self, artist):
        self._artists[artist.artist_id] = artist

    def add_album(self, album):
        self._albums[album.album_id] = album

    def add_playlist(self, playlist):
        self._playlists[playlist.playlist_id] = playlist

    def record_session(self, session):
        self._sessions.append(session)

        if session.user:
            session.user.sessions.append(session)

    def get_track(self, track_id):
        return self._catalogue.get(track_id)

    def get_user(self, user_id):
        return self._users.get(user_id)

    def get_artist(self, artist_id):
        return self._artists.get(artist_id)

    def get_album(self, album_id):
        return self._albums.get(album_id)

    def all_users(self):
        return list(self._users.values())

    def all_tracks(self):
        return list(self._catalogue.values())
    
    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        if start > end:
            raise ValueError("start must be <= end")

        total_seconds = sum(
            session.duration_listened_seconds
            for session in self._sessions
            if start <= session.timestamp <= end
        )

        return total_seconds / 60
    
    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        premium_users = [
            user for user in self._users.values()
            if isinstance(user, PremiumUser)
        ]

        if not premium_users:
            return 0.0

        cutoff = datetime.now() - timedelta(days=days)

        total = 0
        count = 0

        for user in premium_users:
            unique_tracks = {
                s.track.track_id
                for s in user.sessions
                if s.timestamp >= cutoff
            }
            total += len(unique_tracks)
            count += 1 #always inlucde premium user

        return total / count if count > 0 else 0.0
    
    def track_with_most_distinct_listeners(self):
        if not self._sessions:
            return None

        track_listeners = {}

        for session in self._sessions:
            track = getattr(session, "track", None)
            user = getattr(session, "user", None)

            if not track or not user:
                continue

            track_id = getattr(track, "track_id", None)
            user_id = getattr(user, "user_id", None)

            if track_id is None or user_id is None:
                continue

            track_listeners.setdefault(track_id, set()).add(user_id)

        if not track_listeners:
            return None
        
        max_track_id = max(
            track_listeners, 
            key=lambda k: len(track_listeners[k])
        )

        return self._catalogue.get(max_track_id)
    
    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        if not self._sessions:
            return []

        all_types = {type(u).__name__ for u in self._users.values()}

        type_totals = {t: 0 for t in all_types}
        type_counts = {t: 0 for t in all_types}

        for session in self._sessions:
            t = type(session.user).__name__
            type_totals[t] += session.duration_listened_seconds
            type_counts[t] += 1

        return sorted(
            [
                (t, type_totals[t] / type_counts[t] if type_counts[t] > 0 else 0.0)
                for t in all_types
            ],
            key=lambda x: x[1],
            reverse=True
        )
    
    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        total_seconds = 0

        for session in self._sessions:
            user = session.user

            if hasattr(user, "age") and user.age < age_threshold:
                total_seconds += session.duration_listened_seconds

        return total_seconds / 60
    
    def top_artists_by_listening_time(self, n: int = 5):
        artist_time = {}

        for session in self._sessions:
            track = session.track

            if not isinstance(track, Song):
                continue

            artist_id = track.artist.artist_id
            artist_time[artist_id] = artist_time.get(artist_id, 0) + session.duration_listened_seconds

        result = [
            (self._artists[aid], secs / 60)
            for aid, secs in artist_time.items()
            if aid in self._artists
        ]

        return sorted(result, key=lambda x: x[1], reverse=True)[:n]
    
    def user_top_genre(self, user_id: str):
        genre_time = {}
        total_time = 0

        for session in self._sessions:
            user = getattr(session, "user", None)
            track = getattr(session, "track", None)

            if not user or not track:
                continue

            if getattr(user, "user_id", None) != user_id:
                continue

            genre = getattr(track, "genre", None)
            duration = getattr(session, "duration_listened_seconds", 0)

            if genre is None:
                continue

            genre_time[genre] = genre_time.get(genre, 0) + duration
            total_time += duration

        if total_time == 0 or not genre_time:
            return None

        top_genre = max(genre_time.items(), key=lambda x: (x[1], x[0]))[0]

        return (top_genre, (genre_time[top_genre] / total_time) * 100)
    
    def collaborative_playlists_with_many_artists(self, threshold: int = 3):
        result = []

        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artists = set()

                for track in playlist.tracks:
                    if isinstance(track, Song):  # exclude podcasts & audiobooks
                        artists.add(track.artist.artist_id)

                if len(artists) > threshold:
                    result.append(playlist)

        return sorted(result, key=lambda p: p.playlist_id)
    
    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        normal_count = 0
        normal_tracks = 0

        collab_count = 0
        collab_tracks = 0

        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                collab_count += 1
                collab_tracks += len(playlist.tracks)
            elif isinstance(playlist, Playlist):
                normal_count += 1
                normal_tracks += len(playlist.tracks)

        avg_normal = normal_tracks / normal_count if normal_count > 0 else 0.0
        avg_collab = collab_tracks / collab_count if collab_count > 0 else 0.0

        return {
            "Playlist": float(avg_normal),
            "CollaborativePlaylist": float(avg_collab)
        }
    
    def users_who_completed_albums(self):
        result = []

        albums = {
            album.title: set(album.track_ids())
            for album in self._albums.values()
            if album.track_ids()
        }

        for user in self._users.values():
            listened = set(user.unique_tracks_listened())
            completed = []

            for title, tracks in albums.items():
                if tracks.issubset(listened):
                    completed.append(title)

            if completed:
                result.append((user, sorted(completed)))

        result.sort(key=lambda x: x[0].user_id)

        return result