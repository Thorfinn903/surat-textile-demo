from .base import Config

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    
    # Use SimpleCache for development to avoid needing a local Redis server
    CACHE_TYPE = 'SimpleCache'
