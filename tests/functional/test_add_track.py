from app import create_app


def test_add_track():
    """
    GIVEN a Flask application configured for development
    WHEN the '/add_song' page is requested (POST) with correct payload
    THEN check that the song is added to DB correctly
    """
    flask_app, _ = create_app()
    track_payload = {
        "name": "name",
        "artist": "artist",
        "uri": "uri",
        "img_sm": "sm_img_url",
        "img_md": "md_img_url",
        "img_lg": "lg_img_url",
        "duration_ms": 1000,
    }
    with flask_app.test_client() as test_client:
        breakpoint()
        response = test_client.post("/add_track", json=track_payload)
        assert response.status_code == 201
        assert response.json()["message"] == "success"
