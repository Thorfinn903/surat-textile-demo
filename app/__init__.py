import os
from flask import Flask
from .extensions import db, login_manager, migrate, cors, cache, socketio, init_celery, limiter
from .utils.helpers import load_settings
from .models import User, Product, ActivityLog, InquiryLog
from .utils.seeder import seed_database
from .context_processors import inject_global_template_data
from .config import config_dict

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or \
                      os.environ.get('FLASK_ENV') or \
                      os.environ.get('ENV') or \
                      'development'

    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates',
                instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(config_dict[config_name])
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Load dynamic settings
    app.config['SHOP_SETTINGS'] = load_settings()

    # --- INITIALIZE EXTENSIONS ---
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    cache.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    init_celery(app)
    limiter.init_app(app)
    
    # Import tasks so celery discovers them
    with app.app_context():
        from . import tasks
    
    # Initialize Swagger
    from flasgger import Swagger
    app.config['SWAGGER'] = {
        'title': 'Digital Dukan API',
        'uiversion': 3
    }
    Swagger(app)
    
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # --- REGISTER CONTEXT PROCESSORS ---
    app.context_processor(inject_global_template_data)

    # --- INFRASTRUCTURE SETUP ---
    from .utils.errors import register_error_handlers
    from .utils.logging_config import configure_logging
    from .utils.middleware import register_middleware
    
    register_error_handlers(app)
    configure_logging(app)
    register_middleware(app)
    from .utils import sockets # Register SocketIO handlers

    # --- REGISTER FEATURE BLUEPRINTS ---
    from .namespaces.public import public_bp
    from .namespaces.auth import auth_bp
    from .namespaces.catalog import catalog_bp
    from .namespaces.admin import admin_bp
    from .namespaces.api.v1 import api_v1_bp

    app.register_blueprint(public_bp) # No prefix to keep / as index
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    # --- DB SETUP ---
    with app.app_context():
        db.create_all()
        pass

    # Database and Migrations are initialized above
    return app
