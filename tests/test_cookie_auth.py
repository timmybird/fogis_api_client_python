import unittest
from unittest.mock import MagicMock, patch

import requests

from fogis_api_client.fogis_api_client import FogisApiClient, FogisLoginError


class TestCookieAuth(unittest.TestCase):
    """Test cases for cookie-based authentication in FogisApiClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_cookies = {
            "FogisMobilDomarKlient.ASPXAUTH": "test_auth_cookie",
            "ASP.NET_SessionId": "test_session_id",
        }

    def test_init_with_cookies(self):
        """Test initializing the client with cookies."""
        client = FogisApiClient(cookies=self.test_cookies)
        self.assertEqual(client.cookies, self.test_cookies)
        self.assertIsNone(client.username)
        self.assertIsNone(client.password)

    def test_init_with_credentials(self):
        """Test initializing the client with username and password."""
        client = FogisApiClient(username="test_user", password="test_pass")
        self.assertIsNone(client.cookies)
        self.assertEqual(client.username, "test_user")
        self.assertEqual(client.password, "test_pass")

    def test_init_with_no_auth(self):
        """Test initializing the client with neither cookies nor credentials."""
        with self.assertRaises(ValueError):
            FogisApiClient()

    @patch("requests.Session.post")
    def test_login_with_cookies(self, mock_post):
        """Test login method when client is initialized with cookies."""
        client = FogisApiClient(cookies=self.test_cookies)
        cookies = client.login()
        self.assertEqual(cookies, self.test_cookies)
        mock_post.assert_not_called()  # Login should not be attempted

    def test_login_with_credentials(self):
        """Test login method when client is initialized with credentials."""
        # Save the original methods
        original_get = requests.Session.get
        original_post = requests.Session.post

        # Create mock responses
        mock_get_response = MagicMock()
        mock_get_response.text = (
            '<input name="__VIEWSTATE" value="test_viewstate" />'
            '<input name="__EVENTVALIDATION" value="test_eventvalidation" />'
        )
        mock_get_response.raise_for_status = lambda: None

        mock_post_response = MagicMock()
        mock_post_response.raise_for_status = lambda: None

        # Create mock cookies
        mock_cookies = {
            "FogisMobilDomarKlient.ASPXAUTH": "test_auth_cookie",
            "ASP.NET_SessionId": "test_session_id",
        }

        # Define mock methods
        def mock_get(self, url, **kwargs):
            return mock_get_response

        def mock_post(self, url, **kwargs):
            # Set up the mock cookies
            self.cookies = MagicMock()
            self.cookies.items = lambda: list(mock_cookies.items())
            self.cookies.__contains__ = lambda self, key: key in mock_cookies
            return mock_post_response

        # Apply the mocks
        requests.Session.get = mock_get
        requests.Session.post = mock_post

        try:
            client = FogisApiClient(username="test_user", password="test_pass")
            cookies = client.login()

            # Verify cookies were set
            self.assertIsNotNone(cookies)
            self.assertIn("FogisMobilDomarKlient.ASPXAUTH", cookies)
        finally:
            # Restore original methods
            requests.Session.get = original_get
            requests.Session.post = original_post

    @patch("fogis_api_client.fogis_api_client.FogisApiClient._api_request")
    def test_validate_cookies_valid(self, mock_api_request):
        """Test validate_cookies method with valid cookies."""
        mock_api_request.return_value = {"matcher": []}

        client = FogisApiClient(cookies=self.test_cookies)
        result = client.validate_cookies()

        self.assertTrue(result)
        mock_api_request.assert_called_once()

    @patch("fogis_api_client.fogis_api_client.FogisApiClient._api_request")
    def test_validate_cookies_invalid(self, mock_api_request):
        """Test validate_cookies method with invalid cookies."""
        mock_api_request.side_effect = FogisLoginError("Invalid session")

        client = FogisApiClient(cookies=self.test_cookies)
        result = client.validate_cookies()

        self.assertFalse(result)
        mock_api_request.assert_called_once()

    def test_validate_cookies_no_cookies(self):
        """Test validate_cookies method with no cookies."""
        client = FogisApiClient(username="test_user", password="test_pass")
        result = client.validate_cookies()

        self.assertFalse(result)

    def test_get_cookies(self):
        """Test get_cookies method."""
        client = FogisApiClient(cookies=self.test_cookies)
        cookies = client.get_cookies()

        self.assertEqual(cookies, self.test_cookies)

    def test_api_request_with_cookies(self):
        """Test _api_request method when client is initialized with cookies."""
        # Create a mock for the _api_request method that returns a valid response
        original_api_request = FogisApiClient._api_request

        def mock_api_request(self, url, payload=None, method="POST"):
            if url.endswith("HamtaMatchLista"):
                return {"matcher": []}  # Return a valid response with the 'matcher' key
            return {"test": "data"}

        # Patch the _api_request method
        FogisApiClient._api_request = mock_api_request

        try:
            client = FogisApiClient(cookies=self.test_cookies)
            result = client.fetch_matches_list_json()

            self.assertEqual(result, [])
        finally:
            # Restore the original method
            FogisApiClient._api_request = original_api_request


if __name__ == "__main__":
    unittest.main()
