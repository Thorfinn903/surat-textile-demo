import os
from .base import Config

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    # SQLAlchemy database URI should also be pulled from environment in production
    db_url = os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    REDIS_URL = os.environ.get('REDIS_URL', None)
    
    if REDIS_URL:
        CACHE_TYPE = os.environ.get('CACHE_TYPE', 'RedisCache')
        CACHE_REDIS_URL = REDIS_URL
    else:
        CACHE_TYPE = 'SimpleCache'
        CELERY_BROKER_URL = None
        CELERY_RESULT_BACKEND = None
