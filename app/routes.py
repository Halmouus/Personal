from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_user as flask_login_user, logout_user as flask_logout_user, login_required
from . import app, db
from datetime import datetime
from .models import User, LoginSession, Token, TokenTransaction

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

        last_session = LoginSession.query.filter_by(user_id=user.id).order_by(LoginSession.login_time.desc()).first()
        if last_session:
            user.last_login_time = last_session.login_time

        flask_login_user(user)
        session = LoginSession(user_id=user.id)
        db.session.add(session)

        # Issue a token to the user
        user.tokens += 10
        token = Token(user_id=user.id, token_value=1)
        db.session.add(token)

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
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists and user_exists.id != current_user.id:
            flash('Username already exists', 'danger')
            return redirect(url_for('profile'))

        current_user.username = username
        db.session.commit()
        flash('Your profile has been updated', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html')

@app.route('/toggle-dark-mode', methods=['POST'])
@login_required
def toggle_dark_mode():
    data = request.get_json()
    dark_mode = data.get('dark_mode', False)
    session['dark_mode'] = dark_mode
    return jsonify(success=True)

@app.route('/share-tokens', methods=['GET', 'POST'])
@login_required
def share_tokens():
    if request.method == 'POST':
        recipient_username = request.form['recipient']
        tokens = int(request.form['tokens'])

        recipient = User.query.filter_by(username=recipient_username).first()
        if not recipient:
            flash('Recipient not found', 'danger')
            return redirect(url_for('share_tokens'))

        if current_user.tokens < tokens:
            flash('Insufficient tokens', 'danger')
            return redirect(url_for('share_tokens'))

        current_user.tokens -= tokens
        recipient.tokens += tokens

        transaction = TokenTransaction(sender_id=current_user.id, recipient_id=recipient.id, tokens=tokens)
        db.session.add(transaction)
        db.session.commit()

        flash(f'Successfully shared {tokens} tokens with {recipient.username}', 'success')
        return redirect(url_for('dashboard'))

    return render_template('share_tokens.html')