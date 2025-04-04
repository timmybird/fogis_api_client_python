import os
import pytest
import requests
import json
import time

# Get the API URL from environment variable or use default
API_URL = os.environ.get('API_URL', 'http://localhost:8080')

def test_hello_endpoint():
    """Test the /hello endpoint returns a valid response."""
    response = requests.get(f"{API_URL}/hello")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, str)
    assert "Hello" in data

def test_root_endpoint():
    """Test the root endpoint returns a valid JSON response."""
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check for Unicode handling
    unicode_items = [item for item in data if 'unicode_item' in item]
    assert len(unicode_items) > 0
    assert 'åäö' in unicode_items[0]['unicode_item']

def test_matches_endpoint():
    """Test the /matches endpoint returns a list of matches."""
    response = requests.get(f"{API_URL}/matches")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # If we have matches, check their structure
    if len(data) > 0:
        match = data[0]
        assert 'match_id' in match
        assert 'team1' in match
        assert 'team2' in match

def test_match_details_endpoint():
    """Test the /match/<match_id> endpoint returns match details."""
    # First get a match ID from the matches endpoint
    response = requests.get(f"{API_URL}/match/1")
    assert response.status_code == 200
    data = response.json()
    
    # Check the structure of the match details
    assert 'match_id' in data
    assert 'team1' in data
    assert 'team2' in data
    assert 'referees' in data
    assert isinstance(data['referees'], list)

if __name__ == "__main__":
    # Add a delay to ensure the API service is fully up
    print("Waiting for API service to be ready...")
    time.sleep(5)
    
    # Run the tests
    pytest.main(["-v", __file__])
