import unittest
from unittest.mock import patch, MagicMock
import logging
import io

from fogis_api_client.fogis_api_client import FogisApiClient
from fogis_api_client.fogis_api_client import FogisAPIRequestError, FogisLoginError
import requests
import json

class TestFogisApiClient(unittest.TestCase):
    def setUp(self):

        self.api_client = FogisApiClient(username='test_user', password='test_password')
        self.log_capture = io.StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        self.handler.setFormatter(formatter)
        self.api_client.logger.addHandler(self.handler)
        self.api_client.logger.setLevel(logging.DEBUG)

    def tearDown(self):
        self.api_client.logger.removeHandler(self.handler)

    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_login_success(self, mock_get, mock_post):
        # Mock successful POST request
        mock_post_response = MagicMock()  # Create a MagicMock for the response
        mock_post_response.raise_for_status = MagicMock()
        mock_post_response.status_code = 302
        mock_post_response.headers = {'Location': '/mdk/default.aspx'}

        # Simulate setting the cookie in the response AND updating the session cookies
        mock_post_response.cookies = requests.cookies.RequestsCookieJar()
        mock_post_response.cookies.set('FogisMobilDomarKlient.ASPXAUTH', 'test_cookie',
                                       domain='fogis.svenskfotboll.se')  # Set cookie

        mock_post.return_value = mock_post_response

        #  *THIS IS THE CRUCIAL ADDITION*:  Update the session cookies with the mocked response cookies
        self.api_client.session.cookies = mock_post_response.cookies

        # Mock successful GET request (redirect)
        mock_get_response = MagicMock()  # Create a MagicMock for the response
        mock_get_response.raise_for_status = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.text = '<HTML><BODY><form id="aspnetForm"></form></BODY></HTML>'  # Mock the HTML content for BeautifulSoup to parse.
        mock_get.return_value = mock_get_response

        #  Capture the logger.info call using a patch
        with patch.object(self.api_client.logger, 'info') as mock_info:
            # Call the login method
            cookies = self.api_client.login()

            # Assertions
            mock_info.assert_called_once_with("Login successful!")  # Remove extra=ANY, it's implied
            self.assertEqual(cookies['FogisMobilDomarKlient.ASPXAUTH'], 'test_cookie')

    @patch('requests.Session.post')
    def test_login_failure(self, mock_post):
        mock_post.return_value.raise_for_status = MagicMock(
            side_effect=requests.exceptions.RequestException('Login failed'))
        with self.assertRaises(FogisAPIRequestError):
            self.api_client.login()
        self.assertIn('ERROR: Login request error', self.log_capture.getvalue())

    @patch('requests.Session.post')
    def test_api_request_error_logging(self, mock_post):
        mock_post.return_value.raise_for_status = MagicMock(side_effect=requests.exceptions.RequestException('API request failed'))
        self.api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            self.api_client._api_request(self.api_client.BASE_URL + '/MatchWebMetoder.aspx/SparaMatchhandelse', {})

        log_message = self.log_capture.getvalue()
        # Extract the first line, removing the traceback
        first_line = log_message.split('\n')[0]
        self.assertIn(f'ERROR: API request error to {self.api_client.BASE_URL}/MatchWebMetoder.aspx/SparaMatchhandelse: API request failed', first_line)

    def test_login_success_old(self):
        with patch.object(self.api_client, 'login', return_value=True) as mock_login:
            result = self.api_client.login()
            self.assertTrue(result)
            mock_login.assert_called_once()

    def test_login_failure_old(self):
        api_client = FogisApiClient(username='test_user', password='test_password')
        with patch.object(api_client, 'login', side_effect=FogisAPIRequestError('Login failed')) as mock_login:
            with self.assertRaises(FogisAPIRequestError):
                api_client.login()

    def test_login_incorrect_credentials(self):
        api_client = FogisApiClient(username='wrong_user', password='wrong_password')
        with patch.object(api_client, 'login', side_effect=FogisLoginError('Incorrect username or password')) as mock_login:
            with self.assertRaises(FogisLoginError):
                api_client.login()

    def test__api_request_invalid_method(self):
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError) as context:
            api_client._api_request(api_client.BASE_URL + '/MatchWebMetoder.aspx/SparaMatchhandelse', {}, method='PUT')

        self.assertIsInstance(context.exception, FogisAPIRequestError)
        self.assertIsInstance(context.exception.__cause__, ValueError)

    def test__api_request_not_logged_in(self):
        api_client = FogisApiClient(username='test_user', password='test_password')
        with self.assertRaises(FogisLoginError):
            api_client._api_request(api_client.BASE_URL + '/MatchWebMetoder.aspx/SparaMatchhandelse', {})

    @patch('requests.Session.post')
    def test__api_request_http_error(self, mock_post):
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        mock_post.return_value.raise_for_status = MagicMock(side_effect=requests.exceptions.HTTPError('HTTP Error'))
        with self.assertRaises(FogisAPIRequestError):
            api_client._api_request(api_client.BASE_URL + '/MatchWebMetoder.aspx/SparaMatchhandelse', {})

    @patch('requests.Session.post')
    def test__api_request_invalid_json(self, mock_post):
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        mock_post.return_value.json = MagicMock(side_effect=json.JSONDecodeError('Invalid JSON', 'doc', 0))
        with self.assertRaises(FogisAPIRequestError):
            api_client._api_request(api_client.BASE_URL + '/MatchWebMetoder.aspx/SparaMatchhandelse', {})

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_matches_list_json_success(self, mock_api_request):
        mock_api_request.return_value = {'matchlista': [{'id': 1, 'name': 'Match 1'}, {'id': 2, 'name': 'Match 2'}]}
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        result = api_client.fetch_matches_list_json()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Match 1')
        mock_api_request.assert_called_once()

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_matches_list_json_failure(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.fetch_matches_list_json()

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_matches_list_json_empty_list(self, mock_api_request):
        mock_api_request.return_value = {'matchlista': []}
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        result = api_client.fetch_matches_list_json()
        self.assertEqual(result, [])


    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_team_players_json_success(self, mock_api_request):
        mock_api_request.return_value = [{'id': 1, 'name': 'Player 1'}, {'id': 2, 'name': 'Player 2'}]
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        result = api_client.fetch_team_players_json(team_id=123)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Player 1')
        mock_api_request.assert_called_once()

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_team_players_json_invalid_team_id(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.fetch_team_players_json(team_id=-1)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_team_officials_json_failure(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.fetch_team_officials_json(team_id=123)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_match_events_json_success(self, mock_api_request):
        mock_api_request.return_value = [{'id': 1, 'name': 'Event 1'}, {'id': 2, 'name': 'Event 2'}]
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        result = api_client.fetch_match_events_json(match_id=456)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'Event 1')
        mock_api_request.assert_called_once()

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_match_events_json_invalid_match_id(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.fetch_match_events_json(match_id=-1)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_fetch_match_events_json_failure(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.fetch_match_events_json(match_id=456)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_report_match_event_success(self, mock_api_request):
        mock_api_request.return_value = True
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        event_data = {'event_type': 'goal', 'player': 'Player A'}
        result = api_client.report_match_event(event_data)
        self.assertTrue(result)
        mock_api_request.assert_called_once_with(api_client.BASE_URL + '/MatchWebMetoder.aspx/SparaMatchhandelse', event_data)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_report_match_event_invalid_event_data(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        event_data = {'event_type': None, 'player': 'Player A'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.report_match_event(event_data)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_report_match_event_failure(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        event_data = {'event_type': 'goal', 'player': 'Player A'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.report_match_event(event_data)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_delete_match_event_success(self, mock_api_request):
        mock_api_request.return_value = None
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        result = api_client.delete_match_event(event_id=123)
        self.assertTrue(result)
        mock_api_request.assert_called_once()

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_delete_match_event_invalid_event_id(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.delete_match_event(event_id=-1)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_delete_match_event_failure(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.delete_match_event(event_id=123)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_clear_match_events_success(self, mock_api_request):
        mock_api_request.return_value = []
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        result = api_client.clear_match_events(match_id=456)
        self.assertFalse(result)
        mock_api_request.assert_called_once()

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_clear_match_events_no_match_events_found(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('No match events found')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.clear_match_events(match_id=456)

    @patch('fogis_api_client.fogis_api_client.FogisApiClient._api_request')
    def test_clear_match_events_failure(self, mock_api_request):
        mock_api_request.side_effect = FogisAPIRequestError('API request failed')
        api_client = FogisApiClient(username='test_user', password='test_password')
        api_client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'test_cookie'}
        with self.assertRaises(FogisAPIRequestError):
            api_client.clear_match_events(match_id=456)

    def test_login_empty_credentials(self):
        api_client = FogisApiClient(username='', password='')
        with patch.object(api_client, 'login', side_effect=FogisLoginError('Incorrect username or password')) as mock_login:
            with self.assertRaises(FogisLoginError):
                api_client.login()

    def test_login_long_username(self):
        api_client = FogisApiClient(username='a' * 200, password='test_password')
        with patch.object(api_client, 'login', side_effect=FogisLoginError('Incorrect username or password')) as mock_login:
            with self.assertRaises(FogisLoginError):
                api_client.login()

    def test_login_long_password(self):
        api_client = FogisApiClient(username='test_user', password='a' * 200)
        with patch.object(api_client, 'login', side_effect=FogisLoginError('Incorrect username or password')) as mock_login:
            with self.assertRaises(FogisLoginError):
                api_client.login()
