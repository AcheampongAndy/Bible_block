from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = 'b7736b7af313ca79ca4a62ba539f1871'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(os.path.dirname(app.root_path), 'flask_block', 'site.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from flask_block import routes
