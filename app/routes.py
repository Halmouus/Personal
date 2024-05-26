import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_user as flask_login_user, logout_user as flask_logout_user, login_required
from . import app, db
from datetime import datetime
from .models import User, LoginSession, Token, TokenTransaction, Status

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'], endpoint='register')
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        pseudo = request.form['pseudo']
        password = request.form['password']

        user_exists = User.query.filter_by(username=username).first()
        pseudo_exists = User.query.filter_by(pseudo=pseudo).first()
        
        if user_exists:
            flash('Bad Habiba! Username already exists', 'danger')
            return redirect(url_for('register'))
        
        if pseudo_exists:
            flash('This Habiba is already taken mate!', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, pseudo=pseudo)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('You are a registered Habiba and can log in now!', 'success')
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
        pseudo = request.form.get('pseudo')
        status_text = request.form.get('status')
        profile_picture = request.files.get('profile_picture')
        
        if pseudo:
            pseudo_exists = User.query.filter(User.pseudo == pseudo, User.id != current_user.id).first()
            if pseudo_exists:
                flash('Too bad! Habiba already taken', 'danger')
                return redirect(url_for('profile'))
            current_user.pseudo = pseudo
        
        if status_text:
            new_status = Status(user_id=current_user.id, text=status_text)
            db.session.add(new_status)

        if profile_picture:
            filename = secure_filename(profile_picture.filename)
            profile_picture_dir = os.path.join('static', 'profile_pics')
            profile_picture_path = os.path.join(profile_picture_dir, filename)
            profile_picture.save(profile_picture_path)
            current_user.profile_picture = 'profile_pics/' + filename
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))

    statuses = Status.query.filter_by(user_id=current_user.id).order_by(Status.timestamp.desc()).all()
    return render_template('profile.html', title='Profile', user=current_user, statuses=statuses)


@app.route('/toggle-dark-mode', methods=['POST'])
@login_required
def toggle_dark_mode():
    data = request.get_json()
    dark_mode = data.get('dark_mode', False)
    session['dark_mode'] = dark_mode
    return jsonify(success=True)


@app.route('/share-tokens', methods=['GET', 'POST'], endpoint='share_tokens')
@login_required
def share_tokens():
    if request.method == 'POST':
        recipient_username = request.form.get('recipient')
        amount = request.form.get('amount')
        
        if not recipient_username or not amount:
            flash('Recipient and amount are required.', 'danger')
            return redirect(url_for('share_tokens'))
        
        if recipient_username == current_user.pseudo:
            flash('You cannot send tokens to yourself', 'danger')
            return redirect(url_for('share_tokens'))  
             
        try:
            amount = int(amount)
        except ValueError:
            flash('Amount must be an integer.', 'danger')
            return redirect(url_for('share_tokens'))

        if amount <= 0:
            flash('Amount must be greater than zero.', 'danger')
            return redirect(url_for('share_tokens'))

        recipient = User.query.filter_by(pseudo=recipient_username).first()
        if not recipient:
            flash('Habiba not found.', 'danger')
            return redirect(url_for('share_tokens'))
        
        if current_user.tokens < amount:
            flash('Poor! Not enough Habiba Points!', 'danger')
            return redirect(url_for('share_tokens'))

        current_user.tokens -= amount
        recipient.tokens += amount
        
        transaction = TokenTransaction(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            tokens=amount,
            timestamp=datetime.utcnow()
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash('Habibas successfully shared.', 'success')
        return redirect(url_for('share_tokens'))
    
    return render_template('share_tokens.html')


@app.route('/transaction-history', methods=['GET'])
@login_required
def transaction_history():
    sent_transactions = TokenTransaction.query.filter_by(sender_id=current_user.id).all()
    received_transactions = TokenTransaction.query.filter_by(recipient_id=current_user.id).all()
    
    return render_template('transaction_history.html', sent_transactions=sent_transactions, received_transactions=received_transactions)


@app.route('/autocomplete_usernames', methods=['GET'])
@login_required
def autocomplete_usernames():
    query = request.args.get('query', '')
    if not query:
        return jsonify([])

    users = User.query.filter(User.pseudo.ilike(f'{query}%'), User.id != current_user.id).all()
    usernames = [user.pseudo for user in users]

    return jsonify(usernames)


@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.tokens.desc()).limit(100).all()
    current_user_rank = User.query.filter(User.tokens > current_user.tokens).count() + 1

    return render_template('leaderboard.html', users=users, current_user_rank=current_user_rank)

@app.route('/like_status/<int:status_id>', methods=['POST'])
@login_required
def like_status(status_id):
    status = Status.query.get_or_404(status_id)
    status.likes += 1
    db.session.commit()
    return jsonify({'likes': status.likes, 'dislikes': status.dislikes})


@app.route('/dislike_status/<int:status_id>', methods=['POST'])
@login_required
def dislike_status(status_id):
    status = Status.query.get_or_404(status_id)
    status.dislikes += 1
    db.session.commit()
    return jsonify({'likes': status.likes, 'dislikes': status.dislikes})

