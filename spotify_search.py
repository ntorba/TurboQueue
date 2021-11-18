import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
