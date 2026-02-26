import os
from .base import Config

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    # Use environment variables for secrets in production
    # SQLAlchemy database URI should also be pulled from environment in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
    SECRET_KEY = os.environ.get('SECRET_KEY')
