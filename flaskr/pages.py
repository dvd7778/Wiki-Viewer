from flask import render_template, redirect, url_for, flash, send_file, request
from flask_login import login_user, current_user, logout_user, login_required
from flaskr.backend import Backend
from flaskr.forms import RegisterForm, LoginForm, ResetPasswordForm, RequestResetForm
import hashlib
from flaskr.models import User
import re
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import URLSafeTimedSerializer as Serializer
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
            genres = []
        else:
            genres = b.get_genres(filename)
        return render_template('parametrized_pages.html',
                               filename=filename,
                               text_lines=text_lines, 
                               genres=genres)

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
                first_name = info["first_name"]
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
    #This is profile route where user can change their profile     
    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        #check if user is authenticated
        if current_user.is_authenticated:
            #get username for current_user
            username = current_user.username
            #handle get request for the route
            if request.method == 'GET':
                #get profile img url 
                output = b.get_image_url(username)
                #if profile picture exists, render the profile page with profile picture
                if output:
                    return render_template('profile.html', profile_url=output, profile_picture=True)
                #if url does not exist, show default image as profile picture
                else:
                    flash('You need to upload your profile picture!')
                    return render_template('profile.html', title="Profile", profile_picture=False)
            
            #handle post request for the route
            if request.method == 'POST':
                #get the uploaded file from the request object
                try:
                    f = request.files['file']
                    #check if file was selected
                    if not f.filename:
                        flash('No file selected')
                        return redirect(url_for('profile'))
                    #upload file to the database (bucket)
                    b.upload_profile(f.filename, f.stream.read(), username)
                    flash("Profile Picture Changed!")
                except Exception as e:
                    flash(f"Upload failed: {e}")
                
                #redirect the user back to the profile page
                return redirect(url_for('profile'))
           
        #if not authenticated return user to the login 
        else:
            return redirect(url_for('login'))


    @app.route("/search", methods=["GET", "POST"])
    def search():
        # Do stuff here for the data
        if request.method == "POST":
            radio = request.form["choice"]
            query = request.form["search"]
            if radio == "Title":
                title_matches = b.title_search(query)

            elif radio == "Genre":
                title_matches = b.genre_search(query)
            # Have to make search_results html
            is_str = type(title_matches) == str
            return render_template('search_results.html',
                                   title="Search",
                                   results=title_matches,
                                   is_str=is_str,
                                   query=query)
        else:
            return render_template('search.html', title="Search")

    # Logins the user to the Flask
    @login_manager.user_loader
    def load_user(user_id):
        user = User(user_id)
        info = b.get_user_info(user_id)
        first_name = info["first_name"]
        last_name = info["last_name"]
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
        return render_template('upload.html', error=None) # error is None because it is used when a genre is not selected when uploading

    # Route for uploading files to the GCS bucket
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if request.method == 'POST':
            checkbox_names = ['genre_act', 'genre_adv', 'genre_anim', 'genre_com', 'genre_fant', 'genre_rom', 'genre_hor', 'genre_thr', 'genre_scifi', 'genre_drama']
            checked_genres = []
            for genre in checkbox_names: # stores all of the selected genres in the checked_genres list
                checked = request.form.get(genre)
                if checked:
                    checked_genres.append(checked)
            if not checked_genres:
                # There is an error because there was no genre selected when there should have
                return render_template('upload.html', error="No genres were selected. Please select at least one genre.")
            f = request.files['file']
            b.upload_genres(f.filename, checked_genres) # uploads the selected genres
            b.upload(f.filename, f.stream.read()) # uploads the selected file
            return 'file uploaded successfully'

    # Route for sending email with link to reset password
    def send_reset_email(user):
        # check if user is a valid email address
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'         
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='reset-password')
        token = s.dumps({'user': user})
        msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user])
        msg.body = f'''To reset your password visit the following link: 
            {url_for('reset_token', token=token, _external=True)}

            If you did not send the request to change your password, simply ignore this email.
            '''
        mail.send(msg)

    #Route for resetting user password via email
    @app.route('/reset_password',methods = ['POST', 'GET'])
    def reset_request():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        error = None
        form = RequestResetForm()
        if form.validate_on_submit() and request.method == "POST":
            user = form.email.data.lower()
            check_if_correct = b.check_if_registered(user)
            if check_if_correct:
                send_reset_email(user)
                flash('Password reset link sent to your email!')
                return redirect(url_for('login'))
            else:
                error = 'Your email is not registered'
                return render_template('reset_request.html',title = 'Reset Password', form = form, error = error )      
        return render_template('reset_request.html',title = 'Reset Password',form = form)
    
    #Route that links to page of reset password and send reset email confirmation  
    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_token(token):
        # Verify the token
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='reset-password')
        try:
            data = s.loads(token, max_age=86400)
        except:
            flash('The password reset link is invalid or has expired.')
            return redirect(url_for('reset_request'))

        # Get the user from the token        
        user = data['user']
        # Initialize the reset password form
        form = ResetPasswordForm()
        # Handle form submission
        if form.validate_on_submit() and request.method == 'POST':
            password = form.password.data
            check_if_reset = b.reset_password(user, password)
            if check_if_reset:
                # Redirect to the login page
                flash('Your password has been reset successfully. You can now log in.', 'success')
                return redirect(url_for('login'))
                # Send confirmation email
                msg = Message('Your password has been reset', sender='noreply@demo.com', recipients=[user])
                msg.body = f'''Your password for the WikiViewer has been reset successfully.'''
                mail.send(msg)
                
            else:
                flash('Password Reset Fails')
        return render_template('reset_token.html', title='Reset Password', form=form)
