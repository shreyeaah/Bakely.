from app import db
from flask_login import UserMixin, current_user
from datetime import datetime

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
    logo = db.Column(db.String(120), nullable=True)
    banner = db.Column(db.String(120), nullable=True)
    instagram = db.Column(db.String(150), nullable=True)
    facebook = db.Column(db.String(150), nullable=True)
    

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(120))  # store image filename
    category = db.Column(db.String(50), nullable=True)

    baker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    baker = db.relationship('User', backref='menu_items')


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship('User', backref='cart_items')
    menu_item = db.relationship('MenuItem')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Keys
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    baker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=True)

    # Order Details
    quantity = db.Column(db.Integer, nullable=False, default=1)
    weight = db.Column(db.Float, nullable=True)
    shape = db.Column(db.String(20), nullable=True)
    tiers = db.Column(db.Integer, nullable=True)
    message = db.Column(db.Text, nullable=True)
    is_custom = db.Column(db.Boolean, default=False)


    delivery_mode = db.Column(db.String(20), nullable=False)
    payment_mode = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Pending')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='orders')
    baker = db.relationship('User', foreign_keys=[baker_id])
    menu_item = db.relationship('MenuItem', backref='orders')


class BakerPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baker_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    base_price_per_kg = db.Column(db.Float, nullable=False)
    extra_tier_price = db.Column(db.Float, nullable=False)

    frosting_prices = db.Column(db.JSON, default={})
    topper_prices = db.Column(db.JSON, default={})
    

    baker = db.relationship('User', backref='pricing', uselist=False)


