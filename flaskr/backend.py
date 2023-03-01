# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib

# Class for backend objects.
class Backend:

    def __init__(self):
        pass
    # Gets an uploaded page from the content bucket.  
    def get_wiki_page(self, name):
        pass
    # Gets the names of all pages from the content bucket.
    def get_all_page_names(self):
        pass
    # Adds data to the content bucket.
    def upload(self, filename, data):
        storage_client = storage.Client()
        bucket = storage_client.bucket('wiki_content')
        blob = bucket.blob(filename)
        with blob.open('wb') as f:
            f.write(data)

    """
    It stores password inside the file which named after each username in the gcs bucket. 
    """
    def sign_up(self,file_userInfo,data):
        storage_client = storage.Client()
        bucket_userInfo = storage_client.bucket('users-passwords')
        filename = file_userInfo + ".txt"
        stats = storage.Blob(bucket = bucket_userInfo, name = filename).exists(storage_client)
        if not stats:
            blob = bucket_userInfo.blob(filename)
            blob.upload_from_string(data)
        return "Username Taken!"
    """
    It checks for the username by name of the file if it exists and then proceeds to check user credential inside the file.
    If it matches, lets the user login else does not.
    """
    def sign_in(self,username,password):
        storage_client = storage.Client()
        bucket_name = storage_client.bucket('users-passwords')
        filename = username + ".txt"
        blob = bucket_name.blob(filename)
        stats = storage.Blob(bucket = bucket_name, name = filename).exists(storage_client)
        if stats: 
            entered_password = hashlib.blake2b(password.encode()).hexdigest()
            stored_password = blob.download_as_text()
            if entered_password == stored_password:
                return True
        return False
    # Gets an image from the content bucket.
    def get_image(self, bucket_name, blob_name):
        pass

# b = Backend()
# b.upload('pages.py', 'Hello World!!')

# b= Backend()
# b.sign_up('barsha',"Flask")
