# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
from io import BytesIO

# Class for backend objects.
class Backend:

    def __init__(self):
        pass
    # Gets an uploaded page from the content bucket.  
    def get_wiki_page(self, filename):
        page_names = self.get_all_page_names()
        if filename in page_names:
            storage_client = storage.Client()
            bucket = storage_client.bucket('wiki_content')
            blob = bucket.get_blob(filename + ".txt")
            text = blob.download_as_string()
            text_str = str(text, "UTF-8")
            return text_str
        return None

    def get_all_page_names(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket('wiki_content')
        blobs = bucket.list_blobs()
        page_names = []
        for blob in blobs:
            if blob.name[:13] != "About Images/" and blob.name[-4:] != ".jpg" and blob.name[-4:] != ".png":
                page_names.append(blob.name[:-4])
        return page_names
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
    def get_image(self, image_file):
        storage_client = storage.Client()
        bucket = storage_client.bucket('wiki_content')
        blob = bucket.get_blob(image_file)
        with blob.open('rb') as f:
            return BytesIO(f.read())

b = Backend()
# b.upload('pages.py', 'Hello World!!')
#print(b.get_image('headshot.jpg'))

# b= Backend()
# b.sign_up('barsha',"Flask")
