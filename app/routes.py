import os
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_user as flask_login_user, logout_user as flask_logout_user, login_required
from . import socketio
from . import app, db
from datetime import datetime
from .models import User, LoginSession, Token, TokenTransaction, Status, LikeDislike, Notification, Category, UserItem, Item, Message
from sqlalchemy import update

@app.route('/')
@login_required
def home():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'], endpoint='register')
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        pseudo = request.form['pseudo']
        password = request.form['password']
        profile_picture = request.form['profile_picture']

        user_exists = User.query.filter_by(username=username).first()
        pseudo_exists = User.query.filter_by(pseudo=pseudo).first()

        if user_exists:
            flash('Bad Habiba! Username already exists', 'danger')
            return redirect(url_for('register'))

        if pseudo_exists:
            flash('This Habiba is already taken mate!', 'danger')
            return redirect(url_for('register'))

        if not profile_picture:
            flash('Profile picture selection is required.', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, pseudo=pseudo, profile_picture=profile_picture)
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
            if not os.path.exists(profile_picture_dir):
                os.makedirs(profile_picture_dir)
            profile_picture_path = os.path.join(profile_picture_dir, filename)
            
            # Save and read the file stream
            profile_picture.save(profile_picture_path)
            profile_picture.stream.seek(0)
            # Add any further file processing here if needed
            
            current_user.profile_picture = filename
            flash(f'Profile picture successfully uploaded to {profile_picture_path}', 'success')

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
            flash('You cannot send Habibas to yourself. Are you pansexual?', 'danger')
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
            flash('User not found.', 'danger')
            return redirect(url_for('share_tokens'))
        
        if current_user.tokens < amount:
            flash('Not enough Habibas! You are broke as hell!', 'danger')
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

        # Create notification
        notification = Notification(
            recipient_id=recipient.id,
            sender_id=current_user.id,
            amount=amount
        )
        db.session.add(notification)
        db.session.commit()
        
        # Emit real-time notification
        socketio.emit('new_notification', {
            'recipient_id': recipient.id,
            'sender': current_user.pseudo,
            'amount': amount
        })

        flash('Love successfully shared. You are gay now!', 'success')
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
def increment_like_status(status_id):
    status = Status.query.get_or_404(status_id)
    status.likes += 1
    db.session.commit()
    return jsonify({'likes': status.likes, 'dislikes': status.dislikes})


@app.route('/dislike_status/<int:status_id>', methods=['POST'])
@login_required
def increment_dislike_status(status_id):
    status = Status.query.get_or_404(status_id)
    status.dislikes += 1
    db.session.commit()
    return jsonify({'likes': status.likes, 'dislikes': status.dislikes})


@app.route('/like/<int:status_id>', methods=['POST'])
@login_required
def like_status(status_id):
    status = Status.query.get_or_404(status_id)
    existing_like = LikeDislike.query.filter_by(user_id=current_user.id, status_id=status_id).first()

    if existing_like:
        if existing_like.is_like:
            db.session.delete(existing_like)
        else:
            existing_like.is_like = True
            status.likes += 1
            status.dislikes -= 1
    else:
        new_like = LikeDislike(user_id=current_user.id, status_id=status_id, is_like=True)
        db.session.add(new_like)
        status.likes += 1

    db.session.commit()

    likes_count = LikeDislike.query.filter_by(status_id=status_id, is_like=True).count()
    dislikes_count = LikeDislike.query.filter_by(status_id=status_id, is_like=False).count()

    return jsonify({"likes": likes_count, "dislikes": dislikes_count})


@app.route('/dislike/<int:status_id>', methods=['POST'])
@login_required
def dislike_status(status_id):
    status = Status.query.get_or_404(status_id)
    existing_dislike = LikeDislike.query.filter_by(user_id=current_user.id, status_id=status_id).first()

    if existing_dislike:
        if not existing_dislike.is_like:
            db.session.delete(existing_dislike)
        else:
            existing_dislike.is_like = False
            status.likes -= 1
            status.dislikes += 1
    else:
        new_dislike = LikeDislike(user_id=current_user.id, status_id=status_id, is_like=False)
        db.session.add(new_dislike)
        status.dislikes += 1

    db.session.commit()

    likes_count = LikeDislike.query.filter_by(status_id=status_id, is_like=True).count()
    dislikes_count = LikeDislike.query.filter_by(status_id=status_id, is_like=False).count()

    return jsonify({"likes": likes_count, "dislikes": dislikes_count})


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    if query:
        users = User.query.filter(User.pseudo.like(f'{query}%')).all()
        results = [
            {
                'id': user.id,
                'pseudo': user.pseudo,
                'tokens': user.tokens  # Assuming you have a field for token count
            }
            for user in users
        ]
        return jsonify(results)
    return jsonify([])


@app.route('/network')
@login_required
def network():
    return render_template('network.html')

@app.route('/profile/<string:user_id>')
@login_required
def view_profile(user_id):
    app.logger.info(f"Fetching profile for user ID: {user_id}")
    user = User.query.get_or_404(user_id)
    if not user:
        app.logger.error(f"User with ID {user_id} not found.")
        return "User not found", 404
    statuses = Status.query.filter_by(user_id=user.id).order_by(Status.timestamp.desc()).all()
    return render_template('view_profile.html', user=user, statuses=statuses)


@app.route('/notifications')
@login_required
def notifications():
    # Fetch unread notifications
    notifications = Notification.query.filter_by(recipient_id=current_user.id, read=False).all()

    # Prepare notification data for JSON response
    notification_data = [{
        'id': notification.id,  # Ensure each notification has a unique identifier
        'sender': notification.sender.pseudo,
        'amount': notification.amount,
        'timestamp': notification.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
    } for notification in notifications]

    # Mark notifications as read after sending
    for notification in notifications:
        notification.read = True
    db.session.commit()

    return jsonify(notification_data)


@app.route('/shop')
@login_required
def shop():
    categories = Category.query.all()
    items = Item.query.all()
    return render_template('shop.html', categories=categories, items=items)

@app.route('/shop/item/<string:item_id>')
@login_required
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@app.route('/shop/purchase/<string:item_id>', methods=['POST'])
@login_required
def purchase_item(item_id):
    item = Item.query.get_or_404(item_id)

    if UserItem.query.filter_by(user_id=current_user.id, item_id=item.id).first():
        flash('You already own this item, Habiba!', 'danger')
        return redirect(url_for('item_detail', item_id=item_id))
    
    if current_user.tokens < item.price:
        flash('Sorry, cannot afford it, because you are poor! Get some Habibas!', 'danger')
        return redirect(url_for('shop'))
    
    current_user.tokens -= item.price
    user_item = UserItem(user_id=current_user.id, item_id=item.id)
    db.session.add(user_item)
    db.session.commit()
    
    flash('Item purchased successfully!', 'success')
    return redirect(url_for('shop'))

from collections import defaultdict

@app.route('/inventory')
@login_required
def inventory():
    user_items = UserItem.query.filter_by(user_id=current_user.id).all()
    items = [ui.item for ui in user_items]
    categories = Category.query.all()

    # Organize items by category
    categorized_items = defaultdict(list)
    for item in items:
        categorized_items[item.category.name].append(item)

    # Ensure each category is represented even if no items are present
    categorized_items_full = {cat.name: categorized_items[cat.name] for cat in categories}

    return render_template('inventory.html', categorized_items=categorized_items_full)


@app.route('/set_profile_picture/<item_id>', methods=['GET'])
@login_required
def set_profile_picture(item_id):
    item = Item.query.filter_by(id=item_id).first()
    if item and item.category.name == "Avatars":
        current_user.profile_picture = item.image_url
        db.session.commit()
        flash('Profile picture updated.', 'success')
    else:
        flash('Invalid item selected.', 'error')
    return redirect(url_for('inventory'))

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    receiver_id = request.form.get('receiver_id')
    message_text = request.form.get('message')
    if receiver_id and message_text:
        message = Message(sender_id=current_user.id, receiver_id=receiver_id, body=message_text)
        db.session.add(message)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Message sent!'})
    return jsonify({'status': 'error', 'message': 'Failed to send message.'})

@app.route('/conversations/<user_id>')
@login_required
def conversations(user_id):
    messages_sent = Message.query.filter_by(sender_id=current_user.id, receiver_id=user_id).all()
    messages_received = Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id).all()
    # Combine and sort the messages
    messages = sorted(messages_sent + messages_received, key=lambda x: x.timestamp)
    return jsonify({'messages': [message.body for message in messages]})

@app.route('/list_conversations')
@login_required
def list_conversations():
    sent_users = User.query.join(Message, User.id == Message.receiver_id).filter(Message.sender_id == current_user.id).distinct()
    received_users = User.query.join(Message, User.id == Message.sender_id).filter(Message.receiver_id == current_user.id).distinct()
    all_users = {user.id: user.pseudo for user in set(sent_users).union(set(received_users))}
    return jsonify(all_users)

@app.route('/fetch-users')
@login_required
def fetch_users():
    # Fetch users with whom the current user has exchanged messages
    users = User.query.join(Message, db.or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)).distinct().all()
    return jsonify(users=[{'id': user.id, 'pseudo': user.pseudo} for user in users])

@app.route('/fetch-messages/<int:user_id>')
@login_required
def fetch_messages(user_id):
    # Fetch messages between the current user and the specified user_id
    messages = Message.query.filter(
        db.or_(
            db.and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            db.and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    return jsonify(messages=[{'content': message.content, 'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for message in messages])

@app.route('/messages')
@login_required
def messages():
    return render_template('messages.html')
