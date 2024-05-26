from whitenoise import WhiteNoise
from app import app

app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

if __name__ == '__main__':
    app.run(debug=True)
