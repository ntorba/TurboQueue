from datetime import datetime
from .app import db

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'), nullable=False)

    name = db.Column(db.String(50), nullable=False)
    artist = db.Column(db.String(50), nullable=False)
    uri = db.Column(db.String(80), nullable=False)
    img_sm = db.Column(db.String(80), nullable=False)
    img_md = db.Column(db.String(80), nullable=False)
    img_lg = db.Column(db.String(80), nullable=False)
    votes = db.Column(db.Integer, nullable=False, default=0)
    progress_ms = db.Column(db.Integer)
    duration_ms = db.Column(db.Integer)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    already_played = db.Column(db.Boolean, nullable=False, default=False)
    played_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Song %r>' % self.name

class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    access_token = db.Column(db.String(100), nullable=False)
    refresh_token = db.Column(db.String(100), nullable=False)
    expires_in = db.Column(db.Integer, nullable=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    songs = db.relationship(Song, backref='party')
    active = db.Column(db.Boolean, default=True)
    now_playing_song_id = db.Column(db.Integer) # TODO: Use a relationship for this..