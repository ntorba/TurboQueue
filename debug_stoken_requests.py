
import requests
from backend.app import create_app 
from backend.extensions import db 
from backend.models import Party 

app = create_app()

with app.app_context():
    party = Party.query.first()
    access_token = party.access_token

headers = {
    "Content-Type": "application/json", 
    "Authorization": "Bearer " + access_token
}

res = requests.get("https://api.spotify.com/v1/me", headers=headers)
breakpoint()
print(res)
