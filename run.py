from app import app, socketio  # Import socketio here
from whitenoise import WhiteNoise

app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

if __name__ == '__main__':
    socketio.run(app, debug=True)
