"""
This will use all the forms for login and use the result from the forms.
"""

from flask import request
#flask-wtf not working
# from flask-wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField

# class RegisterForm(FlaskForm):
#     username = StringField('Username', validators= [DataRequired(), Length(min = 5, max= 20)])
#     email = StringField('Email', validators = [DataRequired(),Email()])
#     password = PasswordField('Password', validators = [DataRequired()])
#     submit = SubmitField('Sign Up')

#     def vaildate_username(self, username):
#         username = "Barsha"
#         if username: 
#             raise ValidationError("The username is taken!!")
    
#     def validate_email(self,email):
#         user_email = "Barshachy@gmail.com"
#         if user_email:
#             raise ValidationError("This email is registered!!")
# class LoginForm(FlaskForm):
#     user_email = StringField('Email', validators= [DataRequired(), Length(min = 5, max= 20)])
#     password= PasswordField('Password', validators = [DataRequired()])
#     remember_user = BooleanField('Remember Me')
#     submit = SubmitField('Login')