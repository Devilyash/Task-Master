from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

mysqluser=os.environ.get('MYSQL_USER')
mysqlpass=os.environ.get('MYSQL_PASS')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{mysqluser}:{mysqlpass}@localhost/task_master'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  
# app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('DB_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('DB_PASS')

mail = Mail(app)

from task_manager import routes