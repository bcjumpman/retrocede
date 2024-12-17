import os
from app import db, create_app
from app.models import User
from flask_bcrypt import Bcrypt
from flask_migrate import upgrade

# Initialize Flask app and context
app = create_app()
bcrypt = Bcrypt(app)

with app.app_context():
    # Delete the existing database file
    if os.path.exists("main.db"):
        os.remove("main.db")
        print("✅ Database file deleted successfully.")

    # Drop all existing tables
    print("🔄 Dropping existing tables...")
    db.drop_all()

    # Recreate the database schema
    print("🔄 Recreating database schema...")
    db.create_all()

    # Seed initial data
    print("🌱 Seeding database with initial data...")
    demo_user = User(
        username="demo",
        email="demo@example.com",
        password=bcrypt.generate_password_hash("password").decode('utf-8'),
        balance=1000.0
    )
    db.session.add(demo_user)
    db.session.commit()

    print("🎉 Database reset complete with demo user!")
