import requests
import time
from flask import render_template, current_app
from .extensions import turbo, db
from .models import Song, Party

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


def __get_remote_now_playing(party, update_db = False):
    res = requests.get(
        "https://api.spotify.com/v1/me/player",
        headers={
            "Authorization": f"Bearer {party.access_token}",
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
        now_playing = Song(party_id=party.id, already_played=True, **track_info)
        if update_db:
            if now_playing not in party.songs:
                db.session.add(now_playing)
                db.session.commit()
        return res, now_playing
    else:
        return res, None

def __update_now_playing(party, update_db=False):
    if isinstance(party, int):
        party = Party.query.filter(Party.id == party).first()
    else: 
        party = party
    if party.access_token is None:
        print(
            f"access token for party '{party.name}', with id {party.id} is not defined yet. sleeping..."
        )
        time.sleep(3)
        return None
    
    res, remote_now_playing = __get_remote_now_playing(party, update_db)
    if remote_now_playing is None: 
        remote_now_playing = EMPTY_TRACK
    
    if res.status_code == 204:
        # TODO: update this error handling...
        print("your playback is not on your party's device")
        time.sleep(5)
        return None
    if res.status_code != 200:
        print(
            f"failed when getting now_playing from spotify with status code '{res.status_code}'"
        )
        print(res.text)
        time.sleep(5)
        return None
    else:
        with current_app.app_context():
            current_now_playing_song_id = Party.query.filter(Party.id == party.id).first().now_playing_song_id
            current_now_playing = Song.query.filter(Song.id == current_now_playing_song_id).first()

            # current_now_playing = NOW_PLAYING.setdefault(party.id, remote_now_playing)
            print("current_now_playing = ", current_now_playing)
            print("remote_now_playing.name = ", remote_now_playing.name)
            if current_now_playing != remote_now_playing.name: # "remote" now_playing is spotify
                print("I should update the IMAGE..")
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
            party.now_playing_party_id = remote_now_playing.id 
            print("pushing playback progress")
            turbo.push(
                turbo.update(
                    f'<div class="h-full bg-green-500 absolute" style="width:{ round((remote_now_playing.progress_ms / remote_now_playing.duration_ms)*100) }%">',
                    "now_playing_progress",
                )
            )
        return remote_now_playing

def update_song_table(party_id, songs=None):
    if songs is None: 
        songs = Song.query.order_by(Song.votes.desc(), Song.pub_date).filter(Song.party_id == party_id).filter(Song.already_played==False).all()
    with current_app.app_context():
        turbo.push(
            turbo.update(
                render_template(
                    "song_table_body.html", songs=songs
                ),
                "song_table_body",
            )
        )