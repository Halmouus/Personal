import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://halmous:Halmous%402024@localhost/my_project_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False