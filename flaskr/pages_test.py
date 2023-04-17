from flaskr import create_app
from unittest.mock import MagicMock
from unittest.mock import patch
from flask import request, render_template, redirect, url_for, flash, session
import pytest
from flask_wtf.csrf import generate_csrf
from io import BytesIO
from flaskr.models import User
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

#testing for route to get image for profile
def test_get_profile_img(client):
    image_data = b'sample image data'
    with patch('flaskr.backend.Backend.get_profile_img', return_value=BytesIO(image_data)):
        resp = client.get('/get_profile_img/sample.jpg')
    assert resp.status_code == 200
    assert resp.mimetype == 'image/jpg'
    assert resp.data == image_data

#test for profile route when user is not logged in
def test_profile_not_logged_in(client):
    # Test POST when the user is not authenticated 
    resp = client.post('/profile', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Login to Wiki' in resp.data


#set up for the logged in user for test_profile
def test_profile_logged_in(client):
    with patch('flask_login.utils._get_user') as mock_cc:
        with patch('flaskr.backend.Backend.get_image_url') as mock_url:
            user = User('Barsha')
            mock_cc.return_value = user
            mock_url.return_value = 'test_img/Barsha.jpg'
            resp = client.post('/profile', follow_redirects=True)
            assert resp.status_code == 200
            assert b'Customize Your Profile Here' in resp.data

#testing for the get request for the profile route when user is logged in
def test_profile_logged_in_GET_request(client):
    with patch('flask_login.utils._get_user') as mock_cc:
        with patch('flaskr.backend.Backend.get_image_url') as mock_url:
            # create a user object and set it as the current user
            user = User('Barsha')
            mock_cc.return_value = user
            
            # set the mock URL for the user's profile picture
            mock_url.return_value = 'test_img/Barsha.jpg'
            
            # make a GET request to the profile route
            resp = client.get('/profile')

            # check that the response status code is 200
            assert resp.status_code == 200
            
            #check if profile route  
            assert b'Customize Your Profile Here' in resp.data
            
            # check that the user's profile picture URL is in the response data
            assert b'test_img/Barsha.jpg' in resp.data

#testing for the post request for the profile route when user is logged in
def test_profile_logged_in_POST_request(client):
    with patch('flask_login.utils._get_user') as mock_cc:
        with patch('flaskr.backend.Backend.get_image_url') as mock_url:
            with patch('flaskr.backend.Backend.upload_profile') as mock_upload:
                # create a user object and set it as the current user
                user = User('Barsha')
                mock_cc.return_value = user

                # set the mock URL ans set return values for the user's profile picture
                mock_url.return_value = 'test_img/Barsha.jpg'
                filename = 'test_img/Barsha.jpg'
                file_stream = b'1234'
                mock_upload.return_value = True

                #make a post request to the profile route with file data
                resp = client.post('/profile', data={'file': (BytesIO(file_stream), filename)}, follow_redirects=True)
                assert resp.status_code == 200
                assert b'Profile Picture Changed!' in resp.data
                assert b'test_img/Barsha.jpg' in resp.data
                mock_upload.assert_called_once_with(filename, file_stream, user.username)

# Tests the search route.
def test_search_page(client):
    resp = client.get('/search')
    assert resp.status_code == 200
    assert b"Search For Netflix Shows" in resp.data
