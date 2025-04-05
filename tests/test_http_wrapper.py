import unittest
from unittest.mock import patch, MagicMock, Mock
import os
import json
import sys
from flask import Flask
from flask.testing import FlaskClient

# Import the Flask app from the HTTP wrapper
import fogis_api_client_http_wrapper


class TestHttpWrapper(unittest.TestCase):
    """Test cases for the HTTP wrapper."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a test client
        self.app = fogis_api_client_http_wrapper.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Mock the FogisApiClient
        self.mock_fogis_client = Mock()
        fogis_api_client_http_wrapper.client = self.mock_fogis_client

        # Set up mock responses
        self.mock_fogis_client.hello_world.return_value = "Hello, brave new world!"
        self.mock_fogis_client.fetch_matches_list_json.return_value = [{"id": "1", "home_team": "Team A", "away_team": "Team B"}]
        self.mock_fogis_client.fetch_match_json.return_value = {"id": "123", "home_team": "Team A", "away_team": "Team B"}

    def test_hello_endpoint(self):
        """Test the /hello endpoint."""
        response = self.client.get('/hello')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Hello, brave new world!"})

    def test_index_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.json, {"status": "ok", "message": "Fogis API Client HTTP Wrapper"})

    @patch('fogis_api_client_http_wrapper.client.fetch_matches_list_json')
    def test_matches_endpoint(self, mock_fetch):
        """Test the /matches endpoint."""
        # Set up the mock
        mock_fetch.return_value = [{"id": "1", "home_team": "Team A", "away_team": "Team B"}]

        # Call the endpoint
        response = self.client.get('/matches')

        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [{"id": "1", "home_team": "Team A", "away_team": "Team B"}])
        mock_fetch.assert_called_once()

    @patch('fogis_api_client_http_wrapper.client.fetch_match_json')
    def test_match_details_endpoint(self, mock_fetch):
        """Test the /match/<match_id> endpoint."""
        # Set up the mock
        mock_fetch.return_value = {"id": "123", "home_team": "Team A", "away_team": "Team B"}

        # Call the endpoint
        response = self.client.get('/match/123')

        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"id": "123", "home_team": "Team A", "away_team": "Team B"})
        mock_fetch.assert_called_once_with("123")

    @patch('fogis_api_client_http_wrapper.client.fetch_match_json')
    def test_match_details_endpoint_error(self, mock_fetch):
        """Test the /match/<match_id> endpoint with an error."""
        # Set up the mock to raise an exception
        mock_fetch.side_effect = Exception("Test error")

        # Call the endpoint
        response = self.client.get('/match/123')

        # Verify the response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Test error"})
        mock_fetch.assert_called_once_with("123")

    @patch('fogis_api_client_http_wrapper.client.fetch_matches_list_json')
    def test_matches_endpoint_error(self, mock_fetch):
        """Test the /matches endpoint with an error."""
        # Set up the mock to raise an exception
        mock_fetch.side_effect = Exception("Test error")

        # Call the endpoint
        response = self.client.get('/matches')

        # Verify the response
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Test error"})
        mock_fetch.assert_called_once()

    def test_invalid_endpoint(self):
        """Test accessing an invalid endpoint."""
        response = self.client.get('/invalid-endpoint')
        self.assertEqual(response.status_code, 404)

    def test_signal_handler(self):
        """Test the signal handler function."""
        # This is a simple test to ensure the function exists and can be called
        # We can't easily test the actual signal handling without complex mocking
        self.assertTrue(callable(fogis_api_client_http_wrapper.signal_handler))


if __name__ == '__main__':
    unittest.main()
