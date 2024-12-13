from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from app.models import User, Portfolio, Transaction
from app import db, bcrypt
from app.forms import SignupForm
from app.utils import get_stock_data
import re

# Create a Blueprint instance
bp = Blueprint('routes', __name__)

# Landing page route
@bp.route('/')
def landing():
    return render_template('landing.html')


# Login route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        # Verify the password hash
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))

        flash('Invalid email or password', 'danger')
    return render_template('login.html')


# Signup route
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Backend logic to process the form
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if the email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('routes.login'))

        # Check if the username is already registered
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username is already taken. Please choose a different one.', 'danger')
            return redirect(url_for('routes.signup'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Add the user to the database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! You can now log in.', 'success')
        return redirect(url_for('routes.login'))

    # Display form errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    return render_template('signup.html', form=form)


# Dashboard route
@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Stock data
@bp.route('/stock/<symbol>', methods=['GET'])
def stock_data(symbol):
    """
    Endpoint to fetch stock data for a given symbol.
    """
    try:
        data = get_stock_data(symbol)
        if "error" in data:
            return jsonify({"error": data["error"]}), 400  # Return 400 for errors
        return jsonify(data)
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

# Buy stock
@bp.route('/buy', methods=['POST'])
@login_required
def buy_stock():
    stock = request.form.get('stock').upper()
    quantity = int(request.form.get('quantity'))
    price = float(request.form.get('price'))

    # Record the transaction
    transaction = Transaction(
        stock=stock,
        quantity=quantity,
        price=price,
        transaction_type="buy",
        user_id=current_user.id
    )
    db.session.add(transaction)

    # Update the portfolio
    portfolio_item = Portfolio.query.filter_by(user_id=current_user.id, stock=stock).first()
    if portfolio_item:
        portfolio_item.quantity += quantity
    else:
        portfolio_item = Portfolio(stock=stock, quantity=quantity, user_id=current_user.id)
        db.session.add(portfolio_item)

    db.session.commit()
    flash(f"Successfully bought {quantity} shares of {stock} at ${price} each.", "success")
    return redirect(url_for('routes.dashboard'))

# Sell stock
@bp.route('/sell', methods=['POST'])
@login_required
def sell_stock():
    stock = request.form.get('stock').upper()
    quantity = int(request.form.get('quantity'))
    price = float(request.form.get('price'))

    # Update the portfolio
    portfolio_item = Portfolio.query.filter_by(user_id=current_user.id, stock=stock).first()
    if not portfolio_item or portfolio_item.quantity < quantity:
        flash(f"Error: Not enough shares of {stock} to sell.", "danger")
        return redirect(url_for('routes.dashboard'))

    portfolio_item.quantity -= quantity
    if portfolio_item.quantity == 0:
        db.session.delete(portfolio_item)

    # Record the transaction
    transaction = Transaction(
        stock=stock,
        quantity=quantity,
        price=price,
        transaction_type="sell",
        user_id=current_user.id
    )
    db.session.add(transaction)
    db.session.commit()

    flash(f"Successfully sold {quantity} shares of {stock} at ${price} each.", "success")
    return redirect(url_for('routes.dashboard'))

# Logout route
@bp.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('routes.landing'))
