import uuid
from datetime import datetime
from . import db, bcrypt, login
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    login_sessions = db.relationship('LoginSession', backref='user', lazy=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username!r}>'
    
@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class LoginSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime)

    def __repr__(self):
        return f"<LoginSession {self.id} for User {self.user_id}>"
