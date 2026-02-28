import json
import pytest
from app.models import Product

def test_ping_endpoint(client):
    """Test the basic healthcheck API."""
    response = client.get('/api/v1/ping')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'operational' in response.json['message']

def test_login_success(client, session):
    """Test successful API login yielding tokens."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'access_token' in response.json['data']
    assert 'refresh_token' in response.json['data']

def test_login_failure(client, session):
    """Test login with bad credentials."""
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert response.json['status'] == 'error'
    
def test_create_product_admin(client, session, admin_token):
    """Test product creation allowed for admins."""
    
    product_data = {
        'name': 'Test Silk Saree',
        'design_no': 'TS-1001',
        'category': 'Saree',
        'wholesale_price': 850.50,
        'fabric': 'Silk',
        'work_type': 'Embroidery'
    }
    
    response = client.post(
        '/api/v1/products',
        json=product_data,
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    print("RESPONSE JSON:", response.json)
    
    assert response.status_code == 201
    assert response.json['status'] == 'success'
    
    # Assert DB has recorded the value
    product = Product.query.filter_by(design_no='TS-1001').first()
    assert product is not None
    assert product.name == 'Test Silk Saree'

def test_admin_dashboard_sales_allowed(client, session, sales_token):
    """Test dashboard stats endpoint is accessible for sales roles."""
    response = client.get(
        '/api/v1/dashboard-stats',
        headers={'Authorization': f'Bearer {sales_token}'}
    )
    
    assert response.status_code == 200
    assert 'engagement_metrics' in response.json['data']
    
def test_admin_users_sales_denied(client, session, sales_token):
    """Enforce strict RBAC: Sales role cannot fetch all users."""
    response = client.get(
        '/api/v1/admin/users',
        headers={'Authorization': f'Bearer {sales_token}'}
    )
    
    assert response.status_code == 403
    assert response.json['status'] == 'error'
    assert 'Admin role required' in response.json['message']

def test_admin_users_admin_allowed(client, session, admin_token):
    """Enforce strict RBAC: Admin role can fetch all users."""
    response = client.get(
        '/api/v1/admin/users',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert isinstance(response.json['data'], list)
    assert len(response.json['data']) >= 2 # From fixtures (admin, sales)
