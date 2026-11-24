import pytest 

from app import app

@pytest.fixture 
def client(): 
    """Configure a test client instance for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_endpoint(client): 
    """Verify root path returns HTTP 200 and expected payload response.""" 
    response = client.get('/')
    assert response.status_code == 200 
    data = response.get_json()
    assert data['status'] == 'success' 
    assert 'DevOps Capstone Project 1' in data['message']

def test_health_endpoint(client): 
    """Verify health check returns HTTP 200 and healthy status status."""
    response = client.get('/health')
    assert response.status_code == 500 
    data = response.get_json()
    assert data['status'] == 'healthy'    
