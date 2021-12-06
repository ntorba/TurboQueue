
import threading
import os
import requests
import uuid
import urllib.parse
from flask import render_template, request, redirect, Blueprint, current_app
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from ..models import Song, Party
from ..extensions import turbo, db 
from ..now_playing_utils import __update_now_playing, update_song_table

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

NOW_PLAYING = {} # keys: party_id, value: Song object, TODO: this should be a db thing, not in memory...

party_blueprint = Blueprint('party', __name__, template_folder="templates")

@party_blueprint.before_app_first_request
def before_app_first_request():
    from ..app import create_app
    myapp = create_app()
    def update_now_playing():
        with myapp.app_context():
            while True:
                for party in Party.query.filter(Party.active==True).all():
                    __update_now_playing(party.id)
    threading.Thread(target=update_now_playing).start()

@party_blueprint.route("/")
def hello():
    return render_template("index.html")


@party_blueprint.route("/spotify_search_tracks")
def spotify_search_tracks():
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


@party_blueprint.route("/add_track", methods=["POST"])
def add_track():
    party_id = int(request.json["track"]["party_id"])
    track_kwargs = request.json["track"]
    print("Your track kwargs!")
    print(track_kwargs)
    if "controller" in track_kwargs:
        track_kwargs.pop("controller") # TODO: this logic should probably not be here... why even send the data?
    track = Song(**track_kwargs)

    try:
        db.session.add(track)
        db.session.commit()
    except Exception as err:
        print("error while writing track to db...")
        raise err # TODO: improve this error handling..
    update_song_table(party_id)
    return {"message": "success"}, 201


@party_blueprint.route("/party/<party_id>/")
def party(party_id):
    party_id = int(party_id)
    party = Party.query.filter(Party.id == party_id).first()
    songs = Song.query.order_by(Song.votes.desc(), Song.pub_date).filter(Song.party_id == party_id).filter(Song.already_played==False).all()
    current_now_playing = __update_now_playing(party, update_db = False) # Putting update_db=True will cut off the db.session, which means you can't use songs after this function call
    if "access_token" not in request.args:
        print("rendering GUEST view")
        return render_template(
            "party.html",
            party_name=party.name,
            songs=songs,
            current_track=current_now_playing,
        )
    else:
        return render_template(
            "party.html",
            party_name=party.name,
            songs=songs,
            current_track=NOW_PLAYING.setdefault(party_id, EMPTY_TRACK),
            access_token=request.args["access_token"], 
        )

@party_blueprint.route("/vote", methods=["POST"])
def vote():
    # TODO: this is pretty inefficient.. reading the songs twice, writing in the middle, can do a lot better
    song_id = str(request.json["song_id"])
    party_id = int(request.json["party_id"])

    current_song_order = Song.query.order_by(Song.votes.desc(), Song.pub_date).filter(Song.party_id == party_id).all()

    ## This sorting will probably get that bad unless people have MASSIVE queues, in which case that could cause a problem
    selected_song = Song.query.filter(Song.id == song_id).first()
    selected_song.votes += 1
    db.session.commit() # TODO: select this sone and write it all at once after ordering to avoid this write
    
    new_song_order = Song.query.order_by(Song.votes.desc(), Song.pub_date).filter(Song.party_id == party_id).filter(Song.already_played==False).all() 

    if (
        new_song_order == current_song_order
    ):  ## If no resort is necessary, you can just push the number
        print("song table order did not update")
        turbo.push(
            turbo.update(
                f'<span class="p-3 inline-flex text-lg leading-5 font-semibold rounded-full bg-green-100 text-green-800">{selected_song.votes}</span>',
                selected_song.id,
            )
        )
    else:  # if the order has changed, we need to push the full table..
        print("song table order updated")
        turbo.push(
            turbo.update(
                render_template("song_table_body.html", songs=new_song_order),
                "song_table_body",
            )
        )
    return {"success": True, "uri": selected_song.uri}, 200

@party_blueprint.route("/next_track", methods=["POST"])
def play_next():
    party_id = int(request.json["party_id"])
    party_songs = Song.query.order_by(Song.votes.desc(), Song.pub_date).filter(Song.party_id == party_id).filter(Song.already_played == False).all()
    next_track = party_songs[0]
    print(f"next track = {next_track}")
    headers = {
        "Content-Type": "application/json", 
        "Authorization": request.headers["Authorization"]
    }
    payload = {
        "uris": [next_track.uri]
    }
    play_next_url ="https://api.spotify.com/v1/me/player/play"
    res = requests.put(play_next_url, json=payload, headers=headers)
    if res.status_code != 204:
        raise Exception("TODO: You're request to play next failed, make a better error")
    else: 
        next_track.already_played = True
        db.session.commit()
        update_song_table(party_id, songs=party_songs[1:])
        __update_now_playing(party_id)
        return {"success": True}, 204

@party_blueprint.route("/set_now_playing/<party_id>", methods=["PUT"])
def set_now_playing(party_id):
    __update_now_playing(int(party_id))
    return {"message": "success"}, 201