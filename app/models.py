import uuid
import random
from datetime import datetime
from . import db, bcrypt, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    last_login_time = db.Column(db.DateTime)
    tokens = db.Column(db.Integer, default=0)
    profile_picture = db.Column(db.String(150), nullable=True)
    sessions = db.relationship('LoginSession', backref='user', lazy=True)
    statuses = db.relationship('Status', backref='user', lazy=True)
    items = db.relationship('UserItem', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username!r}>'
    
    def has_liked(self, status):
        return LikeDislike.query.filter_by(user_id=self.id, status_id=status.id, is_like=True).count() > 0

    def has_disliked(self, status):
        return LikeDislike.query.filter_by(user_id=self.id, status_id=status.id, is_like=False).count() > 0

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class LoginSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)
    
    def __repr__(self):
        return f"<LoginSession {self.id} for User {self.user_id}>"
    
class Token(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    token_value = db.Column(db.Integer, nullable=False, default=1)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.token_value} for User {self.user_id}>"
    
class TokenTransaction(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    tokens = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_transactions')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_transactions')

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)

class LikeDislike(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)
    is_like = db.Column(db.Boolean, nullable=False)
    db.UniqueConstraint('user_id', 'status_id', name='user_status_uc')

class Notification(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_notifications')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_notifications')

class Category(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)

class Item(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('category.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    users = db.relationship('UserItem', back_populates='item', lazy=True)

    category = db.relationship('Category', backref=db.backref('items', lazy=True))

class UserItem(db.Model):
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    item_id = db.Column(db.String(36), db.ForeignKey('item.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('user_items', lazy=True))
    item = db.relationship('Item', backref=db.backref('user_items', lazy=True))
