import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt

# Load environment variables
load_dotenv()


# Initialize the Flask application
app = Flask(__name__)

# Securely set the secret key from the .env file
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Fallback for development

# Configure the database URI from the .env file or use a default SQLite URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///main.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'routes.login'

# Import and register routes
from app.routes import bp as routes_bp
app.register_blueprint(routes_bp)

# Import User model after db and login_manager are initialized
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
