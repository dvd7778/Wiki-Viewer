from flask_login import LoginManager,UserMixin
from flask import Flask
"""
I have to work on this one - Barsha
"""

class User(UserMixin):
    def __init__(self,username, active = True):
        self.username = username
        self.active = active
    def getId(self):
        current_user = self.username
        return current_user
    def __str__(self):
        return "%s"%(self.username)
    def is_active(self):
        return self.active
    def __repr__(self):
        return f"User('{self.username}')"
    def is_authenticated(self):
        return True
    def logout_user(self):
        return False
        
    
        
