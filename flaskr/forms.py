"""
This will use all the forms for login and use the result from the forms.
"""

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_login import UserMixin,LoginManager

class RegisterForm(FlaskForm):
    # username = StringField('Username', validators= [DataRequired(), Length(min = 5, max= 20)])
    email = StringField('email', validators = [DataRequired()])
    password = PasswordField('password', validators = [DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('SignUp')

    # def vaildate_username(self, username):
    #     username = "Barsha"
    #     if username: 
    #         raise ValidationError("The username is taken!!")
    
    # def validate_email(self,email):
    #     user_email = "Barshachy@gmail.com"
    #     if user_email:
    #         raise ValidationError("This email is registered!!")
class LoginForm(FlaskForm):
    email = StringField('email', validators= [DataRequired()])
    password= PasswordField('password', validators = [DataRequired()])
    remember_user = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
