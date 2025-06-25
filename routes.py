from flask import render_template, redirect, url_for, abort, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, bcrypt, login_manager
from models import User, BakerProfile, MenuItem, CartItem, Order, BakerPricing
from forms import RegisterForm, LoginForm, ApproveForm, DeclineForm, MenuItemForm, OrderForm, BakerProfileForm, BakerPricingForm
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func
import requests
from dotenv import load_dotenv
import base64


STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
@app.route('/init-db')
def init_db():
    db.create_all()
    return " Database initialized!"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/create-admin')
def create_admin():
    from models import User
    from app import db
    from werkzeug.security import generate_password_hash

    hashed_pw = generate_password_hash("admin123", method='sha256')
    admin = User(username='admin', password=hashed_pw, role='admin', is_approved=True)
    db.session.add(admin)
    db.session.commit()
    return "Admin user created!"

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
            category=form.category.data.strip().lower(),
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

    if item.baker_id != current_user.id:
        abort(403)

    form = MenuItemForm(obj=item)

    if form.validate_on_submit():
        print("✅ Form validated")

        item.name = form.name.data
        item.price = form.price.data
        item.description = form.description.data
        item.category = form.category.data.strip().lower()

        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(app.root_path, 'static/uploads', filename)
            form.image.data.save(image_path)
            item.image_filename = filename

        db.session.commit()
        flash('Item updated!', 'success')
        return redirect(url_for('baker_dashboard'))
    
    # 👇 Add these lines to debug
    print("Form not validated")
    print("Form submitted:", form.is_submitted())
    print("Form errors:", form.errors)

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
    return redirect( url_for('baker_orders'))

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
    return redirect( url_for('baker_orders'))


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
        if form.logo.data and hasattr(form.logo.data, 'filename'):
            logo_filename = secure_filename(form.logo.data.filename)
            logo_path = os.path.join(app.root_path, 'static/uploads', logo_filename)
            form.logo.data.save(logo_path)
            profile.logo = logo_filename

        # Upload banner
        if form.banner.data and hasattr(form.banner.data, 'filename'):
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

@app.route('/baker/<int:baker_id>/custom-order-form')
def custom_order_form(baker_id):
    baker = User.query.get_or_404(baker_id)
    if baker.role != 'baker' or not baker.is_approved:
        abort(404)

    cake_types = MenuItem.query.filter_by(baker_id=baker_id, category='cake').all()
    pricing_model = BakerPricing.query.filter_by(baker_id=baker_id).first()

    # ✅ Convert to dict to make it JSON serializable
    pricing = {
        'base_price_per_kg': pricing_model.base_price_per_kg if pricing_model else 0,
        'extra_tier_price': pricing_model.extra_tier_price if pricing_model else 0,
        'frosting_prices': pricing_model.frosting_prices if pricing_model else {},
        'topper_prices': pricing_model.topper_prices if pricing_model else {},
    }

    return render_template(
        'custom_order_form.html',
        baker=baker,
        cake_types=cake_types,
        pricing=pricing  # ✅ now safe to use with `| tojson`
    )



@app.route('/baker/set-pricing', methods=['GET', 'POST'])
@login_required
def set_custom_pricing():
    if current_user.role != 'baker':
        abort(403)

    pricing = BakerPricing.query.filter_by(baker_id=current_user.id).first()
    if not pricing:
        pricing = BakerPricing(baker_id=current_user.id)
        db.session.add(pricing)

    if request.method == 'POST':
        pricing.base_price_per_kg = float(request.form.get('base_price_per_kg', 0))
        pricing.extra_tier_price = float(request.form.get('extra_tier_price', 0))

        # Individual frosting prices
        frosting_prices = {
            'Buttercream': float(request.form.get('frosting_prices[Buttercream]', 0)),
            'Whipped Cream': float(request.form.get('frosting_prices[Whipped Cream]', 0)),
            'Fondant': float(request.form.get('frosting_prices[Fondant]', 0))
        }

        # Topper: one flat price for any
        topper_prices = {
            'Any': float(request.form.get('topper_price', 0))
        }

        pricing.frosting_prices = frosting_prices
        pricing.topper_prices = topper_prices

        db.session.commit()
        flash("Custom pricing saved successfully!", "success")
        return redirect(url_for('baker_dashboard'))

    return render_template('set_custom_pricing.html', pricing=pricing)

@app.route('/baker/<int:baker_id>/get-price', methods=['POST'])
def get_custom_price(baker_id):
    baker = User.query.get_or_404(baker_id)
    if baker.role != 'baker' or not baker.is_approved:
        abort(404)

    # Get pricing rules set by baker
    pricing = BakerPricing.query.filter_by(baker_id=baker_id).first()
    if not pricing:
        flash("Pricing not set by baker yet.", "warning")
        return redirect(request.referrer or url_for('view_bakery', baker_id=baker_id))

    # Fetch cake_types for the baker (needed for rendering the template)
    cake_types = MenuItem.query.filter(
    MenuItem.baker_id == baker_id,
    func.lower(MenuItem.category) == 'cake').all()
    # Get user inputs
    weight = float(request.form.get("weight", 1))
    cake_type = request.form.get("cake_type")
    frosting = request.form.get("frosting")
    tiers = int(request.form.get("tiers", 1))
    topper = request.form.get("topper")

    # Fetch base price of selected cake type from MenuItem
    base_item = MenuItem.query.filter_by(baker_id=baker_id, name=cake_type).first()
    if not base_item:
        flash("Cake type not found.", "danger")
        return redirect(request.referrer)

    base_price = base_item.price * weight
    extra_tier_price = pricing.extra_tier_price * (tiers - 1) if tiers > 1 else 0
    frosting_price = pricing.frosting_prices.get(frosting, 0)
    topper_price = 0 if topper == "None" else pricing.topper_prices.get(topper, 0)

    total_price = base_price + extra_tier_price + frosting_price + topper_price

    # You can flash, redirect or render a new template
    flash(f"Estimated Price: ₹{round(total_price, 2)}", "info")
    return render_template(
    "custom_order_form.html",
    baker=baker,
    cake_types=cake_types,
    pricing=pricing,
    estimated_price=round(total_price, 2)
)

@app.route('/baker/<int:baker_id>/place-custom-order', methods=['POST'])
@login_required
def place_custom_order(baker_id):
    if current_user.role != 'customer':
        abort(403)

    baker = User.query.get_or_404(baker_id)
    if baker.role != 'baker' or not baker.is_approved:
        abort(404)

    weight = float(request.form.get("weight", 1))
    cake_type = request.form.get("cake_type")
    frosting = request.form.get("frosting")
    tiers = int(request.form.get("tiers", 1))
    theme = request.form.get("theme")
    message = request.form.get("message")
    topper = request.form.get("topper")
    delivery_mode = request.form.get("delivery_mode")
    payment_mode = request.form.get("payment_mode")
    estimated_price = float(request.form.get("estimated_price", 0))

    reference_img = request.files.get("reference_img")
    filename = None
    if reference_img:
        filename = secure_filename(reference_img.filename)
        image_path = os.path.join(app.root_path, 'static/uploads', filename)
        reference_img.save(image_path)

    order = Order(
        customer_id=current_user.id,
        baker_id=baker_id,
        is_custom=True,
        weight=weight,
        tiers=tiers,
        cake_type=cake_type,
        frosting=frosting,
        topper=topper,
        theme=theme,
        message=message,
        reference_img=filename,
        estimated_price=estimated_price,
        delivery_mode=delivery_mode,
        payment_mode=payment_mode,
        status="Pending"
    )

    db.session.add(order)
    db.session.commit()

    flash("Custom order placed successfully!", "success")
    return redirect(url_for('my_orders'))


@app.route('/cart/update_quantity/<int:item_id>/<action>', methods=['POST'])
@login_required
def update_cart_quantity(item_id, action):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)

    if action == 'increment':
        item.quantity += 1
    elif action == 'decrement' and item.quantity > 1:
        item.quantity -= 1

    db.session.commit()
    return redirect(url_for('view_cart'))  # or your cart route

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)

    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart", "info")
    return redirect(url_for('view_cart'))

@app.route('/generate-cake-image', methods=['POST'])
def generate_cake_image():
    try:
        data = request.get_json()
        print("Received data:", data)

        weight = data.get('weight', '1')
        tiers = data.get('tiers', '1')
        cake_type = data.get('flavor', 'Vanilla')
        frosting = data.get('frosting', 'Buttercream')
        topper = data.get('topper', 'None')
        theme = data.get('theme', 'Simple')

        prompt = (
            f"A {tiers}-tier {cake_type} cake with {frosting} frosting, "
            f"{topper} topper, {theme} theme, weight approx. {weight} kg, professional photo"
        )
        print("Generated prompt:", prompt)

        url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Accept": "application/json"
        }

        files = {
            "prompt": (None, prompt),
            "output_format": (None, "png"),
            "model": (None, "stable-diffusion-xl-v1")
        }

        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()

        # Parse the response as JSON
        result = response.json()
        print("API response keys:", result.keys())

        # Extract base64 image string
        base64_img = result.get("image")
        if not base64_img:
            print("No 'image' key found in response")
            return jsonify({'error': 'Invalid image response from API'}), 500

        image_data_url = f"data:image/png;base64,{base64_img}"
        print("Returned base64 string (first 100 chars):", image_data_url[:100])

        return jsonify({'image': image_data_url})

    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e.response.status_code)
        print("Response Text:", e.response.text)
        return jsonify({'error': 'Image generation failed'}), 500
    except Exception as e:
        print("Other Error:", str(e))
        return jsonify({'error': 'Image generation failed'}), 500
