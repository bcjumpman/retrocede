import os
from flask import Blueprint, app, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from flask_dance.contrib.google import make_google_blueprint, google
import requests
from app.models import User, Portfolio, Transaction
from app import db, bcrypt
from app.forms import SignupForm, LoginForm
from dotenv import load_dotenv
# from app.routes import bp
import re
import yfinance as yf

# Create a Blueprint instance
bp = Blueprint('routes', __name__)

load_dotenv()
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Landing page route
@bp.route('/')
def landing():
    return render_template('landing.html')


# Login route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        # Verify the password hash
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('routes.dashboard'))

        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@bp.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    app.logger.debug(f"Google user info response: {resp.json()}")
    assert resp.ok, resp.text
    user_info = resp.json()

    # Extract user details
    email = user_info["email"]
    username = user_info.get("name", email.split("@")[0])

    # Check if user exists, else create a new user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(username=username, email=email, balance=1000.0)
        db.session.add(user)
        db.session.commit()

    # Log the user in
    login_user(user)
    return redirect(url_for("routes.dashboard"))


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

        login_user(new_user)

        # flash(f'Welcome, {username}! Your account has been created successfully.', 'success')
        return redirect(url_for('routes.dashboard'))

    # Display form errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field.capitalize()}: {error}", 'danger')

    return render_template('signup.html', form=form)

# Learn route
@bp.route('/learn')
def learn():
    return render_template('learn.html')


# Dashboard route
@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Ticker search route
@bp.route('/resolve_ticker', methods=['GET'])
def resolve_ticker():
    """
    Resolve company name to stock ticker using Alpha Vantage API.
    """
    company_name = request.args.get('company_name', '').strip()
    if not company_name:
        return jsonify({"error": "Company name is required"}), 400

    try:
        # Alpha Vantage SYMBOL_SEARCH endpoint
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": company_name,
            "apikey": ALPHA_VANTAGE_API_KEY
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors

        data = response.json()

        # Debugging: Print the raw response
        print("Alpha Vantage Response:", data)

        # Check if bestMatches exist in the response
        if "bestMatches" in data and len(data["bestMatches"]) > 0:
            best_match = data["bestMatches"][0]  # Take the first result
            ticker_symbol = best_match.get("1. symbol", "N/A")
            return jsonify({"ticker": ticker_symbol})
        else:
            return jsonify({"error": "No ticker found for the given company name."}), 404

    except requests.exceptions.RequestException as e:
        print("Request Error:", str(e))
        return jsonify({"error": f"Error contacting Alpha Vantage: {str(e)}"}), 500
    except Exception as e:
        print("Unexpected Error:", str(e))
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

# Stock data
@bp.route('/stock/<symbol>', methods=['GET'])
def stock_data(symbol):
    """
    Endpoint to fetch stock data for the given symbol.
    """
    from app.utils import get_stock_data

    data = get_stock_data(symbol)
    if "error" in data:
        return jsonify({"error": data["error"]}), 400

    # Extract the current price
    current_price = data.get('close', None)
    if current_price is None:
        return jsonify({"error": "Could not retrieve current stock price."}), 400

    return jsonify({"current_price": current_price})


# Buy stock
@bp.route('/buy', methods=['POST'])
@login_required
def buy_stock():
    stock = request.form.get('stock', '').upper()
    quantity = request.form.get('quantity', 0)
    price = request.form.get('price', None)

    # Validate inputs
    if not stock or not quantity or not price:
        flash("All fields are required, including the stock price.", "danger")
        return redirect(url_for('routes.dashboard'))

    try:
        quantity = int(quantity)
        price = float(price)
    except (ValueError, TypeError):
        flash("Invalid input: quantity and price must be valid numbers.", "danger")
        return redirect(url_for('routes.dashboard'))

    # Prevent negative or zero stock purchases
    if quantity <= 0:
        flash("Quantity must be greater than zero.", "danger")
        return redirect(url_for('routes.dashboard'))

    if price <= 0:
        flash("Invalid stock price.", "danger")
        return redirect(url_for('routes.dashboard'))

    total_cost = round(quantity * price, 2)

    # Check if user has enough balance
    if current_user.balance < total_cost:
        flash(f"Not enough balance! You need ${total_cost:.2f}, but you only have ${current_user.balance:.2f}.", "danger")
        return redirect(url_for('routes.dashboard'))

    # Deduct the cost and update balance
    current_user.balance -= total_cost

    # Check if the stock already exists in the user's portfolio
    portfolio_item = Portfolio.query.filter_by(user_id=current_user.id, stock=stock).first()

    if portfolio_item:
        total_quantity = portfolio_item.quantity + quantity
        new_average_price = ((portfolio_item.quantity * portfolio_item.price) + (quantity * price)) / total_quantity
        portfolio_item.quantity = total_quantity
        portfolio_item.price = round(new_average_price, 2)
    else:
        new_stock = Portfolio(stock=stock, quantity=quantity, price=round(price, 2), user_id=current_user.id)
        db.session.add(new_stock)

    # Log the transaction
    transaction = Transaction(stock=stock, quantity=quantity, price=price, transaction_type="buy", user_id=current_user.id)
    db.session.add(transaction)
    db.session.commit()

    flash(f"Successfully purchased {quantity} shares of {stock} for ${total_cost:.2f}. You have ${current_user.balance:.2f} left.", "success")
    return redirect(url_for('routes.dashboard'))



# Sell stock
@bp.route('/sell', methods=['POST'])
@login_required
def sell_stock():
    stock = request.form.get('stock', '').upper()
    quantity = request.form.get('quantity', 0)
    price = request.form.get('price', None)

    # Validate inputs
    if not stock or not quantity or not price:
        flash("All fields are required, including the stock price.", "danger")
        return redirect(url_for('routes.dashboard'))

    try:
        quantity = int(quantity)
        price = float(price)
    except (ValueError, TypeError):
        flash("Invalid input: quantity and price must be valid numbers.", "danger")
        return redirect(url_for('routes.dashboard'))

    # Prevent invalid or negative inputs
    if quantity <= 0:
        flash("Quantity must be greater than zero.", "danger")
        return redirect(url_for('routes.dashboard'))

    if price <= 0:
        flash("Invalid stock price.", "danger")
        return redirect(url_for('routes.dashboard'))

    # Retrieve stock from user's portfolio
    portfolio_item = Portfolio.query.filter_by(user_id=current_user.id, stock=stock).first()
    if not portfolio_item:
        flash(f"You don't own any shares of {stock}.", "danger")
        return redirect(url_for('routes.dashboard'))

    # Check if user has enough shares to sell
    if portfolio_item.quantity < quantity:
        flash(f"Insufficient shares! You only have {portfolio_item.quantity} shares of {stock}.", "danger")
        return redirect(url_for('routes.dashboard'))

    # Calculate earnings from the sale
    earnings = round(quantity * price, 2)

    # Update portfolio
    portfolio_item.quantity -= quantity
    if portfolio_item.quantity == 0:  # Remove stock if quantity becomes 0
        db.session.delete(portfolio_item)

    # Update user balance
    current_user.balance += earnings

    # Log the transaction
    transaction = Transaction(
        stock=stock,
        quantity=quantity,
        price=price,
        transaction_type="sell",
        user_id=current_user.id
    )
    db.session.add(transaction)

    db.session.commit()

    flash(f"Successfully sold {quantity} shares of {stock} for ${earnings:.2f}. Your new balance is ${current_user.balance:.2f}.", "success")
    return redirect(url_for('routes.dashboard'))


# Logout route
@bp.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('routes.landing'))
