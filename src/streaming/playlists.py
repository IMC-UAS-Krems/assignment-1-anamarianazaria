"""
playlists.py
------------
Implement playlist classes for organizing tracks.

Classes to implement:
  - Playlist
    - CollaborativePlaylist
"""

class Playlist():
    def __init__(self, playlist_id, name, owner, tracks = None):
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.tracks = tracks if tracks is not None else []

    def add_track(self, track):
        if track not in self.tracks:
            self.tracks.append(track)

    def remove_track(self, track_id):
        self.tracks = [track for track in self.tracks if track.track_id != track_id]

    def total_duration_seconds(self):
        return sum(track.duration_seconds for track in self.tracks)
    

class CollaborativePlaylist(Playlist):
    def __init__(self, playlist_id, name, owner, tracks=None, contributors=None):
        super().__init__(playlist_id, name, owner, tracks)
        self.contributors = contributors if contributors is not None else []

    def add_contributor(self, user):
        if user not in self.contributors:
            self.contributors.append(user)

    def remove_contributor(self, user):
        if user in self.contributors:
            self.contributors.remove(user)