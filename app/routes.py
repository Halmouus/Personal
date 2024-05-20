from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user as flask_login_user, logout_user as flask_logout_user, login_required
from . import app, db
from datetime import datetime
from .models import User, LoginSession

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'], endpoint='register')
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'], endpoint='login')
def login_user():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
        
        flask_login_user(user)
        session = LoginSession(user_id=user.id)
        db.session.add(session)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout', endpoint='logout')
def logout_user():
    if current_user.is_authenticated:
        session = LoginSession.query.filter_by(user_id=current_user.id, logout_time=None).order_by(LoginSession.login_time.desc()).first()
        if session:
            session.logout_time = datetime.utcnow()
            db.session.commit()
    flask_logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard', endpoint='dashboard')
@login_required
def dashboard_user():
    return render_template('dashboard.html')

@app.route('/profile', methods=['GET', 'POST'], endpoint='profile')
@login_required
def profile():
    if request.method == 'POST':
        username = request.form['username']
        
        # Check if the new username is already taken
        user_exists = User.query.filter_by(username=username).first()
        if user_exists and user_exists.id != current_user.id:
            flash('Username already exists', 'danger')
            return redirect(url_for('profile'))

        current_user.username = username
        db.session.commit()
        flash('Your profile has been updated', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')
