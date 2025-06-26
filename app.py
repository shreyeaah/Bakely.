from dotenv import load_dotenv
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

load_dotenv()
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

BASE_DIR = os.getcwd()
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'donkeyflyspillflower'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'




from routes import *  