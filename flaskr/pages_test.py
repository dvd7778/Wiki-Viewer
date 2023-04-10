from flaskr import create_app
from unittest.mock import MagicMock
from unittest.mock import patch
from flask import request, render_template, redirect, url_for, flash, session
import pytest
from flask_wtf.csrf import generate_csrf
from flaskr import pages


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


# Test for upload route.
def test_upload_page(client):
    resp = client.get('/upload')
    assert resp.status_code == 200
    assert b"Upload Shows to the Wiki" in resp.data
    #Test for the feature1-adding genre clickable button
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
# TODO: This test is not mocking validate_on_submit() properly, needs to be fixed.
# For now, removing the prefix "test_" so that pytest doesn't run it.
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
    filename = "TestFile"
    resp = client.get(f'/pages/{filename}')
    assert resp.status_code == 200
    assert b'Page not found.' in resp.data


# Tests that the parametrized pages renders a page with the parameter file's content
def test_parametrized_pages_working(client):
    with patch('flaskr.backend.Backend.get_wiki_page') as get_wiki_page:
        filename = "TestFile"
        filename_bytes = f'{filename}'.encode()
        get_wiki_page.return_value = ["This", "is", "a", "test"]
        resp = client.get(f'/pages/{filename}')
        assert resp.status_code == 200
        assert filename_bytes in resp.data
        assert b'This' in resp.data
        assert b'is' in resp.data
        assert b'a' in resp.data
        assert b'test' in resp.data


#testing pages for login success
def test_login_success(client):
    response = client.post('/login', follow_redirects=True)
    assert response.status_code == 200
    assert b'<p class="message">You have successfully logged in!</p>' in response.data



# Tests the profile route.
def test_profile_page(client):
    resp = client.get('/profile')
    assert resp.status_code == 200
    assert b"Customize Your Profile Here" in resp.data


# Tests the search route.
def test_search_page(client):
    resp = client.get('/search')
    assert resp.status_code == 200
    assert b"Search For Netflix Shows" in resp.data

def test_search_results_title_fail(client):
    with patch('flaskr.backend.Backend.title_search') as title_search:
        with patch('flaskr.backend.Backend.genre_search') as genre_search:
            title_search.return_value = "No results"
            genre_search.return_value = []
            resp = client.post('/search', data = {'choice': 'Title', 'search': 'Fail'})
            assert resp.status_code == 200
            genre_search.assert_not_called()
            title_search.assert_called_once_with('Fail')
            assert b'No results' in resp.data

def test_search_results_title_working(client):
    with patch('flaskr.backend.Backend.title_search') as title_search:
        with patch('flaskr.backend.Backend.genre_search') as genre_search:
            title_search.return_value = ["Title", "pages"]
            genre_search.return_value = []
            resp = client.post('/search', data = {'choice': 'Title', 'search': 'Working'})
            assert resp.status_code == 200
            genre_search.assert_not_called()
            title_search.assert_called_once_with('Working')
            assert b'Results for Working' in resp.data
            assert b'Title' in resp.data
            assert b'pages' in resp.data

def test_search_results_genre_fail(client):
    with patch('flaskr.backend.Backend.title_search') as title_search:
        with patch('flaskr.backend.Backend.genre_search') as genre_search:
            genre_search.return_value = "No results"
            title_search.return_value = []
            resp = client.post('/search', data = {'choice': 'Genre', 'search': 'Fail'})
            assert resp.status_code == 200
            title_search.assert_not_called()
            genre_search.assert_called_once_with('Fail')
            assert b'No results' in resp.data
    
def test_search_results_genre_working(client):
    with patch('flaskr.backend.Backend.title_search') as title_search:
        with patch('flaskr.backend.Backend.genre_search') as genre_search:
            genre_search.return_value = ["Genre", "pages"]
            title_search.return_value = []
            resp = client.post('/search', data = {'choice': 'Genre', 'search': 'Working'})
            assert resp.status_code == 200
            title_search.assert_not_called()
            genre_search.assert_called_once_with('Working')
            assert b'Results for Working' in resp.data
            assert b'Genre' in resp.data
            assert b'pages' in resp.data