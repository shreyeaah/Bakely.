from flask import render_template, redirect, url_for, abort, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, bcrypt, login_manager
from models import User, BakerProfile, MenuItem, CartItem, Order
from forms import RegisterForm, LoginForm, ApproveForm, DeclineForm, MenuItemForm, OrderForm, BakerProfileForm
from werkzeug.utils import secure_filename
import os


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("validated")
        user = User.query.filter_by(username=form.username.data).first()

        print("User found:", user)
        if user:
            print("Approved:", user.is_approved)
            print("Role:", user.role)
            
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.role == 'baker' and not user.is_approved:
                return "Your account is pending approval. Please wait for admin approval.", 403
            login_user(user)

            if user.role == 'admin':
                return redirect(url_for('approve_bakers'))
            
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data,
                        password=hashed_password,
                        role=form.role.data)
        db.session.add(new_user)
        db.session.commit()

        if form.role.data == 'baker':
            profile = BakerProfile(
                user_id=new_user.id,
                bakery_name=form.bakery_name.data,
                phone=form.phone.data,
                address=form.address.data,
                description=form.description.data)
            
            db.session.add(profile)
            db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'baker':
        return redirect(url_for('baker_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('approve_bakers'))
    else:
        return redirect(url_for('customer_dashboard'))

@app.route('/baker_dashboard')
@login_required
def baker_dashboard():
    if current_user.role != 'baker':
        abort(403)

    # Get only this baker's items
    items = MenuItem.query.filter_by(baker_id=current_user.id).all()
    return render_template('baker_dashboard.html', items=items)

@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
     if current_user.role != 'customer':
        abort(403)
     
     search_place = request.args.get('place', '').strip().lower()

     query = User.query.filter_by(role='baker', is_approved=True)
     if search_place:
        query = query.join(User.baker_profile).filter(
            db.func.lower(BakerProfile.address).contains(search_place)
        )

     bakers = query.all()
     return render_template('customer_dashboard.html', bakers=bakers, place=search_place)


@app.route('/admin/approve_bakers')
@login_required
def approve_bakers():
    if current_user.role != 'admin':
        abort(403)
    # Fetch all bakers who are pending approval

    pending_bakers = User.query.filter_by(role='baker', is_approved=False).all()
    approve_form = ApproveForm()
    decline_form = DeclineForm()
    return render_template('approve_bakers.html', bakers=pending_bakers, approve_form=approve_form, decline_form=decline_form)

@app.route('/admin/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_baker(user_id):
    if current_user.role != 'admin':
        return "Access denied", 403

    baker = User.query.get_or_404(user_id)
    baker.is_approved = True
    db.session.commit()

    return redirect(url_for('approve_bakers'))
   
@app.route('/admin/decline/<int:user_id>', methods=['POST'])
@login_required
def decline_baker(user_id):
    if current_user.role != 'admin':
        abort(403)

    baker = User.query.get_or_404(user_id)

    # Optional: also delete associated profile
    if baker.baker_profile:
        db.session.delete(baker.baker_profile)

    db.session.delete(baker)
    db.session.commit()
    return redirect(url_for('approve_bakers'))

@app.route('/baker/add_item', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    if current_user.role != 'baker':
        abort(403)

    form = MenuItemForm()
    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(app.root_path, 'static/uploads', filename)
            form.image.data.save(image_path)

        item = MenuItem(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            image_filename=filename,
            baker_id=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash("Item added!", "success")
        return redirect(url_for('baker_dashboard'))  # or a page showing all items

    return render_template('add_menu_item.html', form=form)  

@app.route('/baker/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)

    # ✅ Ensure the item belongs to the current baker
    if item.baker_id != current_user.id:
        abort(403)

    form = MenuItemForm(obj=item)

    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.description = form.description.data

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(app.root_path, 'static/uploads', filename)
            form.image.data.save(image_path)
            item.image_filename = filename

        db.session.commit()
        flash('Item updated!', 'success')
        return redirect(url_for('baker_dashboard'))

    return render_template('edit_menu_item.html', form=form, item=item)

@app.route('/baker/delete_item/<int:item_id>', methods=['POST', 'GET'])
@login_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)

    # ✅ Secure multi-tenant delete
    if item.baker_id != current_user.id:
        abort(403)

    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.', 'info')
    return redirect(url_for('baker_dashboard'))

@app.route('/bakeries')
def list_bakeries():
    bakers = User.query.filter_by(role='baker', is_approved=True).all()
    return render_template('bakery_list.html', bakers=bakers)

@app.route('/bakery/<int:baker_id>')
def view_bakery(baker_id):
    baker = User.query.get_or_404(baker_id)
    if baker.role != 'baker' or not baker.is_approved:
        abort(404)
    menu_items = baker.menu_items  # via relationship
    return render_template('bakery_profile.html', baker=baker, menu_items=menu_items)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    if current_user.role != 'customer':
        abort(403)

    existing = CartItem.query.filter_by(user_id=current_user.id, menu_item_id=item_id).first()
    if existing:
        existing.quantity += 1
    else:
        new_item = CartItem(user_id=current_user.id, menu_item_id=item_id, quantity=1)
        db.session.add(new_item)

    db.session.commit()
    flash("Item added to cart.", "success")
    return redirect(request.referrer or url_for('customer_dashboard'))

@app.route('/cart')
@login_required
def view_cart():
    if current_user.role != 'customer':
        abort(403)

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.menu_item.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/order/<int:cart_item_id>', methods=['GET', 'POST'])
@login_required
def place_order_form(cart_item_id):
    if current_user.role != 'customer':
        abort(403)

    cart_item = CartItem.query.get_or_404(cart_item_id)
    form = OrderForm()

    if form.validate_on_submit():
        order = Order(
            customer_id=current_user.id,
            menu_item_id=cart_item.menu_item.id,
            baker_id=cart_item.menu_item.baker_id,
            quantity=cart_item.quantity,
            weight=form.weight.data,
            shape=form.shape.data,
            tiers=form.tiers.data,
            message=form.message.data,
            delivery_mode=form.delivery_mode.data,
            payment_mode=form.payment_mode.data,
            status="Pending"
        )
        db.session.add(order)
        db.session.delete(cart_item)
        db.session.commit()
        flash("Order placed!", "success")
        return redirect(url_for('view_cart'))

    return render_template('place_order.html', form=form, item=cart_item.menu_item)


@app.route('/baker/orders')
@login_required
def baker_orders():
    if current_user.role != 'baker':
        abort(403)

    # Fetch orders for this baker
    orders = Order.query.filter_by(baker_id=current_user.id).order_by(Order.created_at.desc()).all()

    return render_template('baker_order.html', orders=orders)

@app.route('/baker/order/<int:order_id>/accept', methods=['POST'])
@login_required
def accept_order(order_id):
    if current_user.role != 'baker':
        abort(403)

    order = Order.query.get_or_404(order_id)
    if order.baker_id != current_user.id:
        abort(403)

    order.status = 'Accepted'
    db.session.commit()
    flash('Order accepted.', 'success')
    return redirect(url_for('baker_orders'))

@app.route('/baker/order/<int:order_id>/decline', methods=['POST'])
@login_required
def decline_order(order_id):
    if current_user.role != 'baker':
        abort(403)

    order = Order.query.get_or_404(order_id)
    if order.baker_id != current_user.id:
        abort(403)

    order.status = 'Declined'
    db.session.commit()
    flash('Order declined.', 'info')
    return redirect(url_for('baker_orders'))


@app.route('/my_orders')
@login_required
def my_orders():
    if current_user.role != 'customer':
        abort(403)

    orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.id.desc()).all()
    return render_template('my_orders.html', orders=orders)

@app.route('/baker/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_baker_profile():
    if current_user.role != 'baker':
        abort(403)

    profile = current_user.baker_profile
    form = BakerProfileForm(obj=profile)

    if form.validate_on_submit():
        profile.bakery_name = form.bakery_name.data
        profile.phone = form.phone.data
        profile.address = form.address.data
        profile.description = form.description.data
        profile.instagram = form.instagram.data
        profile.facebook = form.facebook.data
        

        # Upload logo
        if form.logo.data:
            logo_filename = secure_filename(form.logo.data.filename)
            logo_path = os.path.join(app.root_path, 'static/uploads', logo_filename)
            form.logo.data.save(logo_path)
            profile.logo = logo_filename

        # Upload banner
        if form.banner.data:
            banner_filename = secure_filename(form.banner.data.filename)
            banner_path = os.path.join(app.root_path, 'static/uploads', banner_filename)
            form.banner.data.save(banner_path)
            profile.banner = banner_filename

        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for('baker_dashboard'))

    return render_template('edit_baker_profile.html', form=form)


@app.route('/baker/order/<int:order_id>/ready', methods=['POST'])
@login_required
def mark_ready(order_id):
    if current_user.role != 'baker':
        abort(403)

    order = Order.query.get_or_404(order_id)
    if order.baker_id != current_user.id:
        abort(403)

    order.status = 'Ready'
    db.session.commit()
    flash('Order marked as Ready.', 'success')
    return redirect(url_for('baker_orders'))


@app.route('/baker/order/<int:order_id>/delivered', methods=['POST'])
@login_required
def mark_delivered(order_id):
    if current_user.role != 'baker':
        abort(403)

    order = Order.query.get_or_404(order_id)
    if order.baker_id != current_user.id:
        abort(403)

    order.status = 'Delivered'
    db.session.commit()
    flash('Order marked as Delivered.', 'success')
    return redirect(url_for('baker_orders'))
