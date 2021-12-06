from flask.cli import FlaskGroup

from backend.app import create_app, db 

cli = FlaskGroup(create_app=create_app)

@cli.command()
def recreate_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command()
def seed_db():
    """Put some inital data in the database"""
    from random import randint
    from query_spotify import mac_miller_songs
    from backend.models import Party, Song 

    song_kwargs = mac_miller_songs(n=3)

    party = Party(name="Bailey's Birthday Party", access_token="token-placeholder", refresh_token="placeholder")
    db.session.add(party)

    for i, kwargs in enumerate(song_kwargs):
        db.session.add(Song(votes=randint(1,5), party_id=1, **kwargs))

    db.session.commit()
    songs = Song.query.all()
    print("")
    print("db now has the follinwg songs and parties:")
    print(Song.query.all())
    print(Party.query.all())


if __name__ == '__main__':
    cli()
