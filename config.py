import os

class Config:
    SECRET_KEY = 'a_super_secret_key_for_testing_purposes'  # Fixed key for sessions
    SQLALCHEMY_DATABASE_URI = os.getenv('JAWSDB_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True  # Ensure cookies are secure
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # Mitigate CSRF attacks
