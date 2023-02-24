# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
class Backend:

    def __init__(self):
        pass
        
    def get_wiki_page(self, name):
        pass

    def get_all_page_names(self):
        pass

    def upload(self, filename, data):
        storage_client = storage.Client()
        bucket = storage_client.bucket('wiki_content')
        blob = bucket.blob(filename)
        with blob.open('wb') as f:
            f.write(data)

    def sign_up(self):
        pass

    def sign_in(self):
        pass

    def get_image(self, bucket_name, blob_name):
        pass

# b = Backend()
# b.upload('pages.py', 'Hello World!!')