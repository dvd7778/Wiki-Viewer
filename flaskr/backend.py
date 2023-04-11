# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
from io import BytesIO
from flaskr import pages
import json
import secrets 
import os

# Class for backend objects.
class Backend:
    # Backend class constructor
    def __init__(self, storage_client=storage.Client()):
        self.storage_client = storage_client
        self.content_bucket = storage_client.bucket('wiki_content')
        self.userInfo_bucket = storage_client.bucket('users-passwords')
        self.userProfile_bucket = storage_client.bucket('user-profile-pictures-wiki')
        self.page_names = []

    # Gets an uploaded page from the content bucket.
    # Parameter: filename - a string with the name of the file you want to get
    # Returns: text - a list of strings with the contents of the file you are getting
    #          None - returns None when the file is not in the bucket
    def get_wiki_page(self, filename):
        if filename in self.page_names:
            blob = self.content_bucket.get_blob(filename + ".txt")
            file = blob.open()
            text = file.readlines()
            return text
        return None

    # Gets the name of all of the text files in the content bucket
    # Return: self.page_names - a list with the names of all the text files in the bucket
    def get_all_page_names(self):
        blobs = self.content_bucket.list_blobs()
        self.page_names.clear()
        for blob in blobs:
            if blob.name[-4:] == ".txt":  # Checks if the blob is a text file
                self.page_names.append(blob.name[:-4])
        return self.page_names

    # Adds data to the content bucket.
    def upload(self, filename, data):
        blob = self.content_bucket.blob(filename)
        with blob.open('wb') as f:
            f.write(data)

    #It stores password inside the file which named after each username in the gcs bucket.
    def sign_up(self, username, password, first_name, last_name):
        filename = username + ".txt"
        stats = storage.Blob(bucket=self.userInfo_bucket,
                             name=filename).exists(self.storage_client)
        if stats:
            return "Username Taken!"
        blob = self.userInfo_bucket.blob(filename)
        data = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
        blob.upload_from_string(json.dumps(data))

    #It checks for the username by name of the file if it exists and then proceeds to check user credential inside the file.
    #If it matches, lets the user login else does not.
    def sign_in(self, username, password):
        filename = username + ".txt"
        blob = self.userInfo_bucket.blob(filename)
        stats = storage.Blob(bucket=self.userInfo_bucket,
                             name=filename).exists(self.storage_client)
        if stats:
            entered_password = self.hash_password(password)
            stored_info = blob.download_as_text()
            info = json.loads(stored_info)
            stored_password = info["password"]
            if entered_password == stored_password:
                return True
        return False

    #This method hashes password
    def hash_password(self, password):
        return hashlib.blake2b(password.encode()).hexdigest()

    #Input: userId
    #Returns: User Information except Password
    def get_user_info(self, username):
        information = dict()
        filename = str(username) + ".txt"
        blob = self.userInfo_bucket.blob(filename)
        stored_info = blob.download_as_text()
        info = json.loads(stored_info)
        information["Firstname"] = info["first_name"]
        information["Secondname"] = info["last_name"]
        information["email"] = info["username"]
        return information

    # Gets an image from the content bucket.
    def get_image(self, image_file):
        blob = self.content_bucket.get_blob(image_file)
        with blob.open('rb') as f:
            return BytesIO(f.read())

    # Gets an image from the userProfile bucket
    def get_profile_img(self, image_file):
        blob = self.userProfile_bucket.get_blob(image_file)
        with blob.open('rb') as f:
            return BytesIO(f.read())

    # Gets image url for a image from the userprofile bucket
    # returns None if user has not uploaded any profile picture.
    def get_image_url(self, user_name):
        blobs = list(self.userProfile_bucket.list_blobs(prefix=user_name))
        for blob in blobs:
            if os.path.splitext(blob.name)[0] == user_name:
                return f"/get_profile_img/{blob.name}"
        return None

    # Adds profile picture to the profileImage bucket.
    def upload_profile(self, filename, data, user_name):
        blobs = list(self.userProfile_bucket.list_blobs(prefix=user_name))
        if blobs:
            for blob in blobs:
                if os.path.splitext(blob.name)[0] == user_name:
                    filename_to_remove = user_name + os.path.splitext(blob.name)[-1]
                    blob_to_remove = self.userProfile_bucket.blob(filename_to_remove)
                    blob_to_remove.delete()
        file_info = filename.split('.')
        filename = f"{user_name}.{file_info[-1]}"
        blob = self.userProfile_bucket.blob(filename)
        with blob.open('wb') as f:
            f.write(data)

