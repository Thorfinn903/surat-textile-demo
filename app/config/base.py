import os
from datetime import timedelta
from pathlib import Path

class Config:
    """Base config."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'surat-textile-secret-key-123')
    # Since this file is in app/config/base.py, BASE_DIR is parent.parent.parent
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    # Instance folder logic
    INSTANCE_PATH = BASE_DIR / 'instance'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{INSTANCE_PATH / "textile.db"}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    
    # Redis & Caching
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Celery
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Application specific
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'products'
