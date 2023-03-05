from flask import render_template, redirect,url_for, flash, send_file
from flask import request
from flask_login import login_user, current_user, logout_user, login_required
from flaskr.backend import Backend
from flaskr.forms import RegisterForm, LoginForm
from .forms import RegisterForm, LoginForm
import hashlib
from PIL import Image
import base64
import io
from flaskr.models import User
#import imageio as iio
def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    @app.route("/main")
    def main():
        return render_template("main.html")

    @app.route("/home")
    def home():
        return render_template("home.html", title = "Home", data = "User")

    # TODO(Project 1): Implement additional routes according to the project requirements.
    @app.route("/pages")
    def pages():
        b = Backend()
        pages = b.get_all_page_names()
        return render_template('pages.html', title = "Wiki Pages", pages = pages)

    @app.route("/pages/<filename>")
    def parametrized_pages(filename):
        b = Backend()
        text_lines = b.get_wiki_page(filename)
        if not text_lines:
            return 'This page does not exist.'
        return render_template('parametrized_pages.html', filename = filename, text_lines = text_lines)
        
    @app.route("/about")
    def about():
        return render_template('about.html', title = "About this Wiki")

    @app.route('/get_image/<filename>')
    def retreive_image(filename):
        b = Backend()
        return send_file(b.get_image(filename), mimetype='image/jpeg')

    """
    This is the route for the registration page
    Passing the username and hashed-password to the sign-up method in Backend
    """
    @app.route("/register", methods = ['GET', 'POST'])
    def register(): 
        # if current_user.is_authenticated:
        #     return redirect(url_for('home'))
        form = RegisterForm()
        if form.validate_on_submit():
            username = form.email.data
            password = form.password.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            username = username.lower()
            hashed_password = hashlib.blake2b(password.encode()).hexdigest()
            b = Backend()
            message = b.sign_up(username,hashed_password,first_name,last_name)
            if message == "Username Taken!":
                flash(f"This username is taken")
                return render_template("register.html", title = "SignUp",form = form)
            flash(f"Your account has been created", 'success')
            return redirect(url_for('login'))
        return render_template("register.html", title = "SignUp",form = form)
    
    """
    This is the route for the login page
    Passing the username and password to the sign-in method in Backend
    """
    @app.route("/login", methods = ['GET','POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.email.data
            username_lower = username.lower()
            password = form.password.data
            b = Backend()
            check_if_correct = b.sign_in(username_lower,password)
            if check_if_correct:  
                flash('You have been logged in!', "success")
                user = User(username)
                userInfo = user.getId()
                info = b.get_user_info(userInfo)
                first_name = info["Firstname"]            
                return render_template('home.html', title = "Home", data = first_name )
            else:
                flash('Login Unsuccessful. Please check username and password', "danger")
        return render_template('login.html', title='Login', form=form)
    
    @app.route("/logout")
    def logout():
        flash("You have been logged out!","info")
        return redirect(url_for('login'))

    @app.route('/upload', methods= ['GET'])
    def upload_page():
        return render_template('upload.html')

    @app.route('/upload', methods= ['POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['file']
            b = Backend()
            b.upload(f.filename, f.stream.read())
            return 'file uploaded successfully'

    

    
