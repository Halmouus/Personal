from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login = LoginManager(app)
login.login_view = 'login'

csrf = CSRFProtect(app)

# Import routes after initializing db to avoid circular imports
from . import routes, models
