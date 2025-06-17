from app import db
from flask_login import UserMixin, current_user

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable = False)
    is_approved = db.Column(db.Boolean, default=False)

    baker_profile = db.relationship('BakerProfile', backref='user', uselist=False, cascade="all, delete")
    
class BakerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bakery_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)

'''class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(120))  # store image filename
    baker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    baker = db.relationship('User', backref='menu_items')'''