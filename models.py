from datetime import datetime

from app_with_db import db 

class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    songs = db.relationship('Song', backref='party', lazy=True)

    def __repr__(self):
        return '<Party %r>' % self.title


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