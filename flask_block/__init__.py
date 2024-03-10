import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config["SECRET_KEY"] = 'b7736b7af313ca79ca4a62ba539f1871'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(os.path.dirname(app.root_path), 'flask_block', 'site.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['SECURITY_PASSWORD_SALT'] = '3cc8971d26f9e380a583ebc75423e18b'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'noreplydemo907@gmail.com'
app.config['MAIL_PASSWORD'] = 'nbqa qeyx rrzx sioy'
mail = Mail(app)





from flask_block import routes
