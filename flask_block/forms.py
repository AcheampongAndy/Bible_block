# Import necessary modules and classes from Flask and WTForms
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_block.modules import User
from flask_block import db, app

# Define a registration form for user sign up
class RegistrationForm(FlaskForm):
    # Username input field with validation
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Email input field with validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Password input field with validation
    password = PasswordField('Password', validators=[DataRequired()])
    # Confirm Password input field with validation, ensuring it matches the password
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Submit button for the form
    submit = SubmitField('Sign Up')

    # Function to validate unique username
    def validate_username(self, username):
        # Check if the username is already in the database
        with app.app_context():
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    # Function to validate unique email
    def validate_email(self, email):
        # Check if the email is already in the database
        with app.app_context():
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


# Define a login form for user login
class LoginForm(FlaskForm):
    # Username input field with validation
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Password input field with validation
    password = PasswordField('Password', validators=[DataRequired()])
    # Remember Me checkbox
    remember = BooleanField('Remember Me')
    # Submit button for the form
    submit = SubmitField('Login')


# Define a form for updating user account information
class UpdateAccountForm(FlaskForm):
    # Username input field with validation
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Email input field with validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    # File input field for updating profile picture with allowed file types
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    # Submit button for the form
    submit = SubmitField('Update')

    # Function to validate unique username, excluding the current user's username
    def validate_username(self, username):
        if username.data != current_user.username:
            # Check if the username is already in the database
            with app.app_context():
                user = User.query.filter_by(username=username.data).first()
                if user:
                    raise ValidationError('That username is taken. Please choose a different one.')

    # Function to validate unique email, excluding the current user's email
    def validate_email(self, email):
        if email.data != current_user.email:
            # Check if the email is already in the database
            with app.app_context():
                user = User.query.filter_by(email=email.data).first()
                if user:
                    raise ValidationError('That email is taken. Please choose a different one.')


# Define a form for creating posts
class PostForm(FlaskForm):
    # Title input field with validation
    title = StringField('Title', validators=[DataRequired()])
    # Content input field with validation
    content = TextAreaField('Content', validators=[DataRequired()])
    # Submit button for the form
    submit = SubmitField('Post')


# Define a form for requesting a password reset
class RequestResetForm(FlaskForm):
    # Email input field with validation
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Submit button for the form
    submit = SubmitField('Request Password Reset')

    # Function to validate existence of the email in the database
    def validate_email(self, email):
        # Check if the email is in the database
        with app.app_context():
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                raise ValidationError('There is no account with that email. You must register first.')


# Define a form for resetting the password
class ResetPasswordForm(FlaskForm):
    # Password input field with validation
    password = PasswordField('Password', validators=[DataRequired()])
    # Confirm Password input field with validation, ensuring it matches the password
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Submit button for the form
    submit = SubmitField('Reset Password')
