"""
This will use all the forms for login and use the result from the forms.
"""

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_login import UserMixin,LoginManager
from wtforms import validators

class RegisterForm(FlaskForm):
    first_name = StringField('text', validators = [DataRequired()])
    last_name = StringField('text',validators = [DataRequired()])
    email = StringField('email', validators = [DataRequired()])
    password = PasswordField('password', validators = [DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('SignUp')

class LoginForm(FlaskForm):
    email = StringField('email', validators= [DataRequired()])
    password= PasswordField('password', validators = [DataRequired()])
    remember_user = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RequestResetForm(FlaskForm):
    email = StringField('email', [DataRequired("Please enter your email address."), Email("This field requires a valid email address")])
    submit  = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
    