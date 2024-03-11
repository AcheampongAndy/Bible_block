from datetime import datetime, timedelta, timezone
import jwt
from flask_block import app, db, login_manager
from flask_login import UserMixin

# Define a user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    with app.app_context():
        # Load user from the database using the provided user_id
        user = User.query.get(int(user_id))
    return user

# Define the User class, inheriting from db.Model and UserMixin
class User(db.Model, UserMixin):
    # Define user model fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='subquery')

    # Define a method to generate a JWT token for password reset
    def get_reset_token(self, expires_sec=1800):
        key = app.config['SECRET_KEY']
        encoded = jwt.encode(
            {"exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_sec), 
            "user_id": self.id},
            key,
            algorithm="HS256"
            )
        return encoded

    # Define a static method to verify a password reset token
    @staticmethod
    def verify_reset_token(token):
        key = app.config['SECRET_KEY']
        try:
            user_id = jwt.decode(token, key, algorithms="HS256")['user_id']
        except:
            return None
        with app.app_context():
            # Load and return the user associated with the decoded token
            return User.query.get(user_id)

    # Define a representation method for the User class
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# Define the Post class, inheriting from db.Model
class Post(db.Model):
    # Define post model fields
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Define a representation method for the Post class
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"
