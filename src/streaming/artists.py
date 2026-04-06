"""
artists.py
----------
Implement the Artist class representing musicians and content creators.

Classes to implement:
  - Artist
"""
class Artist:
    def __init__(self, artist_id, name, genre, tracks = None):
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.tracks = tracks if tracks is not None else []
        self.albums = []

    def add_track(self, track):
        if track not in self.tracks:
            self.tracks.append(track)
             
    def track_count(self):
        return len(self.tracks)
    
    def add_album(self, album):
        self.albums.append(album)
        