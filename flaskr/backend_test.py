from flaskr.backend import Backend
from unittest.mock import MagicMock
import pytest

# TODO(Project 1): Write tests for Backend methods.
@pytest.fixture
def file_stream():
    return MagicMock()

@pytest.fixture
def blob(file_stream):
    blob = MagicMock()
    blob.open.return_value.__enter__.return_value = file_stream
    return blob

@pytest.fixture
def bucket(blob):
    bucket = MagicMock()
    bucket.blob.return_value = blob
    bucket.get_blob.return_value = blob
    return bucket

@pytest.fixture
def storage_client(bucket):
    storage_client = MagicMock()
    storage_client.bucket.return_value = bucket
    return storage_client

def test_upload(file_stream, blob, bucket, storage_client):
    b = Backend(storage_client)
    b.upload('test.txt', 'Hello World')
    bucket.blob.assert_called_with('test.txt')
    file_stream.write.assert_called_with('Hello World')

def test_get_image(file_stream, blob, bucket, storage_client):
    file_stream.read.return_value = b'Image data'
    b = Backend(storage_client)
    b.get_image('test.png')
    bucket.get_blob.assert_called_with('test.png')
    file_stream.read.assert_called_once()