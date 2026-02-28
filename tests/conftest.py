import pytest
import datetime
from app import create_app
from app.extensions import db as _db
from app.models import User
from werkzeug.security import generate_password_hash
import jwt

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    # We load production/base config and force testing overrides mapping to in-memory sqlite
    app = create_app('testing')
    
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test_secret_key'
    })
    
    ctx = app.app_context()
    ctx.push()

    yield app

    ctx.pop()

@pytest.fixture(scope='session')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='session')
def db(app):
    """Initializes the database for testing."""
    _db.create_all()
    yield _db
    _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    """Creates a new database session for a test avoiding complete drop_all between tests."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    # Create a new scoped session pointing to this connection
    session_factory = db.sessionmaker(bind=connection)
    session = db.scoped_session(session_factory)
    
    # Assign our db global to this session
    # Used for extensions logic falling back to db.session
    db.session = session

    # Insert test users
    admin = User(username='admin', password=generate_password_hash('adminpass'), role='admin')
    sales = User(username='sales', password=generate_password_hash('salespass'), role='sales')
    session.add(admin)
    session.add(sales)
    session.flush()

    yield session

    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture
def admin_token(client, session):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    return response.json['data']['access_token']

@pytest.fixture
def sales_token(client, session):
    response = client.post('/api/v1/auth/login', json={
        'username': 'sales',
        'password': 'salespass'
    })
    return response.json['data']['access_token']
