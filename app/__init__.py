import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///main.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Set Login Manager view
    login_manager.login_view = 'routes.login'

    # Import and register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Import models (ensure db.Model is initialized)
    from app.models import User

    # @login_manager.user_loader
    # def load_user(user_id):
    #     return User.query.get(int(user_id))

    # Setup Google Auth Blueprint
    google_bp = make_google_blueprint(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_to="routes.google_login"
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    return app
