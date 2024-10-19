import spotipy
import os
import sys
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from dataclasses import dataclass
from typing import List

@dataclass
class SpotifySong:
    """Characteristics of a spotify object."""

    artist_name: str
    song_name: str


@dataclass
class SpotifyUtilizer:
    """Holds a list of SpotifySong objects."""

    list_of_songs: List[SpotifySong]


load_dotenv()

SPOTIFY_CLIENT_ID=os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET=os.getenv("SPOTIFY_CLIENT_SECRET")
scope = "user-library-read"
redirect_uri = "http://127.0.0.1:5000/"
user = 'spotify'
user_playlists = {}

def login_user():
    """Logs in the user to Spotify."""
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=redirect_uri, scope=scope))
    return sp

def getUserPlaylists():
    """Returns a dictionary of the user's playlist names and link."""

    sp = login_user()
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        user_playlists[playlist['name']] = playlist['href']
    return user_playlists

"""
TODO:
def login_user()
def return_all_playlists()
def send_user_playlist()
"""
