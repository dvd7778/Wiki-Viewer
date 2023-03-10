from flaskr import create_app
from unittest.mock import MagicMock

import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.

# Test for home route.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Welcome to the NetflixSeries Wiki!" in resp.data

# Test for upload route.
def test_upload_page(client):
    resp = client.get('/upload')
    assert resp.status_code == 200
    assert b"Upload File to the Wiki" in resp.data

# Test for pages route.
def test_pages_page(client):
    resp = client.get('/pages')
    assert resp.status_code == 200
    assert b"Best Netflix Series" in resp.data

# Test for about route.
def test_about_page(client):
    resp = client.get('/about')
    assert resp.status_code == 200
    assert b"About this Wiki" in resp.data

# Test for login route.
def test_login_page(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b"Login to Wiki" in resp.data

# Test for register route.
def test_register_page(client):
    resp = client.get('/register')
    assert resp.status_code == 200
    assert b"Sign up to NetflixSeries Wiki" in resp.data

# Test for parametrized pages route.
def test_parametrized_pages(client):
    filename = "TestFile"
    resp = client.get(f'/pages/{filename}')
    assert resp.status_code == 200
    assert b'Page not found.' in resp.data
    
"""
def test_parametrized_pages2(client):
    filename = "TestFile"
    filename_bytes = f'{filename}'.encode()
    b = MagicMock()
    b.get_wiki_page().return_value = ["This", "is", "a", "test"]
    resp = client.get(f'/pages/{filename}')
    assert resp.status_code == 200
    assert filename_bytes in resp.data
    assert b'Page does not exist.' in resp.data
"""