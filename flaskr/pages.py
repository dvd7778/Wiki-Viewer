from flask import render_template, redirect, url_for, flash, send_file
from flask import request
from flask_login import login_user, current_user, logout_user, login_required
from flaskr.backend import Backend
from flaskr.forms import RegisterForm, LoginForm
from flaskr.forms import RegisterForm, LoginForm, ResetPasswordForm, RequestResetForm
import hashlib
from flaskr.models import User
import re
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import render_template_string
from flask import render_template_string, url_for
from itsdangerous import URLSafeTimedSerializer

def make_endpoints(app, login_manager,mail):
    b = Backend()
    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    @app.route("/home")
    def home():
        return render_template("main.html", title="Home", data="User")

    """
    This is the pages route which will display a list of all the pages uploaded to the content bucket, 
    and if a page is clicked then it will call the parametrized route for the clicked page.
    """

    @app.route("/pages")
    def pages():
        pages = b.get_all_page_names()
        return render_template('pages.html', title="Wiki Pages", pages=pages)

    """
    This is a parametrized route.
    It passes a filename as a parameter and renders a page that says "Page not found." if the page isn't uploaded,
    and if it has been uploaded, it renders a page with the title and the text file's contents.
    """

    @app.route("/pages/<filename>")
    def parametrized_pages(filename):
        text_lines = b.get_wiki_page(filename)
        if not text_lines:
            filename = "Page not found."
            text_lines = []
        return render_template('parametrized_pages.html',
                               filename=filename,
                               text_lines=text_lines)

    # Route for the about page of the wiki
    @app.route("/about")
    def about():
        return render_template('about.html', title="About this Wiki")

    # Route used to get an image
    @app.route('/get_image/<filename>')
    def retreive_image(filename):
        return send_file(b.get_image(filename), mimetype='image/jpg')
    
   # Route used to get an image
    @app.route('/get_profile_img/<filename>')
    def retreive_profile_image(filename):
        return send_file(b.get_profile_img(filename), mimetype='image/jpg')
    

    """
    This is the route for the registration page
    Passing the username and hashed-password to the sign-up method in Backend
    """

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegisterForm()
        if form.validate_on_submit():
            username = form.email.data
            password = form.password.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            username = username.lower()
            hashed_password = b.hash_password(password)
            message = b.sign_up(username, hashed_password, first_name,
                                last_name)
            if message == "Username Taken!":
                flash(f"This Email is already Registered!")
                return render_template("register.html",
                                       title="SignUp",
                                       form=form)
            flash(f"Your account has been created", 'success')
            flash(f"Please login to continue", 'info')
            return redirect(url_for('login'))
        return render_template("register.html", title="SignUp", form=form)

    """
    This is the route for the login page
    Passing the username and password to the sign-in method in Backend
    """

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        error = None
        if form.validate_on_submit() and request.method == "POST":
            username = form.email.data.lower()
            password = form.password.data
            check_if_correct = b.sign_in(username, password)
            if check_if_correct:
                flash('You have successfully logged in!')
                user = User(username)
                userInfo = user.get_id()
                info = b.get_user_info(userInfo)
                first_name = info["Firstname"]
                user.set_name(first_name)
                login_user(user)
                return render_template('main.html',
                                       title="Home",
                                       data=first_name)
            else:
                error = 'Login Unsuccessful! Please check your username and password again!'
        return render_template('login.html',
                               title='Login',
                               form=form,
                               error=error)
    # @login_required
    # @app.route("/profile", methods = ["GET", "POST"])
    # def profile():
    #     username = current_user.username
    #     if request.method == 'GET':
    #         output = b.get_image_url(username)
    #         if output is None:
    #             flash('You need to upload your profile picture!')                
    #             return render_template('profile.html', title="Profile", profile_picture = False)
    #         return render_template('profile.html', profile_url = output, profile_picture = True )
    #     if request.method == 'POST':
    #         f = request.files['file']
    #         if f.filename == '':
    #             flash('No file selected')
    #             output = b.get_image_url(username)
    #             if not output:
    #                 return render_template('profile.html', title="Profile", profile_picture = False)
    #             return render_template('profile.html', profile_url = output, profile_picture = True )
    #         if f:
    #             b.upload_profile(f.filename, f.stream.read(),username)
    #             output = b.get_image_url(username)
    #             flash("Profile Picture Changed!")
    #             return render_template('profile.html', profile_url = output, profile_picture = True)
    #     return render_template('profile.html', title="Profile", profile_picture = False)          

    @login_required
    @app.route("/profile", methods = ["GET", "POST"])
    def profile():
        if current_user.is_authenticated:
            username = current_user.username
            if request.method == 'GET':
                output = b.get_image_url(username)
                if output:
                    return render_template('profile.html', profile_url=output, profile_picture=True)
                else:
                    flash('You need to upload your profile picture!')
                    return render_template('profile.html', title="Profile", profile_picture=False)
            
            if request.method == 'POST':
                try:
                    f = request.files['file']
                    if not f.filename:
                        flash('No file selected')
                        return redirect(url_for('profile'))
                    b.upload_profile(f.filename, f.stream.read(), username)
                    flash("Profile Picture Changed!")
                except Exception as e:
                    flash(f"Upload failed: {e}")
                
                return redirect(url_for('profile'))
            
            return render_template('profile.html', title="Profile", profile_picture=False)
        else:
            return redirect(url_for('login'))


    @app.route("/search", methods = ["GET", "POST"])
    def search():
        return render_template('search.html', title="Search")


    # Logins the user to the Flask
    @login_manager.user_loader
    def load_user(user_id):
        user = User(user_id)
        info = b.get_user_info(user_id)
        first_name = info["Firstname"]
        last_name = info["Secondname"]
        email = info["email"]
        user.set_name(first_name)
        user.set_last_name(last_name)
        user.set_email(email)
        login_user(user)
        return user

    # Logouts the user from Flask
    @app.route("/logout")
    def logout():
        logout_user()
        flash("You have been logged out!", "info")
        flash(" Do you want to login again?")
        return redirect(url_for('login'))

    # Returns html for upload
    @app.route('/upload', methods=['GET'])
    def upload_page():
        return render_template('upload.html')

    # Route for uploading files to the GCS bucket
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if request.method == 'POST':
            f = request.files['file']
            b.upload(f.filename, f.stream.read())
            return 'file uploaded successfully'

   