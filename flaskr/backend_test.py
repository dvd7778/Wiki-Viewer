from flaskr.backend import Backend
from unittest.mock import MagicMock, patch
import unittest
import json
import pytest
import hashlib


#Testing for upload() and get_image()
@pytest.fixture
def file_stream():
    return MagicMock()


# Mocks the blob
@pytest.fixture
def blob(file_stream):
    blob = MagicMock()
    blob.open.return_value.__enter__.return_value = file_stream
    return blob


# Mocks the bucket
@pytest.fixture
def bucket(blob):
    bucket = MagicMock()
    bucket.blob.return_value = blob
    bucket.get_blob.return_value = blob
    bucket.list_blobs.return_value = [blob]
    return bucket


# Mocks the Google Cloud storage client
@pytest.fixture
def storage_client(bucket):
    storage_client = MagicMock()
    storage_client.bucket.return_value = bucket
    return storage_client


# Test for backend upload method
def test_upload(file_stream, blob, bucket, storage_client):
    b = Backend(storage_client)
    b.upload('test.txt', 'Hello World')
    bucket.blob.assert_called_with('test.txt')
    file_stream.write.assert_called_with('Hello World')

# Test for backend upload_genres method
def test_upload_genres(file_stream, blob, bucket, storage_client):
    file_stream.readlines.return_value = []
    b = Backend(storage_client)
    b.upload_genres('test.txt', ['Action', 'Horror', 'Science Fiction'])
    bucket.get_blob.assert_any_call('Action.txt')
    bucket.get_blob.assert_any_call('Horror.txt')
    bucket.get_blob.assert_called_with('Science Fiction.txt')
    file_stream.write.assert_called_with('test\n')

# Test for backend get_genres method when the blob contains the filename
def test_get_genres_containing(file_stream, blob, bucket, storage_client):
    file_stream.readlines.return_value = ["Wrong\n", "Name\n", "Test\n"]
    blob.name = "Horror.txt"
    b = Backend(storage_client)
    genres = b.get_genres("Test")
    bucket.list_blobs.assert_called_once()
    assert len(genres) == 1
    assert genres[0] == "Horror"

# Test for backend get_genres method when the blob does not contain the filename
def test_get_genres_missing(file_stream, blob, bucket, storage_client):
    file_stream.readlines.return_value = ["Wrong\n", "Name\n", "Bad_Test\n"]
    blob.name = "Horror.txt"
    b = Backend(storage_client)
    genres = b.get_genres("Test")
    bucket.list_blobs.assert_called_once()
    assert len(genres) == 0

def test_get_genres_no_blob(file_stream, blob, bucket, storage_client):
    bucket.list_blobs.return_value = []
    b = Backend(storage_client)
    genres = b.get_genres("Test")
    bucket.list_blobs.assert_called_once()
    assert len(genres) == 0

# Test for backend get_image method
def test_get_image(file_stream, blob, bucket, storage_client):
    file_stream.read.return_value = b'Image data'
    b = Backend(storage_client)
    b.get_image('test.png')
    bucket.get_blob.assert_called_with('test.png')
    file_stream.read.assert_called_once()


# Tests the get_all_page_names Backend method when the blob is a text file
def test_get_all_page_names_txt(file_stream, blob, bucket, storage_client):
    blob.name = "test_blob.txt"
    b = Backend(storage_client)
    pages = b.get_all_page_names()
    bucket.list_blobs.assert_called_once()
    assert "test_blob" in pages


# Tests the get_all_page_names Backend method when the blob is a jpg file
def test_get_all_page_names_jpg(file_stream, blob, bucket, storage_client):
    blob.name.return_value = "test_blob.jpg"
    b = Backend(storage_client)
    pages = b.get_all_page_names()
    bucket.list_blobs.assert_called_once()
    assert len(pages) == 0


# Test for a successful get_wiki_page backend method.
def test_get_wiki_page_working(file_stream, blob, bucket, storage_client):
    blob.name = "test.txt"
    file_stream.readlines.return_value = ["This", "is", "a", "test"]
    blob.open.return_value = file_stream
    b = Backend(storage_client)
    b.get_all_page_names()
    text = b.get_wiki_page('test')
    bucket.get_blob.assert_called_with('test' + '.txt')
    blob.open.assert_called_once()
    file_stream.readlines.assert_called_once()
    assert text == ["This", "is", "a", "test"]


# Test for an unsucessful get_wiki_page backend method.
def test_get_wiki_page_fail(file_stream, blob, bucket, storage_client):
    file_stream.readlines.return_value = ["This", "is", "a", "test"]
    blob.open.return_value = file_stream
    b = Backend(storage_client)
    text = b.get_wiki_page('test')
    bucket.get_blob.assert_not_called()
    bucket.get_blob.open.readlines.assert_not_called()
    assert not text


"""
Testing for sign_up(), sign_in(), hash_password() and test_get_user_info() method starts from here:
I have used fixture to set expected output and input value that I get from the bucket.
"""


#json_value that will be stored inside the bucket if each file to store user_info
@pytest.fixture
def user_info():
    return {
        "username": "barsha@gmail.com",
        "password": "pa$$word",
        "first_name": "Barsha",
        "last_name": "Chaudhary"
    }


#username from the json that is passed to the bucket
@pytest.fixture
#will be used in sign_up_test
def user_name(user_info):
    return user_info["username"]


#user_password from the json that is passed to the bucket
#will be used in sign_up_test
@pytest.fixture
def user_password(user_info):
    return user_info["password"]


#user_first_name from the json that is passed to the bucket
#will be used in sign_up_test
@pytest.fixture
def user_first_name(user_info):
    return user_info["first_name"]


#user_last_name from the json that is passed to the bucket
#will be used in sign_up_test
@pytest.fixture
def user_last_name(user_info):
    return user_info["last_name"]


#test for the sign_up when user email is already taken
def test_sign_up(storage_client, blob, bucket, user_name, user_password,
                 user_first_name, user_last_name):
    b = Backend(storage_client)
    output = b.sign_up(user_name, user_password, user_first_name,
                       user_last_name)
    assert output == "Username Taken!"


#test for sign for the new users who are yet to register
def test_sign_up_new_user(storage_client, blob, bucket, user_name,
                          user_password, user_first_name, user_last_name,
                          user_info):
    with patch('google.cloud.storage.Blob') as storage_blob:
        storage_blob.return_value.exists.return_value = False
        b = Backend(storage_client)
        b.sign_up(user_name, user_password, user_first_name, user_last_name)
        bucket.blob.assert_called_with(user_name + ".txt")
        blob.upload_from_string.assert_called_with(json.dumps(user_info))


#testing for the hash_password()
def test_hash_password(storage_client, user_password):
    b = Backend(storage_client)
    hashed_password = b.hash_password(user_password)
    assert hashed_password == '4b787f1b2774c29601d145fb70becb6c0d507a624eca769d1e85bc5ffbf33ed89a1c5f848444a286f5f639412129441ff58a0d657cbd56423d02c6d97985494a'


#testing when the sign in fails
def test_sign_in_fail(storage_client, blob, bucket, user_name, user_password):
    with patch('google.cloud.storage.Blob') as storage_blob:
        storage_blob.return_value.exists.return_value = False
        b = Backend(storage_client)
        check_sign_in = b.sign_in(user_name, user_password)
        assert check_sign_in == False


#fixture that returns the data that is expected from the files inside the bucket
#blobs are storing the file content in the string form as the files are of txt format
#used in test_sign_in and test_user_info
@pytest.fixture
def user_info_json_loads():
    stored_info = '{"username": "barsha@gmail.com", "password": "pa$$word", "first_name": "Barsha", "last_name": "Chaudhary"}'
    return stored_info


#testing for the sucessful login when the password entered matches
def test_sign_in_success(storage_client, blob, bucket, user_name, user_password,
                         user_info_json_loads, user_info):
    with patch('google.cloud.storage.Blob') as storage_blob:
        storage_blob.return_value.exists.return_value = True
        blob.download_as_text.return_value = user_info_json_loads
        b = Backend(storage_client)
        b.sign_in(user_name, user_password)
        bucket.blob.assert_called_with(user_name + ".txt")
        json_output = json.loads(blob.download_as_text())
        assert user_info["password"] == json_output["password"]


#testing to get general info [firstname and lastname] about the user
def test_get_user_info(storage_client, blob, bucket, user_name, user_password,
                       user_info_json_loads, user_info):
    blob.download_as_text.return_value = user_info_json_loads
    json_output = json.loads(blob.download_as_text())
    b = Backend(storage_client)
    output = b.get_user_info(user_name)
    bucket.blob.assert_called_with(user_name + ".txt")
    assert json_output["first_name"] == output["Firstname"]
    assert json_output["last_name"] == output["Secondname"]
    assert output == {"Firstname": "Barsha","Secondname": "Chaudhary"}

#testing if the function is checking if the user is registered or not
def test_check_if_registered(storage_client,blob,bucket,user_name):
    with patch('google.cloud.storage.Blob') as storage_blob:
        #case when user is registered
        storage_blob.return_value.exists.return_value = True
        b = Backend(storage_client)
        output = b.check_if_registered(user_name)
        assert output == True

        #case when user is not registered
        storage_blob.return_value.exists.return_value = False
        b = Backend(storage_client)
        output = b.check_if_registered(user_name)
        assert output == False


