from app import Song



def test_new_party():
    """
    GIVEN a Party model
    WHEN a new Party is created
    THEN check the id, name, and access_tokens fields are defined correctly
    """
    test_track = Song(
        party_id=1,
        name="not yet",
        artist="not yet",
        votes=0,
        uri="none",
        img_sm="none",
        img_md="medium",
        img_lg="lg",
        progress_ms=0,
        duration_ms=1000,
    )
    assert party.id == 1
    assert party.name == "not yet"
    assert party.artist == "not yet"
    assert party.votes == 0
    assert party.uri == "none"
    assert party.img_sm == "none"
    assert party.img_md == "medium"
    assert party.img_lg == "lg"
    assert progress_ms == 0
    assert duration_ms == 1000
