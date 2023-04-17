from flaskr import create_app
from unittest.mock import MagicMock
from unittest.mock import patch
from flask import request, render_template, redirect, url_for, flash, session
import pytest
from flask_wtf.csrf import generate_csrf
from flaskr.models import User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import datetime, timedelta
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
    assert b"Upload File to the Wiki" in resp.data
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
                    assert b'You should be redirected automatically to target URL: <a href="/reset_password">/reset_password</a>. If not click the link.' in response.data

                    # Make a POST request to the reset password page with a new password
                    response = client.post('/reset_password/{token}', data={'password': 'newpassword', 'confirm_password': 'newpassword'}, follow_redirects = True)

                    assert b'The password reset link is invalid or has expired' in response.data
                    # Assert that the response status code is 200 
                    assert response.status_code == 200
