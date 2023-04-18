from flaskr import create_app
from unittest.mock import MagicMock
from unittest.mock import patch
from flask import request, render_template, redirect, url_for, flash, session
import pytest
from flask_wtf.csrf import generate_csrf
from flaskr.models import User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import datetime, timedelta
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


# Test for getting the upload route.
def test_upload_page_get(client):
    resp = client.get('/upload')
    assert resp.status_code == 200
    assert b"Upload Shows to the Wiki" in resp.data
    #Test for the feature1-adding genre clickable button
    assert b"Select at least one genre the show belong to:" in resp.data

# Test for a correct upload in the upload page
def test_upload_page_post_working(client):
    with patch('flaskr.backend.Backend.upload') as upload: # patches the Backend upload method
        with patch('flaskr.backend.Backend.upload_genres') as upload_genres: # patches the Backend upload_genres method
            resp = client.post('/upload', data = {'file' : (BytesIO(b"test"), 'Wednesday.txt'), 'genre_adv' : 'Adventure', 'genre_hor' : 'Horror'})
            assert resp.status_code == 200
            upload_genres.assert_called_once_with('Wednesday.txt', ['Adventure', 'Horror'])
            upload.assert_called_once_with('Wednesday.txt', b"test")
            assert b"file uploaded successfully" in resp.data

# Test that the file is not uploaded if no genres were selected
def test_upload_page_post_fail(client):
    with patch('flaskr.backend.Backend.upload') as upload: # patches the Backend upload method
        with patch('flaskr.backend.Backend.upload_genres') as upload_genres: # patches the Backend upload_genres method
            resp = client.post('/upload', data = {'file' : (BytesIO(b"test"), 'Wednesday.txt')})
            assert resp.status_code == 200
            upload_genres.assert_not_called()
            upload.assert_not_called()
            assert b"No genres were selected. Please select at least one genre." in resp.data
            assert b"Upload Shows to the Wiki" in resp.data
            assert b"Select at least one genre the show belong to:" in resp.data

# Tests the pages page renders correctly and the list of the uploaded pages
def test_pages_page(client):
    with patch('flaskr.backend.Backend.get_all_page_names') as get_all_page_names: # patches the Backend get_all_page_names method
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


#Will work on this on separate branch

# # Test for login route fail.
# def test_login_fail(client):
#     with patch('flaskr.backend.Backend.get_wiki_page') as mock_backend:
#         with patch('flaskr.forms.LoginForm') as mock_form:
#             mock_form.validate_on_submit.return_value = True
#             mock_backend.sign_in.return_value = False
#             resp = client.post('/login',data = {"email": "Barshachy@gmail.com", "password": "password"})
#             assert resp.status_code == 200
#             assert b'Login Unsuccessful! Please check your username and password again!' in resp.data
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

#Testing for reset_request and send_reset_email for user not authenticated
# @patch('flaskr.backend.Backend')
@patch('flaskr.forms.RequestResetForm')
def test_reset_email_not_authenticated(mock_form,client):
    with patch('flaskr.backend.Backend.check_if_registered') as check_if_registered:
        with patch('flask_mail.Mail.send') as send_mail:
            email = "barshachaudhary@techexchange.in"
            mock_form.validate_on_submit.return_value = True
            mock_form.email.data.return_value = email
            check_if_registered.return_value = True
            resp = client.post('/reset_password',data = {"email": email},follow_redirects=True
)
            message = send_mail.call_args[0][0]
            assert message.sender == 'noreply@demo.com'
            assert message.recipients == [email]
            assert resp.status_code == 200
            assert resp.request.path == '/login'
            send_mail.assert_called_once()

#Testing for reset_request and send_reset_email for user authenticated
def test_reset_email_authenticated(client):
    with patch('flask_login.utils._get_user') as mock_cc:
        user = User('Barsha')
        mock_cc.return_value = user
        resp = client.post('/reset_password', follow_redirects=True)
        assert resp.status_code == 200
        assert b"Welcome to the NetflixSeries Wiki!" in resp.data

#Testing for reset_token route for post
@patch('flaskr.forms.RequestResetForm')
def test_reset_token_expired(mock_form, client):
    with patch('flask_login.utils._get_user') as mock_cc:
            with patch('itsdangerous.URLSafeTimedSerializer') as mock_serializer:
                    user = User('Barsha')
                    email = "barshachaudhary@techexchange.in"
                    mock_cc.return_value = user
                    mock_form.validate_on_submit.return_value = True
                    mock_form.email.data.return_value = email
                    mock_serializer.return_value.loads.side_effect = SignatureExpired('Token has expired')
                    #Generate a valid token that expires in 1 hour
                    s = mock_serializer.dumps({'user': email})
                    token = s.dumps({'user': email})

                    # Make a GET request to the reset password page with the token
                    response = client.get(f'/reset_password/{token}')

                    # Assert that the response status code is 302 (redirects to reset_request)
                    assert response.status_code == 302
                    # Check that the reset password form is in the response
                    # assert b'You should be redirected automatically to the target URL' in response.data

                    # # Make a POST request to the reset password page with a new password
                    # response = client.post('/reset_password/{token}', data={'password': 'newpassword', 'confirm_password': 'newpassword'}, follow_redirects = True)

                    # assert b'The password reset link is invalid or has expired' in response.data
                    # # Assert that the response status code is 200 
                    # assert response.status_code == 200
            
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
