from app import Party


def test_new_party():
    """
    GIVEN a Party model
    WHEN a new Party is created
    THEN check the id, name, and access_tokens fields are defined correctly
    """
    party = Party(1, "god's honest throwdown", "token_string")
    assert party.id == 1
    assert party.name == "god's honest throwdown"
    assert party.access_token == "token_string"
