import os
from .base import Config

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    # Use environment variables for secrets in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # PythonAnywhere Fallback: Use SimpleCache if Redis is not available
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'SimpleCache')
    REDIS_URL = os.environ.get('REDIS_URL', None)
    
    if not REDIS_URL:
        CACHE_TYPE = 'SimpleCache'
        CELERY_BROKER_URL = None
        CELERY_RESULT_BACKEND = None
