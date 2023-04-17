# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage
import hashlib
from io import BytesIO
#from flaskr import pages 
import json
import difflib
import os


# Class for backend objects.
class Backend:
    # Backend class constructor
    def __init__(self, storage_client=storage.Client()):
        self.storage_client = storage_client
        self.content_bucket = storage_client.bucket('wiki_content')
        self.userInfo_bucket = storage_client.bucket('users-passwords')
        self.show_genre_bucket = storage_client.bucket('show-genres')
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
        return information

    # Gets an image from the content bucket.
    def get_image(self, image_file):
        blob = self.content_bucket.get_blob(image_file)
        with blob.open('rb') as f:
            return BytesIO(f.read())

    # Gets the corresponding titles from a title search.
    def title_search(self, query):  
        shows = self.get_all_page_names()
        matches = difflib.get_close_matches(str(query), shows, n=5, cutoff=0.5)
        if not matches:
            return "No title matches found for " + "'" + str(query) + "'"
        return matches

    # Gets the corresponding titles from a genre search.
    def genre_search(self, query):  
        # Checks correct type
        if not isinstance(query, str):
            return 'No genre matches found for ' + "'" + str(query) + "'"
        matches = set()
        queries = query.split(',')
        genres = [
            'action', 'adventure', 'animation', 'thriller', 'comedy', 'drama',
            'romance', 'science fiction', 'fantasy'
        ]
        bad_queries = [] # Any queries that don't match a genre
        for genre in queries:
            if genre.strip().lower() not in genres:
                bad_queries.append(genre)
        # Checks if all queries are bad
        if len(bad_queries) == len(queries):
            return 'No genre matches found for ' + "'" + query + "'"
        # Removes any bad queries
        for query in queries:
            if query in bad_queries:
                queries.remove(query)
    
        for genre in queries:
            blob = self.show_genre_bucket.blob(genre.strip().capitalize() +
                                               '.txt')
            f = blob.open()
            content = f.readlines()
            for show in content:
                matches.add(show.strip())
        # Checks if there are no matches
        if not matches:
            return 'No shows for ' + "'" + query + "'" + ' yet'
        return matches




    #check if user is registered
    def check_if_registered(self,user):
        filename = user + ".txt"
        stats = storage.Blob(bucket = self.userInfo_bucket, name = filename).exists(self.storage_client)
        if stats:
            return True
        else:
            return False
            
    #reset password for the user through forget password feature
    def reset_password(self,username,password):
        filename = username + ".txt"
        blob = self.userInfo_bucket.blob(filename)
        stats = storage.Blob(bucket = self.userInfo_bucket, name = filename).exists(self.storage_client)
        if stats:
            entered_password = self.hash_password(password)
            stored_info = blob.download_as_text()
            data = json.loads(stored_info)
            data["password"] = entered_password
            blob.upload_from_string(json.dumps(data))
            return True
        else:
            return False

