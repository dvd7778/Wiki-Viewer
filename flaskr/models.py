from flask_login import LoginManager
from flask import Flask
app = Flask(__name__)
login_manager = LoginManager(app)

# @login_manager.user_loader
def load_user(user_id):
    #return User.get(user_id)
    pass
class User():
    pass
