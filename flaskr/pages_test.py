from flaskr import create_app
from unittest.mock import MagicMock
from unittest.mock import patch
from flask import request, render_template, redirect, url_for, flash, session
import pytest
from flask_wtf.csrf import generate_csrf
import io


# See https://flask.palletsprojects.com/en/2.2.x/testing/
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
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


# Test for getting the upload route.
def test_upload_page_get(client):
    resp = client.get('/upload')
    assert resp.status_code == 200
    assert b"Upload File to the Wiki" in resp.data
    #Test for the feature1-adding genre clickable button
    assert b"Select at least one genre the show belong to:" in resp.data

# Test for a correct upload in the upload page
def test_upload_page_post_working(client):
    with patch('flaskr.backend.Backend.upload') as upload:
        with patch('flaskr.backend.Backend.upload_genres') as upload_genres:
            resp = client.post('/upload', data = {'file' : (io.BytesIO(b"test"), 'Wednesday.txt'), 'genre_adv' : 'Adventure', 'genre_hor' : 'Horror'})
            assert resp.status_code == 200
            upload_genres.assert_called_once_with('Wednesday.txt', ['Adventure', 'Horror'])
            upload.assert_called_once_with('Wednesday.txt', b"test")
            assert b"file uploaded successfully" in resp.data

# Test that the file is not uploaded if no genres were selected
def test_upload_page_post_fail(client):
    with patch('flaskr.backend.Backend.upload') as upload:
        with patch('flaskr.backend.Backend.upload_genres') as upload_genres:
            resp = client.post('/upload', data = {'file' : (io.BytesIO(b"test"), 'Wednesday.txt')})
            assert resp.status_code == 200
            upload_genres.assert_not_called()
            upload.assert_not_called()
            assert b"No genres were selected. Please select at least one genre." in resp.data
            assert b"Upload File to the Wiki" in resp.data
            assert b"Select at least one genre the show belong to:" in resp.data

# Tests the pages page renders correctly and the list of the uploaded pages
def test_pages_page(client):
    with patch(
            'flaskr.backend.Backend.get_all_page_names') as get_all_page_names:
        get_all_page_names.return_value = ["test", "hello"]
        resp = client.get('/pages')
        assert resp.status_code == 200
        assert b"Best Netflix Series" in resp.data
        assert b"test" in resp.data
        assert b"hello" in resp.data


# Tests that the about page renders correctly
def test_about_page(client):
    resp = client.get('/about')
    assert resp.status_code == 200
    assert b"About this Wiki" in resp.data


# Test for login route.
def test_login_page(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b"Login to Wiki" in resp.data


# Test for login route fail.
@patch('flaskr.backend.Backend')
@patch('flaskr.forms.LoginForm')
def login_fail(mock_backend, mock_form, client):
    mock_form.validate_on_submit.return_value = True
    mock_backend.sign_in.return_value = False
    resp = client.post('/login',data = {"email": "Barshachy@gmail.com", "password": "password"})
    assert resp.status_code == 200
    assert b'Login Unsuccessful! Please check your username and password again!' in resp.data


# Test for register route.
def test_register_page(client):
    resp = client.get('/register')
    assert resp.status_code == 200
    assert b"Sign up to NetflixSeries Wiki" in resp.data
    assert b"Have Netflix Account?:" in resp.data


# Tests that the parametrized pages renders a "Page not found." message when the page is not in the content bucket
def test_parametrized_pages_fail(client):
    with patch('flaskr.backend.Backend.get_wiki_page') as get_wiki_page: # patches the get_wiki_page Backend method
        with patch('flaskr.backend.Backend.get_genres') as get_genres: # patches the get_genres Backend method
            get_wiki_page.return_value = None # sets the return value for the patched get_wiki_page method to None
            get_genres.return_value = [] # sets the return value of the patched get_genres method to an empty list
            filename = "TestFile"
            resp = client.get(f'/pages/{filename}')
            assert resp.status_code == 200
            assert b'Page not found.' in resp.data
            get_wiki_page.assert_called_once_with(filename)
            get_genres.assert_not_called()


# Tests that the parametrized pages renders a page with the parameter file's content and it's genres
def test_parametrized_pages_working(client):
    with patch('flaskr.backend.Backend.get_wiki_page') as get_wiki_page: # patches the get_wiki_page Backend method
        with patch('flaskr.backend.Backend.get_genres') as get_genres: # patches the get_genres Backend method
            filename = "Cyberpunk Edgerunners"
            filename_bytes = f'{filename}'.encode()
            # sets the return value for the patched get_wiki_page method to a list of strings
            get_wiki_page.return_value = ["This", "is", "a", "test"]
            # sets the return value of the patched get_genres method to a list of genres as strings
            get_genres.return_value = ["Action", "Animation", "Science Fiction", "Thriller"] 

            resp = client.get(f'/pages/{filename}')
            get_genres.assert_called_once_with(filename)
            get_wiki_page.assert_called_once_with(filename)
            assert resp.status_code == 200
            assert filename_bytes in resp.data
            assert b'This' in resp.data
            assert b'is' in resp.data
            assert b'a' in resp.data
            assert b'test' in resp.data
            assert b'Genres' in resp.data
            assert b'Action' in resp.data
            assert b'Animation' in resp.data
            assert b'Science Fiction' in resp.data
            assert b'Thriller' in resp.data

#testing pages for login success
def test_login_success(client):
    response = client.post('/login', follow_redirects=True)
    assert response.status_code == 200
    assert b'<p class="message">You have successfully logged in!</p>' in response.data