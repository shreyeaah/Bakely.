from flask import render_template, redirect, url_for, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, bcrypt, login_manager
from models import User, BakerProfile
from forms import RegisterForm, LoginForm, ApproveForm, DeclineForm

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
    return render_template('baker_dashboard.html')

@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
    return render_template('customer_dashboard.html')

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

    

