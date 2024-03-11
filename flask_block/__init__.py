# Import necessary modules and classes from Flask and extensions
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

# Create a Flask application instance
app = Flask(__name__)

# Configure the secret key for the Flask application
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

# Configure the URI for the SQLite database using the app's root path
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(os.path.dirname(app.root_path), 'flask_block', 'site.db')

# Create a SQLAlchemy database instance
db = SQLAlchemy(app)

# Create a Bcrypt instance for password hashing
bcrypt = Bcrypt(app)

# Create a LoginManager instance for managing user login sessions
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Configure the email server settings for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

# Create a Mail instance for sending emails
mail = Mail(app)

# Import routes module from the flask_block package
from flask_block import routes
