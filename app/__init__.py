from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO

app = Flask(__name__, static_folder="static")
app.config.from_object('config.Config')

socketio = SocketIO(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login = LoginManager(app)
login.login_view = 'login'

from . import routes, models
