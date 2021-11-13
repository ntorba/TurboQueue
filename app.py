import os
from pathlib import Path
from flask.globals import current_app
import requests
import time
import threading
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
    img_sm: str
    img_md: str
    img_lg: str
    progress_ms: str = None
    duration_ms: str = None


EMPTY_TRACK = Song(
    name="not yet",
    artist="not yet",
    votes=0,
    uri="none",
    img_sm="none",
    img_md="none",
    img_lg="none",
    progress_ms=0,
    duration_ms=1,
)

song_kwargs = mac_miller_songs(n=20)

SONGS = {}
for i, kwargs in enumerate(song_kwargs):
    SONGS[kwargs["uri"]] = Song(votes=randint(1, 100), **kwargs)

CURRENT_TRACK_NAME = "unset"


def __update_now_playing():
    global CURRENT_TRACK_NAME
    if os.path.isfile("ACCESS_TOKEN.txt"):
        with open("ACCESS_TOKEN.txt", "r") as f:
            ACCESS_TOKEN = f.read()
    else:
        time.sleep(2)
        return None
    print("we in here!!!")
    print("YOU MADE IT, ABOUT TO MAKE REQUEST...")
    res = requests.get(
        "https://api.spotify.com/v1/me/player",
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    print("here is status code: ", res.status_code)
    if res.status_code == 204:
        time.sleep(5)
        return None
    elif res.status_code == 200:
        print("you got a 200!")
        body = res.json()
        track_info = {}
        track_info["artist"] = body["item"]["artists"][0]["name"]
        track_info["name"] = body["item"]["name"]
        track_info["uri"] = body["item"]["uri"]
        track_info["img_sm"] = body["item"]["album"]["images"][-1]["url"]
        track_info["img_md"] = body["item"]["album"]["images"][1]["url"]
        track_info["img_lg"] = body["item"]["album"]["images"][0]["url"]
        track_info["duration_ms"] = body["item"]["duration_ms"]
        track_info["progress_ms"] = body["progress_ms"]
        track_info["votes"] = 0
        song = Song(**track_info)
        print(song.name, CURRENT_TRACK_NAME)
        if CURRENT_TRACK_NAME != song.name:
            print("pushing a new song!!")
            turbo.push(
                turbo.update(
                    f'<img height="150" , width="150" src="{song.img_md}">',
                    "now_playing_img",
                )
            )
            turbo.push(
                turbo.update(
                    f'<div class="song-metadata text-center"><div class="text-lg font-medium text-gray-900">{song.name }</div><div class="text-lg text-gray-500">{ song.artist}</div></div>',
                    "now_playing_metadata",
                )
            )
        CURRENT_TRACK_NAME = song.name
        turbo.push(
            turbo.update(
                f'<div class="h-full bg-green-500 absolute" style="width:{ round((song.progress_ms / song.duration_ms)*100) }%">',
                "now_playing_progress",
            )
        )
        time.sleep(1)


def update_now_playing():
    with app.app_context():
        while True:
            print("updating now playing...")
            __update_now_playing()


threading.Thread(target=update_now_playing).start()

# @app.before_first_request
# def before_first_request():
#     threading.Thread(target=update_now_playing).start()


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
        current_track=EMPTY_TRACK,
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
    ACCESS_TOKEN = res_data["access_token"]
    with open("ACCESS_TOKEN.txt", "w") as f:
        f.write(ACCESS_TOKEN)
    print("I JUST SET ACCESS TOKEN")
    url_args = f"access_token={ACCESS_TOKEN}&refresh_token={res_data['refresh_token']}"
    redirect_url = "{}/#{}".format(FINAL_REDIRECT_URI, url_args)
    return redirect(redirect_url)


@app.route("/spotify/callback")
def spotify_callback():
    return "You finally called me back!"


@app.route("/vote", methods=["POST"])
def vote():
    song_uri = str(request.json["uri"])
    ## This sorting will probably get that bad unless people have MASSIVE queues, in which case that could cause a problem
    current_order = sorted(SONGS.values(), key=lambda x: x.votes, reverse=True)
    current_order = [i.name for i in current_order]
    SONGS[song_uri].votes += 1
    new_order_full = sorted(SONGS.values(), key=lambda x: x.votes, reverse=True)
    new_order = [i.name for i in new_order_full]
    if (
        new_order == current_order
    ):  ## If no resort is necessary, you can just push the number
        turbo.push(
            turbo.update(
                f'<span class="p-3 inline-flex text-lg leading-5 font-semibold rounded-full bg-green-100 text-green-800">{SONGS[song_uri].votes}</span>',
                song_uri,
            )
        )
    else:  # if the order has changed, we need to push the full table..
        turbo.push(
            turbo.update(
                render_template("song_table_body.html", songs=new_order_full),
                "song_table_body",
            )
        )
    return {"success": True, "uri": song_uri}, 200


@app.route("/playground")
def playground():
    return render_template(
        "playground.html",
        songs=sorted(SONGS.values(), key=lambda x: x.votes, reverse=True),
    )


@app.route("/playground_mobile")
def playground_mobile():
    return render_template(
        "playground-mobile-first-different-scroll.html",
        songs=sorted(SONGS.values(), key=lambda x: x.votes, reverse=True),
    )
