# spotify docs are here: https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
# but i found the base64 encoding here: https://dev.to/hmlon/explaining-how-oauth-works-with-spotify-as-an-example-5djl
import os 
import base64
import six
import json
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.environ["SPOTIPY_CLIENT_ID"]
client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]

refresh_url = "https://accounts.spotify.com/api/token" 

with open("ACCESS_TOKEN.json", "r") as f:
    refresh_token = json.load(f)["refresh_token"]

payload = {
    'refresh_token': refresh_token,
    'grant_type': 'refresh_token'
}

auth_header = base64.b64encode(six.text_type(client_id + ':' + client_secret).encode('ascii'))

headers = {
    'Authorization': 'Basic %s' % auth_header.decode('ascii'),
    'Content-Type': 'application/x-www-form-urlencoded'
}

res = requests.post(refresh_url, data=payload, headers=headers)

print(res.json())
{'access_token': 'BQATaycG1AfNCA3xIxTY9849w1hTVapVupphS6qrE_wToQEs4GbDV8gHy7CjkbtpxeJpCafU30HSo2V6EL9SuwCngokh7_PLh8lx58K6Fdyd4IRa3E_WN925jBybSTaTJcjdH0ee43OJZkiodAZkHMDjp-E16AkPGw', 'token_type': 'Bearer', 'expires_in': 3600, 'scope': 'streaming user-modify-playback-state user-read-playback-state user-read-currently-playing user-read-email'}