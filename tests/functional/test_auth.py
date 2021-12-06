import pytest 
import os
import webbrowser

from backend.app import create_app

@pytest.fixture(scope='module')
def test_client():
    app = create_app("Test")
    # Create a test client using the Flask application configured for testing
    with app.test_client() as testing_client:
        # Establish an application context
        with app.app_context():
            yield testing_client  # this is where the testing happens!

def test_spotify_oauth(test_client):
    response = test_client.get('/spotify_oauth/1') # TODO: The party number currently doesn't matter... that's bad...
    assert response.status_code == 302
    res_data = response.get_data().decode()
    key = 'href="'
    url_start = res_data.find(key) + len(key)
    url_end = res_data.find('"', url_start)
    url = res_data[url_start:url_end]
    # TODO: i'm not sure how to get through the spotify oauth page...
    webbrowser.open(url)