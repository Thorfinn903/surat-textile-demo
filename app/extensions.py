from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
from flask_caching import Cache
from flask import current_app

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cors = CORS()

class SafeCache(Cache):
    def _log_status(self, key, status):
        try:
            if current_app:
                current_app.logger.info(f"Cache {status}: {key}")
        except RuntimeError:
            pass

    def get(self, *args, **kwargs):
        try:
            res = super().get(*args, **kwargs)
            self._log_status(args[0], "HIT" if res is not None else "MISS")
            return res
        except Exception as e:
            try:
                if current_app:
                    current_app.logger.warning(f"Cache GET Error (Fallback activated): {e}")
            except RuntimeError:
                pass
            return None

    def set(self, *args, **kwargs):
        try:
            return super().set(*args, **kwargs)
        except Exception as e:
            try:
                if current_app:
                    current_app.logger.warning(f"Cache SET Error (Fallback activated): {e}")
            except RuntimeError:
                pass
            return False

    def delete(self, *args, **kwargs):
        try:
            return super().delete(*args, **kwargs)
        except Exception as e:
            try:
                if current_app:
                    current_app.logger.warning(f"Cache DELETE Error: {e}")
            except RuntimeError:
                pass
            return False

    def delete_memoized(self, *args, **kwargs):
        try:
            return super().delete_memoized(*args, **kwargs)
        except Exception as e:
            try:
                if current_app:
                    current_app.logger.warning(f"Cache DELETE_MEMOIZED Error: {e}")
            except RuntimeError:
                pass
            return False

    def get_many(self, *args, **kwargs):
        try:
            return super().get_many(*args, **kwargs)
        except Exception as e:
            return [None] * len(args[0])

    def set_many(self, *args, **kwargs):
        try:
            return super().set_many(*args, **kwargs)
        except Exception as e:
            return False

    def clear(self):
        try:
            return super().clear()
        except Exception as e:
            try:
                if current_app:
                    current_app.logger.warning(f"Cache CLEAR Error: {e}")
            except RuntimeError:
                pass
            return False

cache = SafeCache()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

# Celery instance - Will be configured in create_app
celery = Celery(__name__)

def init_celery(app):
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
                
    celery.Task = ContextTask
