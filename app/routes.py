from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from app.models import User
from app import db, bcrypt
from app.forms import SignupForm
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
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('routes.login'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Signup successful! Welcome to Retrocede.', 'success')
        return redirect(url_for('routes.dashboard'))

    return render_template('signup.html', form=form)

# Dashboard route
@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Logout route
@bp.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('routes.landing'))
