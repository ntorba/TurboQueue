import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()


def mac_miller_songs(n=5):
    mac_miller_uri = "spotify:artist:4LLpKhyESsyAXpc4laK94U"
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.artist_top_tracks(mac_miller_uri)
    tracks = results["tracks"][:n]
    table_info = []
    for i_track in tracks:
        track_info = {}
        track_info["artist"] = i_track["artists"][0]["name"]
        track_info["name"] = i_track["name"]
        track_info["uri"] = i_track["uri"]
        track_info["img_sm"] = i_track["album"]["images"][-1]["url"]
        track_info["img_md"] = i_track["album"]["images"][1]["url"]
        track_info["img_lg"] = i_track["album"]["images"][0]["url"]
        table_info.append(track_info)
    return table_info


a = mac_miller_songs()
