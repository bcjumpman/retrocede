from app import db, bcrypt, app
from app.models import User

def hash_plain_text_passwords():
    """
    Hash all plain-text passwords in the database.
    This script will update any password that is not already hashed.
    """
    with app.app_context():  # Push application context
        users = User.query.all()
        for user in users:
            # Check if the password is already hashed
            if not user.password.startswith("$2b$"):
                user.password = bcrypt.generate_password_hash(user.password).decode('utf-8')
                print(f"Updated password for user {user.username}")
        db.session.commit()

if __name__ == "__main__":
    hash_plain_text_passwords()
