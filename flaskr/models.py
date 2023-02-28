from flask_login import LoginManager
from flask import Flask
app = Flask(__name__)
login_manager = LoginManager(app)


"""
I have to work on this one - Barsha
"""
@login_manager.user_loader
def load_user(user_id):
    return User.get_id(user_id)
    pass
class User():
    def is_authenticated(self):
        return True
    def get_id(self):
        return self.id
        
