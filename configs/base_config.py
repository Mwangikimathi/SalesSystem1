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

class Production(Base):
    pass