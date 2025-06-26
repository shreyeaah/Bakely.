from app import app, db, bcrypt
from models import User
import os

def initialize_app():
    # Ensure writable folder exists
    instance_path = os.path.join(os.getcwd(), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Auto-create admin if it doesn't exist
        existing_admin = User.query.filter_by(username='admin').first()
        if not existing_admin:
            admin_password = os.getenv("ADMIN_PASSWORD")
            if not admin_password:
                raise Exception("❌ ADMIN_PASSWORD not set in environment!")

            hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')
            admin = User(
                username='admin',
                password=hashed_pw,
                role='admin',
                is_approved=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created.")

# Initialize DB/admin before app starts
initialize_app()


if __name__ == '__main__':
    app.run()
