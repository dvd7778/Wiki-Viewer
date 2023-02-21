from flask import render_template, redirect,url_for
from flask import request
from flask_login import login_user, current_user, logout_user, login_required
# from .forms import RegisterForm, LoginForm
def make_endpoints(app):

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    @app.route("/home")
    def home():
        return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route("/about")
    def about():
        return render_template('about.html', title = "About this page")

    @app.route("/register", methods = ['GET', 'POST'])
    def register():
        return render_template("register.html", title = "Sign Up")
    
    @app.route("/login", methods = ['GET','POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            if username == "wiki" and password == "wiki123":
                return redirect(url_for('home'))
            else:
                return render_template("login.html", title = "Login")
        return render_template("login.html", title = "Login")
        
    
    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for('home'))
    

    
