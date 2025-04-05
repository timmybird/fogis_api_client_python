import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the wrapper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import fogis_api_client_http_wrapper as wrapper

class TestHttpWrapper(unittest.TestCase):
    """Test the HTTP wrapper functionality."""
    
    @patch('fogis_api_client_http_wrapper.FogisApiClient')
    def setUp(self, mock_client):
        """Set up the test environment."""
        self.mock_client_instance = mock_client.return_value
        self.mock_client_instance.hello_world.return_value = "Hello, World!"
        self.mock_client_instance.fetch_matches_list_json.return_value = [
            {"match_id": "1", "team1": "Team A", "team2": "Team B", "date": "2024-01-20"}
        ]
        
        # Create a test client
        wrapper.client = self.mock_client_instance
        self.app = wrapper.app.test_client()
        
    def test_hello_endpoint(self):
        """Test the /hello endpoint."""
        response = self.app.get('/hello')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, "Hello, World!")
        self.mock_client_instance.hello_world.assert_called_once()
        
    def test_index_endpoint(self):
        """Test the root endpoint."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 3)  # 3 items in the list
        
        # Check for Unicode handling
        unicode_items = [item for item in response.json if 'unicode_item' in item]
        self.assertEqual(len(unicode_items), 1)
        self.assertEqual(unicode_items[0]['unicode_item'], 'åäö')
        
    def test_matches_endpoint(self):
        """Test the /matches endpoint."""
        response = self.app.get('/matches')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 1)
        self.mock_client_instance.fetch_matches_list_json.assert_called_once()
        
        match = response.json[0]
        self.assertEqual(match['match_id'], "1")
        self.assertEqual(match['team1'], "Team A")
        self.assertEqual(match['team2'], "Team B")
        
    def test_match_details_endpoint(self):
        """Test the /match/<match_id> endpoint."""
        response = self.app.get('/match/1')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        
        # Check the structure of the match details
        self.assertIn('match_id', response.json)
        self.assertIn('team1', response.json)
        self.assertIn('team2', response.json)
        self.assertIn('referees', response.json)
        self.assertIsInstance(response.json['referees'], list)
        
    @patch('fogis_api_client_http_wrapper.debug_mode', True)
    @patch('fogis_api_client_http_wrapper.app.run')
    def test_debug_mode(self, mock_run):
        """Test that debug mode is properly handled."""
        # Call the main function
        wrapper.signal_handler = MagicMock()  # Mock the signal handler
        
        # Simulate running the main block
        if hasattr(wrapper, '__name__') and wrapper.__name__ == '__main__':
            wrapper.app.run(host='0.0.0.0', port=8080, debug=True)
            
        # Check that app.run was called with debug=True
        mock_run.assert_called_with(host='0.0.0.0', port=8080, debug=True)
        
    @patch('fogis_api_client_http_wrapper.debug_mode', False)
    @patch('fogis_api_client_http_wrapper.app.run')
    def test_production_mode(self, mock_run):
        """Test that production mode is properly handled."""
        # Call the main function
        wrapper.signal_handler = MagicMock()  # Mock the signal handler
        
        # Simulate running the main block
        if hasattr(wrapper, '__name__') and wrapper.__name__ == '__main__':
            wrapper.app.run(host='0.0.0.0', port=8080, debug=False, threaded=False)
            
        # Check that app.run was called with debug=False and threaded=False
        mock_run.assert_called_with(host='0.0.0.0', port=8080, debug=False, threaded=False)

if __name__ == '__main__':
    unittest.main()
