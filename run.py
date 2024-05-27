from whitenoise import WhiteNoise
from app import app
from flask_socketio import SocketIO
import eventlet

socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

if __name__ == '__main__':
    socketio.run(app, debug=True)
