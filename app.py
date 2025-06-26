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
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
from routes import *  # or import init_db if specific

@app.before_first_request
def initialize_app():
    import os
    from models import User
    from app import db, bcrypt  # ✅ Import bcrypt here

    # Ensure writable folder exists
    instance_path = os.path.join(os.getcwd(), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Create all tables
    db.create_all()

    # Auto-create admin if it doesn't exist
    existing_admin = User.query.filter_by(username='admin').first()
    if not existing_admin:
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")  # default fallback
        hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')  # ✅ Correct bcrypt usage
        admin = User(username='admin', password=hashed_pw, role='admin', is_approved=True)
        db.session.add(admin)
        db.session.commit()
