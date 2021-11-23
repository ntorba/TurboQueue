from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'
db = SQLAlchemy(app)

from datetime import datetime

class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    songs = db.relationship('Song', backref='party', lazy=True)

    def __repr__(self):
        return '<Party %r>' % self.name


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # party = db.relationship('Party', backref=db.backref('songs', lazy=True))
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    artist = db.Column(db.String(50), nullable=False)
    uri = db.Column(db.String(80), nullable=False)
    img_sm = db.Column(db.String(80), nullable=False)
    img_md = db.Column(db.String(80), nullable=False)
    img_lg = db.Column(db.String(80), nullable=False)
    votes = db.Column(db.Integer)
    progress_ms = db.Column(db.Integer)
    duration_ms = db.Column(db.Integer)

    def __repr__(self):
        return '<Song %r>' % self.name



party_1 = Party(name="big", access_token="token")
party_2 = Party(name="p2", access_token="token2")

song_1 = Song(
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

song_7 = Song(
    party_id=7,
    name="2222",
    artist="not yet",
    votes=0,
    uri="none",
    img_sm="none",
    img_md="none",
    img_lg="none",
    progress_ms=0,
    duration_ms=1,
)

party_1.songs.append(song_1)

db.session.add(song_2)
db.session.add(party_1)
db.session.add(party_2)
db.session.commit()