from app import app, db, bcrypt
from models import User
import os

def initialize_admin():
    with app.app_context():
        # Auto-create admin if it doesn't exist
        try:
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
        except Exception as e:
            print(f"⚠️ Skipping admin creation: {e}")

if __name__ == '__main__':
    app.run()
