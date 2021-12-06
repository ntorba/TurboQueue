import os
import requests
import uuid
import urllib.parse
from flask import request, redirect, Blueprint
from ..models import Party
from ..extensions import db 


SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = os.environ["SPOTIPY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIPY_CLIENT_SECRET"]
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-email streaming"
REDIRECT_URI = "http://localhost:5000/spotify_oauth/callback"
FINAL_REDIRECT_URI = "http://localhost:5000/party"
RANDOM_ID = str(uuid.uuid4())

spotify_oauth_blueprint = Blueprint('spotify_oauth', __name__, template_folder="templates")

@spotify_oauth_blueprint.route("/spotify_oauth/<party_id>")
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


@spotify_oauth_blueprint.route("/spotify_oauth/callback")
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
    party = Party.query.filter(Party.id == party_id).first()
    party.access_token = ACCESS_TOKEN
    party.refresh_token = REFRESH_TOKEN
    party.expires_in = res_data["expires_in"]
    db.session.commit()
    print("I JUST SET ACCESS and refresh TOKEN")
    url_args = f"access_token={ACCESS_TOKEN}" #&refresh_token={res_data['refresh_token']}" #TODO: do I  need refresh token in url? 
    redirect_url = "{}/?{}".format(f"{FINAL_REDIRECT_URI}/{party_id}", url_args)
    return redirect(redirect_url)