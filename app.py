import os
from pathlib import Path
from flask.globals import current_app
import requests
import json
from random import randint
from dataclasses import dataclass
import urllib.parse
from flask import Flask, render_template, request, redirect
from flask_cors import CORS
from turbo_flask import Turbo
from webpack_boilerplate.config import setup_jinja2_ext
from config import Config
from query_spotify import mac_miller_songs
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
app = Flask(__name__, static_folder="frontend/build", static_url_path="/static/")
app.config.from_object(Config)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"
app.config.update(
    {
        "WEBPACK_LOADER": {
            "MANIFEST_FILE": os.path.join(BASE_DIR, "frontend/build/manifest.json"),
        }
    }
)
setup_jinja2_ext(app)
turbo = Turbo(app)

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-email streaming"
REDIRECT_URI = "http://localhost:5000/spotify_oauth/callback"
FINAL_REDIRECT_URI = "http://localhost:5000/party"
AUTH_INITIAL_STATE = "heasfdasd"


CURRENT_TRACK = dict(name="", album={"images": [{"url": ""}]}, artists=[{"name": ""}])


@dataclass
class Song:
    name: str
    artist: str
    votes: int
    uri: str
    img: str


song_kwargs = mac_miller_songs(n=20)

SONGS = {}
for i, kwargs in enumerate(song_kwargs):
    SONGS[kwargs["uri"]] = Song(votes=randint(1, 100), **kwargs)


@app.cli.command("webpack_init")
def webpack_init():
    from cookiecutter.main import cookiecutter
    import webpack_boilerplate

    pkg_path = os.path.dirname(webpack_boilerplate.__file__)
    cookiecutter(pkg_path, directory="frontend_template")


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/party/")
def party():
    return render_template(
        "party.html",
        songs=sorted(SONGS.values(), key=lambda x: x.votes, reverse=True),
        current_track=CURRENT_TRACK,
    )


@app.route("/spotify_oauth")
def spotify_oauth():
    """
    Auth Step 1: Authorization, redirect to spotify login page
    This sends the user to spotify, where they agree to our scope, then it
    redirects them to /spotify_oauth/callback for me to parse the token,
    then redirect to the party or home page for them to do things.
    """
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "client_id": CLIENT_ID,
        "state": AUTH_INITIAL_STATE,
    }
    url_args = "&".join(
        [
            "{}={}".format(key, urllib.parse.quote(val))
            for key, val in auth_query_parameters.items()
        ]
    )
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/spotify_oauth/callback")
def spotify_get_token():
    # Auth Step 4: Requests refresh and access tokens
    # print('THat original request: ', file=sys.stderr)
    # print(request, file=sys.stderr)
    state = request.args["state"]
    if state != AUTH_INITIAL_STATE:
        raise Exception(
            "The state is different from my request, spotify told me to reject this situation"
        )
    auth_token_code = request.args["code"]
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token_code),
        "redirect_uri": REDIRECT_URI,  # Must match the redirect_uri used to get the code (not actually used for redirection)
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    res = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    res_data = res.json()
    url_args = f"access_token={res_data['access_token']}&refresh_token={res_data['refresh_token']}"
    redirect_url = "{}/#{}".format(FINAL_REDIRECT_URI, url_args)
    return redirect(redirect_url)


@app.route("/spotify/callback")
def spotify_callback():
    return "You finally called me back!"


@app.route("/vote", methods=["POST"])
def vote():
    song_uri = str(request.json["uri"])
    SONGS[song_uri].votes += 1
    turbo.push(
        turbo.update(
            render_template(
                "party.html",
                songs=sorted(SONGS.values(), key=lambda x: x.votes, reverse=True),
                current_track=CURRENT_TRACK,
            ),
            "party",
        )
    )
    return {"success": True, "uri": song_uri}, 200


@app.route("/playground")
def playground():
    return render_template(
        "playground.html",
        songs=sorted(SONGS.values(), key=lambda x: x.votes, reverse=True),
    )


@app.route("/now_playing", methods=["POST"])
def now_playing():
    state = request.json["state"]
    turbo.push(
        turbo.update(
            render_template(
                "now_playing.html",
                current_track=state["track_window"]["current_track"],
            ),
            "now_playing",
        )
    )
    return {"success": True}, 200
