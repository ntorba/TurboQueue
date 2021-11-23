import os
from pathlib import Path
import requests
import uuid
import time
import threading
from random import randint
from dataclasses import dataclass, field, asdict
import urllib.parse
import json
from flask import Flask, render_template, request, redirect
from flask_cors import CORS
from turbo_flask import Turbo
from webpack_boilerplate.config import setup_jinja2_ext
from config import Config
from query_spotify import mac_miller_songs
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent


def create_app():
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
    return app, turbo

app, turbo = create_app()

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-email streaming"
REDIRECT_URI = "http://localhost:5000/spotify_oauth/callback"
FINAL_REDIRECT_URI = "http://localhost:5000/party"
RANDOM_ID = str(uuid.uuid4())
CURRENT_TRACK = dict(name="", album={"images": [{"url": ""}]}, artists=[{"name": ""}])


@dataclass
class Song:
    party_id: int
    name: str
    artist: str
    uri: str
    img_sm: str
    img_md: str
    img_lg: str
    votes: int = 0
    progress_ms: str = 0
    duration_ms: str = None

@dataclass
class Party:
    id: int
    name: str
    access_token: str


PARTY_DB = {1: Party(1, "Bailey's Birthday Party", None)}

CURRENT_TRACK = Song(
    party_id=1,
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

song_kwargs = mac_miller_songs(n=3)

EMPTY_TRACK = Song(
    party_id=1,
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

PARTY_ID = PARTY_DB[1].id
SONG_DB = {PARTY_ID: {"next_up": {}, "next_up_sorted": [], "now_playing": EMPTY_TRACK}}

for i, kwargs in enumerate(song_kwargs):
    SONG_DB[PARTY_ID]["next_up"][kwargs["uri"]] = Song(
        votes=randint(1, 5), party_id=1, **kwargs
    )
    SONG_DB[PARTY_ID]["next_up_sorted"] = sorted(
        SONG_DB[PARTY_ID]["next_up"].values(),
        key=lambda track: track.votes,
        reverse=True,
    )


def __get_remote_now_playing(access_token, party_id):
    res = requests.get(
        "https://api.spotify.com/v1/me/player",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    if res.status_code == 204:
        return res, None
    elif res.status_code == 200:
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
        now_playing = Song(party_id=party_id, **track_info)
        return res, now_playing
    else:
        return res, None


def __update_now_playing(party_id):
    access_token = PARTY_DB[party_id].access_token
    if os.path.isfile("ACCESS_TOKEN.json") and access_token is None:
        with open("ACCESS_TOKEN.json", "r") as f:
            token_data = json.load(f)
            access_token = token_data["access_token"]
            refresh_token = token_data["refresh_token"]
    elif access_token is None:
        time.sleep(3)
        return None
    if access_token is None:
        print(
            f"access token for party '{PARTY_DB[party_id].access_token}', with id {party_id} is not defined yet. sleeping..."
        )
        time.sleep(3)
        return None
    res, remote_now_playing = __get_remote_now_playing(access_token, party_id)
    if res.status_code == 204:
        # TODO: update this error handling...
        print("your playback is not on your party's device")
        time.sleep(5)
        return None
    if res.status_code != 200:
        # print(
        #     f"failed when getting now_playing from spotify with status code '{res.status_code}'"
        # )
        time.sleep(5)
        return None
    else:
        if SONG_DB[party_id]["now_playing"].name != remote_now_playing.name:
            turbo.push(
                turbo.update(
                    f'<img height="150" , width="150" src="{remote_now_playing.img_md}">',
                    "now_playing_img",
                )
            )
            turbo.push(
                turbo.update(
                    f'<div class="song-metadata text-center"><div class="text-lg font-medium text-gray-900">{remote_now_playing.name }</div><div class="text-lg text-gray-500">{ remote_now_playing.artist}</div></div>',
                    "now_playing_metadata",
                )
            )
        SONG_DB[party_id]["now_playing"] = remote_now_playing
        # print("pushing playback progress")
        turbo.push(
            turbo.update(
                f'<div class="h-full bg-green-500 absolute" style="width:{ round((remote_now_playing.progress_ms / remote_now_playing.duration_ms)*100) }%">',
                "now_playing_progress",
            )
        )
        time.sleep(1)


def update_now_playing():
    with app.app_context():
        while True:
            for key in PARTY_DB.keys():
                __update_now_playing(key)


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_now_playing).start()


@app.cli.command("webpack_init")
def webpack_init():
    from cookiecutter.main import cookiecutter
    import webpack_boilerplate

    pkg_path = os.path.dirname(webpack_boilerplate.__file__)
    cookiecutter(pkg_path, directory="frontend_template")


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/spotify_search_tracks")
def spotify_search_tracks():
    print("YOU MADE IT TO THE SRR FUNC")
    print("here are the args")
    print(request.args)
    query = request.args["search"]
    if len(query) == 0:
        return {"message": "you sent an empty query"}, 400
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.search(query, limit=5)
    results = [
        Song(
            **{
                "name": i["name"],
                "artist": i["artists"][0]["name"],
                "uri": i["uri"],
                "img_sm": i["album"]["images"][-1]["url"],
                "img_md": i["album"]["images"][1]["url"],
                "img_lg": i["album"]["images"][0]["url"],
                "duration_ms": i["duration_ms"],
                "party_id": 1 # TODO: this needs to come from client...
            }
        )
        for i in results["tracks"]["items"]
    ]
    return render_template("search_results.html", search_results=results)


@app.route("/add_track", methods=["POST"])
def add_track():
    party_id = int(request.json["track"]["party_id"])
    track_kwargs = request.json["track"]
    print("Your track kwargs!")
    print(track_kwargs)
    track_kwargs.pop("controller") # TODO: this logic should probably not be here... why even send the data?
    track = Song(**track_kwargs)

    # TODO: this would be way better as a class property or something so the sort happens automaticall and not manually
    SONG_DB[party_id]["next_up"][track.uri] = track
    SONG_DB[party_id]["next_up_sorted"] = sorted(
        SONG_DB[PARTY_ID]["next_up"].values(),
        key=lambda track: track.votes,
        reverse=True,
    )
    turbo.push(
        turbo.update(
            render_template(
                "song_table_body.html", songs=SONG_DB[party_id]["next_up_sorted"]
            ),
            "song_table_body",
        )
    )
    return {"message": "success"}, 201


@app.route("/next_up/<party_id>")
def next_up(party_id):
    return SONG_DB[int(party_id)]["next_up"]


@app.route("/party/<party_id>/")
def party(party_id):
    party_id = int(party_id)
    if "access_token" not in request.args:
        print("rendering GUEST view")
        return render_template(
            "party.html",
            party_name=PARTY_DB[party_id].name,
            songs=[track for track in SONG_DB[party_id]["next_up_sorted"]],
            current_track=SONG_DB[party_id]["now_playing"],
        )
    else:
        return render_template(
            "party.html",
            party_name=PARTY_DB[party_id].name,
            songs=[track for track in SONG_DB[party_id]["next_up_sorted"]],
            current_track=SONG_DB[party_id]["now_playing"],
            access_token=request.args["access_token"], 
            # refresh_token=request.args["refresh_token"]
        )


@app.route("/spotify_oauth/<party_id>")
def spotify_oauth(party_id):
    """
    Auth Step 1: Authorization, redirect to spotify login page
    This sends the user to spotify, where they agree to our scope, then it
    redirects them to /spotify_oauth/callback for me to parse the token,
    then redirect to the party or home page for them to do things.
    """
    auth_state = f"{party_id}-----{RANDOM_ID}"
    auth_query_parameters = {
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "client_id": CLIENT_ID,
        "state": auth_state,
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
    party_id, random_string = state.split("-----")
    party_id = int(party_id)
    if random_string != RANDOM_ID:
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
    REFRESH_TOKEN = res_data["refresh_token"]
    PARTY_DB[party_id].access_token = ACCESS_TOKEN
    PARTY_DB[party_id].refresh_token = REFRESH_TOKEN
    PARTY_DB[party_id].expires_in = res_data["expires_in"]
    with open("ACCESS_TOKEN.json", "w") as f:
        json.dump(
            {
                "access_token": ACCESS_TOKEN,
                "refresh_token": REFRESH_TOKEN, 
                "expires_in": res_data["expires_in"]
            }, 
            f, 
            indent=4
        )
    # TODO: update to not write this after I confirm I have things working
    print("I JUST SET ACCESS and refresh TOKEN")
    url_args = f"access_token={ACCESS_TOKEN}" #&refresh_token={res_data['refresh_token']}" #TODO: do I  need refresh token in url? 
    redirect_url = "{}/?{}".format(f"{FINAL_REDIRECT_URI}/{party_id}", url_args)
    return redirect(redirect_url)


@app.route("/vote", methods=["POST"])
def vote():
    song_uri = str(request.json["uri"])
    party_id = int(request.json["party_id"])
    ## This sorting will probably get that bad unless people have MASSIVE queues, in which case that could cause a problem
    SONG_DB[party_id]["next_up"][song_uri].votes += 1
    new_order = sorted(
        SONG_DB[party_id]["next_up"].values(), key=lambda x: x.votes, reverse=True
    )
    if (
        new_order == SONG_DB[party_id]["next_up_sorted"]
    ):  ## If no resort is necessary, you can just push the number
        turbo.push(
            turbo.update(
                f'<span class="p-3 inline-flex text-lg leading-5 font-semibold rounded-full bg-green-100 text-green-800">{SONG_DB[party_id]["next_up"][song_uri].votes}</span>',
                song_uri,
            )
        )
    else:  # if the order has changed, we need to push the full table..
        turbo.push(
            turbo.update(
                render_template("song_table_body.html", songs=new_order),
                "song_table_body",
            )
        )
        SONG_DB[party_id]["next_up_sorted"] = new_order
    return {"success": True, "uri": song_uri}, 200


@app.route("/set_now_playing/<party_id>", methods=["PUT"])
def set_now_playing(party_id):
    __update_now_playing(int(party_id))
    return {"message": "success"}, 201


@app.route("/playground")
def playground():
    return render_template(
        "playground.html",
        songs=sorted(SONG_DB.values(), key=lambda x: x.votes, reverse=True),
    )


@app.route("/playground_mobile")
def playground_mobile():
    return render_template(
        "playground-mobile-first-different-scroll.html",
        songs=sorted(SONG_DB.values(), key=lambda x: x.votes, reverse=True),
    )
