import os
from app import create_app
from app.extensions import celery

# Create an application instance that configures the Celery instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Push application context so models and extensions resolve gracefully
app.app_context().push()
