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
    bucket.list_blobs.return_value = [blob]
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

def test_get_all_page_names_txt(file_stream, blob, bucket, storage_client): ########
    blob.name = "test_blob.txt"
    b = Backend(storage_client)
    pages = b.get_all_page_names()
    # assert storage_client.bucket().list_blobs()[0].name == "test_blob.txt"

    bucket.list_blobs.assert_called_once()
    assert "test_blob" in pages

def test_get_all_page_names_jpg(file_stream, blob, bucket, storage_client):
    blob.name.return_value = "test_blob.jpg"
    b = Backend(storage_client)
    pages = b.get_all_page_names()
    bucket.list_blobs.assert_called_once()
    assert len(pages) == 0

def test_get_wiki_page_working(file_stream, blob, bucket, storage_client): ########
    blob.name = "test.txt"
    file_stream.readlines.return_value = ["This", "is", "a", "test"]
    b = Backend(storage_client)
    b.get_all_page_names()
    text = b.get_wiki_page('test')
    bucket.get_blob.assert_called_with('test' + '.txt')
    blob.open.assert_called_once()
    print(text)
    # file_stream.readlines.assert_called_once()
    assert text == ["This", "is", "a", "test"]

def test_get_wiki_page_fail(file_stream, blob, bucket, storage_client):
    file_stream.readlines.return_value = ["This", "is", "a", "test"]
    b = Backend(storage_client)
    text = b.get_wiki_page('test')
    bucket.get_blob.assert_not_called()
    bucket.get_blob.open.readlines.assert_not_called()
    assert not text