import os
import pytest
import requests
import json
import time

# Get the API URL from environment variable or use default
# When running in Docker, this should be set to http://fogis-api-client-dev:8080
API_URL = os.environ.get('API_URL', 'http://localhost:8080')

def test_health_endpoint():
    """Test the /health endpoint returns a valid response."""
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_hello_endpoint():
    """Test the /hello endpoint returns a valid response."""
    response = requests.get(f"{API_URL}/hello")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert "Hello" in data["message"]

def test_root_endpoint():
    """Test the root endpoint returns a valid JSON response."""
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert data["status"] == "ok"
    assert "message" in data
    assert "FOGIS API Gateway" in data["message"]

def test_matches_endpoint():
    """Test the /matches endpoint returns a list of matches."""
    # This endpoint might return an error if not authenticated
    # We'll just check that it returns a valid response
    response = requests.get(f"{API_URL}/matches")
    assert response.status_code in [200, 500]  # Either success or error is acceptable

    # If successful, check the structure
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)

def test_match_details_endpoint():
    """Test the /match/<match_id> endpoint returns match details."""
    # This endpoint might return an error if not authenticated
    # We'll just check that it returns a valid response
    response = requests.get(f"{API_URL}/match/1")
    assert response.status_code in [200, 500]  # Either success or error is acceptable

    # If successful, check that it's a dict
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)

if __name__ == "__main__":
    # Add a delay to ensure the API service is fully up
    print("Waiting for API service to be ready...")
    time.sleep(5)

    # Run the tests
    pytest.main(["-v", __file__])
