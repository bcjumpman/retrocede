from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    portfolio = db.relationship('Portfolio', backref='owner', lazy=True)

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # "buy" or "sell"
    date = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
