"""
This will use all the forms for login and use the result from the forms.
"""

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Email
from flask_login import UserMixin, LoginManager


class RegisterForm(FlaskForm):
    first_name = StringField('text', validators=[DataRequired()])
    last_name = StringField('text', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    # confirm_password = PasswordField('Confirm Password', validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('SignUp')


class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_user = BooleanField('Remember Me')
    submit = SubmitField('Login')
