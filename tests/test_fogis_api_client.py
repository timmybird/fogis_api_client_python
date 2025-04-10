import unittest
from unittest.mock import patch, MagicMock, Mock
import requests
import json
import logging
import io

from fogis_api_client.fogis_api_client import FogisApiClient, FogisLoginError, FogisAPIRequestError, FogisDataError


class MockResponse:
    """
    A mock class to simulate requests.Response for testing.
    """

    def __init__(self, json_data, status_code):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        if isinstance(self._json_data, Exception):
            raise self._json_data
        return self._json_data

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise requests.exceptions.HTTPError(f"HTTP Error {self.status_code}", response=self)


class TestFogisApiClient(unittest.TestCase):
    """Test cases for the FogisApiClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = FogisApiClient("testuser", "testpassword")

        # Create a mock session
        mock_session = Mock()
        mock_session.get = MagicMock()
        mock_session.post = MagicMock()
        mock_session.cookies = MagicMock(spec=dict)
        mock_session.cookies.set = MagicMock()

        self.client.session = mock_session
        self.client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}  # Simulate being logged in

        # Set up logging capture
        self.log_capture = io.StringIO()
        self.log_handler = logging.StreamHandler(self.log_capture)
        self.logger = logging.getLogger('fogis_api_client.fogis_api_client')
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        """Tear down test fixtures."""
        self.logger.removeHandler(self.log_handler)
        self.log_handler.close()

    def test_login_success(self):
        """Unit test for successful login."""
        # Create a client without cookies
        client = FogisApiClient("testuser", "testpassword")

        # Mock the session
        mocked_session = Mock()
        client.session = mocked_session

        # Mock the get response to return a valid login page
        mock_get_response = Mock()
        mock_get_response.text = '<input name="__VIEWSTATE" value="viewstate_value" /><input name="__EVENTVALIDATION" value="eventvalidation_value" />'
        mocked_session.get.return_value = mock_get_response

        # Mock the post response to simulate successful login
        mock_post_response = Mock()
        mocked_session.post.return_value = mock_post_response

        # Mock the cookies to simulate successful login
        mocked_session.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}

        # Call login
        cookies = client.login()

        # Verify the result
        self.assertEqual(cookies, {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'})
        mocked_session.get.assert_called_once()
        mocked_session.post.assert_called_once()

    def test_login_failure_invalid_credentials(self):
        """Unit test for login failure due to invalid credentials."""
        # Create a client without cookies
        client = FogisApiClient("testuser", "testpassword")

        # Mock the session
        mocked_session = Mock()
        client.session = mocked_session

        # Mock the get response to return a valid login page
        mock_get_response = Mock()
        mock_get_response.text = '<input name="__VIEWSTATE" value="viewstate_value" /><input name="__EVENTVALIDATION" value="eventvalidation_value" />'
        mocked_session.get.return_value = mock_get_response

        # Mock the post response to simulate failed login
        mock_post_response = Mock()
        mocked_session.post.return_value = mock_post_response

        # Mock the cookies to simulate failed login (no auth cookie)
        mocked_session.cookies = {}

        # Call login and expect an exception
        with self.assertRaises(FogisLoginError):
            client.login()

        mocked_session.get.assert_called_once()
        mocked_session.post.assert_called_once()

    def test_api_request_success(self):
        """Unit test for successful _api_request POST."""
        # Mock the session's post method
        mock_session_instance = self.client.session
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SomeEndpoint"
        payload = {"param1": "value1"}

        # Create a mock response
        mock_api_response = MockResponse({"d": '{"key": "value"}'}, 200)
        mock_session_instance.post.return_value = mock_api_response

        # Call _api_request
        response_data = self.client._api_request(url, payload, method='POST')

        # Verify the result
        self.assertEqual(response_data, {"key": "value"})
        mock_session_instance.post.assert_called_once_with(
            url,
            json=payload,
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://fogis.svenskfotboll.se',
                'Referer': f"{FogisApiClient.BASE_URL}/",
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie'
            }
        )

    def test_api_request_get_success(self):
        """Unit test for successful _api_request GET."""
        # Mock the session's get method
        mock_session_instance = self.client.session
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetSomeData"

        # Create a mock response
        mock_api_response = MockResponse({"d": '{"items": [1, 2, 3]}'}, 200)
        mock_session_instance.get.return_value = mock_api_response

        # Call _api_request
        response_data = self.client._api_request(url, method='GET')

        # Verify the result
        self.assertEqual(response_data, {'items': [1, 2, 3]})
        mock_session_instance.get.assert_called_once_with(
            url,
            params=None,
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://fogis.svenskfotboll.se',
                'Referer': f"{FogisApiClient.BASE_URL}/",
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie'
            }
        )

    def test_api_request_http_error(self):
        """Unit test for _api_request handling HTTP errors."""
        # Mock the session's post method
        mock_session_instance = self.client.session
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SomeEndpoint"
        payload = {"param1": "value1"}

        # Create a mock response that raises an HTTP error
        mock_api_response = MockResponse({"error": "Not found"}, 404)
        mock_session_instance.post.return_value = mock_api_response
        mock_api_response.raise_for_status = MagicMock(side_effect=requests.exceptions.HTTPError("HTTP Error 404"))

        # Call _api_request and expect an exception
        with self.assertRaises(FogisAPIRequestError) as excinfo:
            self.client._api_request(url, payload, method='POST')

        self.assertIn("API request failed", str(excinfo.exception))
        mock_session_instance.post.assert_called_once_with(
            url,
            json=payload,
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://fogis.svenskfotboll.se',
                'Referer': f"{FogisApiClient.BASE_URL}/",
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie'
            }
        )

    def test_api_request_invalid_json_response(self):
        """Unit test for _api_request handling invalid JSON response (missing 'd')."""
        # Mock the session's post method
        mock_session_instance = self.client.session
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SomeEndpoint"
        payload = {"param1": "value1"}

        # Create a mock response with invalid JSON (no 'd' key)
        mock_api_response = MockResponse({"not_d": "some_value"}, 200)
        mock_session_instance.post.return_value = mock_api_response

        # Call _api_request and expect the response to be returned as is
        response_data = self.client._api_request(url, payload, method='POST')

        # Verify the result
        self.assertEqual(response_data, {"not_d": "some_value"})

        mock_session_instance.post.assert_called_once_with(
            url,
            json=payload,
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://fogis.svenskfotboll.se',
                'Referer': f"{FogisApiClient.BASE_URL}/",
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie'
            }
        )

    def test_fetch_matches_list_json_success(self):
        """Unit test for fetch_matches_list_json success."""
        # Mock the _api_request method
        self.client._api_request = MagicMock(return_value={"matcher": [{"matchid": 1}, {"matchid": 2}]})

        # Call fetch_matches_list_json
        matches_list = self.client.fetch_matches_list_json()

        # Verify the result
        self.assertEqual(matches_list, [{"matchid": 1}, {"matchid": 2}])
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchLista",
            {}
        )

    def test_fetch_matches_list_json_call_args(self):
        """Unit test for fetch_matches_list_json argument verification."""
        # Mock the _api_request method
        self.client._api_request = MagicMock(return_value={"matcher": []})

        # Call fetch_matches_list_json
        self.client.fetch_matches_list_json()

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchLista",
            {}
        )

    def test_fetch_matches_list_json_api_call_only(self):
        """Unit test for fetch_matches_list_json verifying API call (no filtering)."""
        # Mock the _api_request method
        self.client._api_request = MagicMock(return_value={"matcher": []})

        # Call fetch_matches_list_json WITHOUT filter argument
        self.client.fetch_matches_list_json()  # Call fetch_matches_list_json WITHOUT filter argument

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchLista",
            {}
        )

    def test_fetch_matches_list_json_server_date_filter_call_args(self):
        """Unit test for fetch_matches_list_json verifying server-side date filter arguments."""
        # Mock the _api_request method
        self.client._api_request = MagicMock(return_value={"matcher": []})

        # Call fetch_matches_list_json with filter
        self.client.fetch_matches_list_json(
            filter={
                "datumFran": "2023-01-01",
                "datumTill": "2023-01-31",
                "datumTyp": "match",
                "sparadDatum": "2023-01-15"
            }
        )

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchLista",
            {
                "datumFran": "2023-01-01",
                "datumTill": "2023-01-31",
                "datumTyp": "match",
                "sparadDatum": "2023-01-15"
            }
        )

    def test_fetch_match_result_json(self):
        """Unit test for fetch_match_result_json method."""
        # Mock the _api_request method
        self.client._api_request = MagicMock(return_value=[{"matchresultattypid": 1, "matchlag1mal": 2, "matchlag2mal": 1}])

        # Call fetch_match_result_json
        match_id = 12345
        result_data = self.client.fetch_match_result_json(match_id)

        # Verify the result
        self.assertIsInstance(result_data, list)
        self.assertEqual(len(result_data), 1)
        self.assertEqual(result_data[0]["matchlag1mal"], 2)
        self.assertEqual(result_data[0]["matchlag2mal"], 1)

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatchresultatlista",
            {"matchid": 12345}
        )

    def test_fetch_match_result_json_error(self):
        """Unit test for fetch_match_result_json method with error."""
        # Mock the _api_request method to raise an exception
        self.client._api_request = MagicMock(side_effect=FogisAPIRequestError("API request failed"))

        # Call fetch_match_result_json and expect an exception
        with self.assertRaises(FogisAPIRequestError) as excinfo:
            self.client.fetch_match_result_json(12345)

        # Verify the exception message
        self.assertIn("API request failed", str(excinfo.exception))

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatchresultatlista",
            {"matchid": 12345}
        )

    def test_report_match_result(self):
        """Unit test for report_match_result method."""
        # Mock the _api_request method
        self.client._api_request = MagicMock(return_value={"success": True})

        # Call report_match_result
        result_data = {
            "matchid": "12345",
            "hemmamal": 2,
            "bortamal": 1,
            "halvtidHemmamal": 1,
            "halvtidBortamal": 0
        }
        response = self.client.report_match_result(result_data)

        # Verify the result
        self.assertEqual(response, {"success": True})

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SparaMatchresultatLista",
            {
                "matchid": 12345,  # Should be converted to int
                "hemmamal": 2,
                "bortamal": 1,
                "halvtidHemmamal": 1,
                "halvtidBortamal": 0
            }
        )

    def test_report_match_result_error(self):
        """Unit test for report_match_result method with error."""
        # Mock the _api_request method to raise an exception
        self.client._api_request = MagicMock(side_effect=FogisAPIRequestError("API request failed"))

        # Call report_match_result and expect an exception
        result_data = {
            "matchid": "12345",
            "hemmamal": 2,
            "bortamal": 1
        }
        with self.assertRaises(FogisAPIRequestError) as excinfo:
            self.client.report_match_result(result_data)

        # Verify the exception message
        self.assertIn("API request failed", str(excinfo.exception))

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SparaMatchresultatLista",
            {
                "matchid": 12345,  # Should be converted to int
                "hemmamal": 2,
                "bortamal": 1
            }
        )

    def test_event_types_dictionary(self):
        """Test that the event_types dictionary is present and properly formatted."""
        from fogis_api_client.fogis_api_client import event_types

        # Check that event_types is a dictionary
        self.assertIsInstance(event_types, dict)

        # Check that it has the expected keys and structure
        self.assertIn(6, event_types)  # Regular Goal
        self.assertIn(20, event_types)  # Yellow Card
        self.assertIn(17, event_types)  # Substitution

        # Check the structure of an entry
        self.assertIn("name", event_types[6])
        self.assertIn("goal", event_types[6])
        self.assertEqual(event_types[6]["name"], "Regular Goal")
        self.assertTrue(event_types[6]["goal"])

        # Check a non-goal event
        self.assertFalse(event_types[20]["goal"])

        # Check a control event
        self.assertIn("control_event", event_types[31])
        self.assertTrue(event_types[31]["control_event"])

    def test_report_team_official_action(self):
        """Unit test for report_team_official_action method."""
        # Mock the _api_request method
        self.client._api_request = MagicMock(return_value={"success": True})

        # Call report_team_official_action
        action_data = {
            "matchid": "12345",
            "lagid": "67890",
            "personid": "54321",
            "matchlagledaretypid": "2",  # Example: Yellow card
            "minut": 65
        }
        response = self.client.report_team_official_action(action_data)

        # Verify the result
        self.assertEqual(response, {"success": True})

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SparaMatchlagledare",
            {
                "matchid": 12345,  # Should be converted to int
                "lagid": 67890,  # Should be converted to int
                "personid": 54321,  # Should be converted to int
                "matchlagledaretypid": 2,  # Should be converted to int
                "minut": 65
            }
        )

    def test_report_team_official_action_error(self):
        """Unit test for report_team_official_action method with error."""
        # Mock the _api_request method to raise an exception
        self.client._api_request = MagicMock(side_effect=FogisAPIRequestError("API request failed"))

        # Call report_team_official_action and expect an exception
        action_data = {
            "matchid": "12345",
            "lagid": "67890",
            "personid": "54321",
            "matchlagledaretypid": "2"
        }
        with self.assertRaises(FogisAPIRequestError) as excinfo:
            self.client.report_team_official_action(action_data)

        # Verify the exception message
        self.assertIn("API request failed", str(excinfo.exception))

        # Verify the API call
        self.client._api_request.assert_called_once_with(
            f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SparaMatchlagledare",
            {
                "matchid": 12345,  # Should be converted to int
                "lagid": 67890,  # Should be converted to int
                "personid": 54321,  # Should be converted to int
                "matchlagledaretypid": 2  # Should be converted to int
            }
        )


if __name__ == '__main__':
    unittest.main()
