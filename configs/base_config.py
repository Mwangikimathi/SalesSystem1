import secrets,os

class Base:
    FLASK_APP = os.environ.get('FLASK_APP')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secrets.token_hex(16)

class Development(Base):
    FLASK_ENV = os.environ.get("FLASK_ENV")
    DATABASE = os.environ.get("DATABASE")
    POSTGRES_USER = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
class Staging(Base):
    DATABASE = "df3sunbe9qgbrq"
    POSTGRES_USER = "qtlsbipodudbfx"
    POSTGRES_PASSWORD = "6a283e2624f3a2d08f7ddf67c1534378d04660edc7438830fb3817e8e6e7b8f1"
    SQLALCHEMY_DATABASE_URI ="postgres://qtlsbipodudbfx:6a283e2624f3a2d08f7ddf67c1534378d04660edc7438830fb3817e8e6e7b8f1@ec2-34-254-69-72.eu-west-1.compute.amazonaws.com:5432/df3sunbe9qgbrq"
    pass

class Production(Base):
    pass