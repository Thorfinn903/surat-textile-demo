def test_home_page(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/')
    assert response.status_code == 200
    # Add more assertions based on your home page content
    # assert b"Welcome" in response.data

def test_api_status(client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/v1/products' page is requested (GET)
    THEN check that the response is valid
    """
    response = client.get('/api/v1/products')
    assert response.status_code == 200
    assert response.is_json
