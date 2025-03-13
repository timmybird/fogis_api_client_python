import unittest
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime, timedelta, date
import requests

from fogis_api_client.fogis_api_client import FogisApiClient, FogisDataError, FogisAPIRequestError, FogisLoginError


class MockResponse:
    """
    A mock class to simulate requests.Response for testing.
    """

    def __init__(self, json_data, status_code):
        self._json_data = MagicMock(return_value=json_data)  # Make _json_data a MagicMock
        self.status_code = status_code

    def json(self):
        returned_json_data = self._json_data()  # Call the MagicMock to get the return value
        return returned_json_data

    def raise_for_status(self):
        if 400 <= self.status_code < 600:  # Simulate raise_for_status behavior
            raise requests.exceptions.HTTPError(f"Mocked HTTP Error: {self.status_code}", response=None)


def generate_synthetic_matches_data(num_matches=3):
    """Generates synthetic match list data with referees and team contacts for testing."""
    matches = []
    for i in range(num_matches):
        match_id = 1000 + i
        team1_id = 2000 + i
        team2_id = 3000 + i
        team1_name = f"Synthetic Team 1 - {i + 1}"
        team2_name = f"Synthetic Team 2 - {i + 1}"

        match = {
            "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchJSON",
            "value": f"Synthetic Match {i + 1}",
            "label": f"Synthetic Match {i + 1} Label",
            "matchid": match_id,
            "matchnr": f"SYNTHETIC{match_id}",
            "fotbollstypid": 1,
            "matchlag1id": team1_id,
            "lag1namn": team1_name,
            "matchlag2id": team2_id,
            "lag2namn": team2_name,
            "speldatum": "2024-01-20",
            "avsparkstid": "15:00",
            "domaruppdraglista": generate_synthetic_referees_data(match_id=match_id, num_referees=3),
            # Generate synthetic referees
            "kontaktpersoner": generate_synthetic_team_contacts_data(team1_id, team1_name, num_contacts=2) +
                               generate_synthetic_team_contacts_data(team2_id, team2_name, num_contacts=2),
            # Generate synthetic contacts for both teams
        }
        matches.append(match)
    return matches


def generate_synthetic_team_players_data(num_players=5):
    """Generates synthetic team players list data for testing."""
    players = []
    for i in range(num_players):
        player_id = 6000 + i
        player = {
            "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchdeltagareJSON",
            "matchdeltagareid": 50000 + i,
            "matchid": 0,  # Match ID will be set in the test
            "matchlagid": 0,  # Team ID will be set in the test
            "spelareid": player_id,
            "trojnummer": i + 1,
            "fornamn": f"Synthetic Player {i + 1}",
            "efternamn": "PlayerLastname",
            # ... (add other relevant player fields with synthetic values as needed) ...
        }
        players.append(player)
    return players


def generate_synthetic_team_officials_data(team_id, team_name,
                                           num_officials=2):  # Modified to accept team_id, team_name
    """Generates synthetic team officials list data for testing."""
    officials = []
    official_roles = ["Lagledare", "Tränare"]  # Example official roles
    for i in range(num_officials):
        official_id = 7000 + i
        official = {
            "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchlagledareJSON",
            "matchlagledareid": 60000 + i,
            "matchid": 0,  # Match ID will be set in the test
            "matchlagid": team_id,  # Team ID now included
            "personid": official_id,
            "fornamn": f"Synthetic Official {i + 1} - Team {team_name}",  # Team name in official name
            "efternamn": "OfficialLastname",
            "lagrollnamn": official_roles[i % len(official_roles)],  # Cycle through roles
            # ... (add other official fields with synthetic values) ...
        }
        officials.append(official)
    return officials


def generate_synthetic_team_contacts_data(team_id, team_name, num_contacts=2):  # NEW function for team contacts
    """Generates synthetic team contacts list data for testing."""
    contacts = []
    for i in range(num_contacts):
        contact = {
            "lagid": team_id,  # Team ID now included
            "lagnamn": team_name,  # Team name now included
            "personid": 50000 + i,
            "personnamn": f"Synthetic Contact {i + 1} - Team {team_name}",  # Team name in contact name
            "telefon": f"070-123-456{i}",
            "epostadress": f"contact{i + 1}@synthetic-team.com",
            "foreningId": team_id // 10,  # Example synthetic foreningId
            # ... (add other relevant contact fields with synthetic values as needed) ...
        }
        contacts.append(contact)
    return contacts


def generate_synthetic_referees_data(match_id, num_referees=3):  # NEW function for referees, accepts match_id
    """Generates synthetic referee list data for testing."""
    referees = []
    referee_roles = ["Huvuddomare", "Assisterande 1", "Assisterande 2"]  # Example referee roles
    for i in range(num_referees):
        referee_id = 9000 + i
        referee = {
            "domaruppdragid": 70000 + i,
            "matchid": match_id,  # Match ID now included - important for consistency testing
            "matchnr": f"SYNTHETIC-REF-{match_id}",  # Synthetic match number for referees
            "domarrollid": i + 1,
            "domarrollnamn": referee_roles[i % len(referee_roles)],
            "domareid": referee_id,
            "personid": 80000 + i,
            "personnamn": f"Synthetic Referee {i + 1}",
            "namn": f"Synthetic Referee {i + 1} Name - Redundant",  # Added redundant 'namn' field
            "domarnr": f"DOM{referee_id}"
            # ... (add other relevant referee fields with synthetic values) ...
        }
        referees.append(referee)
    return referees


def generate_synthetic_match_events_data(num_events=10):
    """Generates synthetic match events list data for testing."""
    events = []
    event_types = ["Spelmål", "Varning", "Byte ut", "Byte in"]  # Example event types
    for i in range(num_events):
        event_id = 8000 + i
        event = {
            "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchhandelseJSON",
            "matchhandelseid": event_id,
            "matchid": 0,  # Match ID will be set in the test
            "matchhandelsetypnamn": event_types[i % len(event_types)],  # Cycle event types
            "matchminut": i + 5,
            "period": 1 if i < 5 else 2,
            "hemmamal": i % 3,  # Example scores
            "bortamal": 0,
            # ... (add other event fields with synthetic values) ...
        }
        events.append(event)
    return events


def generate_synthetic_match_results_data():
    """Generates synthetic match results list data for testing."""
    results = [
        {
            "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchresultatJSON",
            "matchresultattypid": 1,  # Full time
            "matchresultattypnamn": "Slutresultat",
            "matchlag1mal": 3,
            "matchlag2mal": 1
        },
        {
            "__type": "Svenskfotboll.Fogis.Web.FogisMobilDomarKlient.MatchresultatJSON",
            "matchresultattypid": 2,  # Half time
            "matchresultattypnamn": "Resultat efter period 1",
            "matchlag1mal": 1,
            "matchlag2mal": 0
        }
    ]
    return results


class TestFogisApiClient(unittest.TestCase):

    def setUp(self):
        self.client = FogisApiClient("testuser", "testpassword")

        # Create a mock session
        mock_session = Mock()

        # Mock session.get and session.post - return value will be set in individual tests
        mock_session.get = MagicMock()
        mock_session.post = MagicMock()

        # Mock session.cookies to behave like a dictionary and have a 'set' method
        mock_session.cookies = MagicMock(spec=dict)
        mock_session.cookies.set = MagicMock()

        self.client.session = mock_session
        self.client.cookies = {
            'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}  # Keep this for now, might be redundant

    def test_fetch_matches_list_json_success(self):
        """Unit test for fetch_matches_list_json success."""
        # Correct mock setup: return MockResponse instance
        mock_api_response = MockResponse(json_data={'d': {'matchlista': [{'matchid': 1}, {'matchid': 2}]}},
                                         status_code=200)
        self.client.session.post.return_value = mock_api_response  # Correct: mock session.post to return MockResponse

        matches_list = self.client.fetch_matches_list_json()
        self.assertEqual(matches_list, [{'matchid': 1}, {'matchid': 2}])
        self.client.session.post.assert_called_once()

    def test_fetch_team_players_json(self):
        """Test fetching team players list from API and validate data structure using SYNTHETIC DATA."""
        team_id_to_test = 12345
        sample_players_data = generate_synthetic_team_players_data(num_players=7)
        sample_response_data = sample_players_data  # No need to wrap in 'd' here anymore for the mock response data itself

        # Correct mock response for team players - just the list (as _api_request will wrap in 'd')
        mock_api_response = MockResponse(json_data={'d': sample_response_data}, status_code=200)
        self.client.session.post.return_value = mock_api_response

        players_list = self.client.fetch_team_players_json(team_id_to_test)

        self.assertIsNotNone(players_list)
        self.assertIsInstance(players_list, list)  # <--- Corrected assertion: expect a list
        self.assertEqual(len(players_list), 7)  # Check list length

        # --- Validate the first player in the list ---
        first_player = players_list[0]  # <--- Access list elements directly
        self.assertIsInstance(first_player, dict)
        self.assertEqual(first_player["spelareid"], 6000)
        self.assertEqual(first_player["fornamn"], "Synthetic Player 1")
        self.assertEqual(first_player["efternamn"], "PlayerLastname")
        self.assertEqual(first_player["trojnummer"], 1)
        self.assertEqual(first_player["matchlagid"], 0)
        last_player = players_list[-1]
        self.assertIsInstance(last_player, dict)
        self.assertEqual(last_player["spelareid"], 6006)
        self.assertEqual(last_player["fornamn"], "Synthetic Player 7")
        self.assertEqual(last_player["efternamn"], "PlayerLastname")
        self.assertEqual(last_player["trojnummer"], 7)
        self.assertEqual(last_player["matchlagid"], 0)
        for player in players_list:
            self.assertIsInstance(player, dict)
            self.assertIn("spelareid", player)
            self.assertIn("fornamn", player)
            self.assertIn("efternamn", player)
            self.assertIn("trojnummer", player)
            self.assertIn("matchlagid", player)
            self.assertIn("matchdeltagareid", player)

    def test_fetch_team_officials_json(self):
        """Test fetching team officials list from API and validate data structure."""
        team_id = 123456
        sample_officials_response = generate_synthetic_team_officials_data(team_id=team_id, team_name="Test Team")
        # Correct mock setup: MockResponse instance
        mock_api_response = MockResponse(json_data={'d': sample_officials_response}, status_code=200)
        self.client.session.post.return_value = mock_api_response

        officials_data_list = self.client.fetch_team_officials_json(team_id)

        self.assertIsNotNone(officials_data_list)
        self.assertIsInstance(officials_data_list, list)  # <--- Corrected assertion: expect list
        self.assertEqual(len(officials_data_list), 2)  # Expect 2 officials

        # --- Validate the first official in the list ---
        first_official = officials_data_list[0]  # <--- Access as list element
        self.assertIsInstance(first_official, dict)
        self.assertEqual(first_official["matchlagledareid"], 60000)
        self.assertEqual(first_official["fornamn"], "Synthetic Official 1 - Team Test Team")
        self.assertEqual(first_official["efternamn"], "OfficialLastname")
        self.assertEqual(first_official["lagrollnamn"], "Lagledare")
        self.assertEqual(first_official["matchlagid"], team_id)
        last_official = officials_data_list[-1]
        self.assertIsInstance(last_official, dict)
        self.assertEqual(last_official["matchlagledareid"], 60001)
        self.assertEqual(last_official["fornamn"], "Synthetic Official 2 - Team Test Team")
        self.assertEqual(last_official["efternamn"], "OfficialLastname")
        self.assertEqual(last_official["lagrollnamn"], "Tränare")
        self.assertEqual(last_official["matchlagid"], team_id)
        for official in officials_data_list:
            self.assertIsInstance(official, dict)
            self.assertIn("matchlagledareid", official)
            self.assertIn("fornamn", official)
            self.assertIn("efternamn", official)
            self.assertIn("lagrollnamn", official)
            self.assertIn("matchlagid", official)

    def test_fetch_match_events_json(self):
        """Test fetching match events list from API and validate data structure."""
        sample_events_response = generate_synthetic_match_events_data(num_events=20)
        # Correct mock setup: MockResponse instance
        mock_api_response = MockResponse(json_data={'d': sample_events_response}, status_code=200)
        self.client.session.post.return_value = mock_api_response  # Correct mock session.post

        match_id_to_test = 5760945
        events_list = self.client.fetch_match_events_json(match_id_to_test)

        self.assertIsNotNone(events_list)
        self.assertIsInstance(events_list, list)  # <--- Corrected assertion: expect list
        self.assertEqual(len(events_list), 20)  # Expect 20 events

        # --- Validate the first event in the list ---
        first_event = events_list[0]  # <--- Access as list element
        self.assertIsInstance(first_event, dict)
        self.assertEqual(first_event["matchhandelseid"], 8000)
        self.assertEqual(first_event["matchhandelsetypnamn"], "Spelmål")
        self.assertEqual(first_event["matchminut"], 5)
        self.assertEqual(first_event["period"], 1)
        self.assertEqual(first_event["matchid"], 0)
        last_event = events_list[-1]
        self.assertIsInstance(last_event, dict)
        self.assertEqual(last_event["matchhandelseid"], 8019)
        self.assertEqual(last_event["matchhandelsetypnamn"], "Byte in")
        self.assertEqual(last_event["matchminut"], 24)
        self.assertEqual(last_event["period"], 2)
        for event in events_list:
            self.assertIsInstance(event, dict)
            self.assertIn("matchhandelseid", event)
            self.assertIn("matchhandelsetypnamn", event)
            self.assertIn("matchminut", event)
            self.assertIn("period", event)

    def test_fetch_match_result_json(self):
        """Test fetching match results list from API and validate data structure."""
        sample_result_data = generate_synthetic_match_results_data()
        # Correct mock setup: MockResponse instance
        mock_api_response = MockResponse(json_data={'d': sample_result_data}, status_code=200)
        self.client.session.post.return_value = mock_api_response  # Correct mock session.post

        match_id_to_test = 5747111
        results_list = self.client.fetch_match_result_json(match_id_to_test)

        self.assertIsNotNone(results_list)
        self.assertIsInstance(results_list, list)
        self.assertEqual(len(results_list), 2)
        full_time_result = results_list[0]
        self.assertIsInstance(full_time_result, dict)
        self.assertEqual(full_time_result["matchresultattypid"], 1)
        self.assertEqual(full_time_result["matchresultattypnamn"], "Slutresultat")
        self.assertEqual(full_time_result["matchlag1mal"], 3)
        self.assertEqual(full_time_result["matchlag2mal"], 1)
        halftime_result = results_list[1]
        self.assertIsInstance(halftime_result, dict)
        self.assertEqual(halftime_result["matchresultattypid"], 2)
        self.assertEqual(halftime_result["matchresultattypnamn"], "Resultat efter period 1")
        self.assertEqual(halftime_result["matchlag1mal"], 1)
        self.assertEqual(halftime_result["matchlag2mal"], 0)
        for result in results_list:
            self.assertIsInstance(result, dict)
            self.assertIn("matchresultattypid", result)
            self.assertIn("matchresultattypnamn", result)
            self.assertIn("matchlag1mal", result)
            self.assertIn("matchlag2mal", result)

    def test_report_regular_goal_event_payload(self):
        """Unit test for report_match_event - payload verification for Regular Goal event."""
        MagicMock(spec=FogisApiClient)
        mock_login = MagicMock(return_value=True)
        with patch.object(FogisApiClient, "login", new=mock_login):
            # Correct mock setup: MockResponse instance (even for empty response)
            mock_api_response = MockResponse(json_data={"d": None}, status_code=200)
            with patch.object(FogisApiClient, "_api_request", new=MagicMock(
                    return_value=mock_api_response)) as mocked_request:  # Mock _api_request to return MockResponse
                event_data = {
                    "matchhandelseid": 0,
                    "matchid": 12345,
                    "period": 1,
                    "matchminut": 30,
                    "sekund": 0,
                    "matchhandelsetypid": 6,  # 6 = Regular Goal
                    "matchlagid": 22222,
                    "spelareid": 77777,
                    "spelareid2": 0,
                    "hemmamal": 1,
                    "bortamal": 0,
                    "planpositionx": "-1",
                    "planpositiony": "-1",
                    "matchdeltagareid": 11111,
                    "matchdeltagareid2": 0,
                    "fotbollstypId": 1,
                    "relateradTillMatchhandelseID": 0
                }
                expected_payload = event_data
                self.client.report_match_event(event_data)
                mocked_request.assert_called_once()
                request_payload = mocked_request.call_args.args[1]
                self.assertEqual(request_payload, expected_payload, "Request payload does not match expected payload")

    def test_login_success(self):
        """Unit test for successful login."""
        client = FogisApiClient("testuser", "testpass")

        mocked_session = self.client.session  # Get the mock session from setUp

        # Mock session.get (for initial login page request)
        mock_initial_response = MockResponse(json_data=None, status_code=200)
        mock_initial_response.text = '<form id="aspnetForm"><input type="hidden" name="__VIEWSTATE" value="mock_viewstate"></form>'
        mocked_session.get.return_value = mock_initial_response

        # Mock session.post (for login POST request - successful redirect)
        mock_login_response = MockResponse(json_data=None, status_code=302)
        mock_login_response.headers = {'Location': '/mdk/default.aspx'}
        mock_login_response.cookies = {
            'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}  # Simulate successful login cookie
        mocked_session.post.return_value = mock_login_response

        with patch.object(client, "session", new=mocked_session), \
                patch("requests.utils.dict_from_cookiejar",
                      new=MagicMock(return_value={'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'})):
            cookies = client.login()

        # Assertions:
        self.assertIsNotNone(cookies)
        self.assertIn('FogisMobilDomarKlient.ASPXAUTH', cookies)
        mocked_session.get.assert_called()
        mocked_session.post.assert_called_once()

    def test_login_failure_invalid_credentials(self):
        """Unit test for login failure due to invalid credentials."""
        client = FogisApiClient("wronguser", "wrongpass")
        mocked_session = self.client.session  # Get mock session from setUp
        mock_initial_response = MockResponse(json_data=None, status_code=200)
        mock_initial_response.text = '<form id="aspnetForm"><input type="hidden" name="__VIEWSTATE" value="mock_viewstate"></form>'
        mocked_session.get.return_value = mock_initial_response
        mock_login_response = MockResponse(json_data=None, status_code=200)
        mock_login_response.cookies = {}
        mocked_session.post.return_value = mock_login_response
        with patch.object(client, "session", new=mocked_session), \
                patch("requests.utils.dict_from_cookiejar", new=MagicMock(return_value={})):
            with self.assertRaises(FogisLoginError) as excinfo:
                client.login()
        self.assertIn("Login failed", str(excinfo.exception))
        mocked_session.post.assert_called_once()

    def test_api_request_post_success(self):
        """Unit test for successful _api_request POST."""
        client = FogisApiClient("testuser", "testpass")
        mock_session_instance = self.client.session  # Get mock session from setUp
        # Correct mock setup: MockResponse instance
        mock_api_response = MockResponse(json_data={'d': {'key': 'value'}}, status_code=200)
        mock_session_instance.post.return_value = mock_api_response  # Correct mock session.post

        url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/SomeEndpoint"
        payload = {"param1": "value1"}
        response_data = self.client._api_request(url, payload, method='POST')
        self.assertEqual(response_data, {'key': 'value'})
        mock_session_instance.post.assert_called_once_with(
            url,
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://fogis.svenskfotboll.se',
                'Referer': 'https://fogis.svenskfotboll.se/mdk/',
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie'
            },
            json=payload
        )
        called_args, called_kwargs = mock_session_instance.post.call_args
        called_headers = called_kwargs['headers']
        self.assertIn('Cookie', called_headers)
        self.assertIn('FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie', called_headers['Cookie'])

    def test_api_request_get_success(self):
        """Unit test for successful _api_request GET."""
        client = FogisApiClient("testuser", "testpass")
        mock_session_instance = self.client.session  # Get mock session from setUp
        # Correct mock setup: MockResponse instance
        mock_api_response = MockResponse(json_data={'d': {'items': [1, 2, 3]}}, status_code=200)
        mock_session_instance.get.return_value = mock_api_response  # Correct mock session.get

        url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/GetSomeData"
        response_data = self.client._api_request(url, method='GET')
        self.assertEqual(response_data, {'items': [1, 2, 3]})
        mock_session_instance.get.assert_called_once_with(
            url,
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Origin': 'https://fogis.svenskfotboll.se',
                'Referer': 'https://fogis.svenskfotboll.se/mdk/',
                'X-Requested-With': 'XMLHttpRequest',
                'Cookie': 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie'
            }
        )

    def test_api_request_not_logged_in(self):
        """Unit test for _api_request when not logged in (REFINED)."""
        client = FogisApiClient("testuser", "testpass")
        client.cookies = None  # Explicitly set cookies to None

        # Mock _api_request to directly RAISE FogisLoginError when called
        mocked_api_request = MagicMock(
            side_effect=FogisLoginError("Not logged in test case"))  # Mock to raise FogisLoginError

        with patch.object(FogisApiClient, "_api_request",
                          new=mocked_api_request) as mocked_request:  # Patch _api_request
            with self.assertRaises(FogisLoginError) as excinfo:  # Assert FogisLoginError is raised
                self.client._api_request(
                    "https://fogis.svenskfotboll.se/mdk/SomeEndpoint")  # Call _api_request (mocked)

        self.assertEqual(mocked_request.call_count, 1)  # Verify _api_request mock was called
        self.assertIn("Not logged in", str(excinfo.exception))  # Assert correct error message

    def test_api_request_http_error(self):
        """Unit test for _api_request handling HTTP errors."""
        client = FogisApiClient("testuser", "testpass")
        mock_session_instance = self.client.session  # Get mock session from setUp
        # Correct mock setup: MockResponse instance for error
        mock_api_response = MockResponse(json_data=None, status_code=404)
        mock_session_instance.post.return_value = mock_api_response
        mock_session_instance.post.side_effect = requests.exceptions.HTTPError("HTTP Error 404")

        with patch.object(client, 'session', new=mock_session_instance):
            url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/BrokenEndpoint"
            payload = {"param1": "value1"}
            with self.assertRaises(FogisAPIRequestError) as excinfo:
                self.client._api_request(url, payload, method='POST')
        self.assertIn("API request error", str(excinfo.exception))

    def test_api_request_invalid_json_response(self):
        """Unit test for _api_request handling invalid JSON response (missing 'd')."""
        client = FogisApiClient("testuser", "testpass")
        mock_session_instance = self.client.session  # Get mock session from setUp
        # Correct mock setup: MockResponse instance for invalid JSON
        mock_api_response = MockResponse(json_data={'unexpected_key': 'value'}, status_code=200)
        mock_session_instance.post.return_value = mock_api_response

        with patch.object(client, 'session', new=mock_session_instance):
            url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/BadJsonResponse"
            payload = {"param1": "value1"}
            with self.assertRaises(FogisDataError) as excinfo:
                self.client._api_request(url, payload, method='POST')
        self.assertIn("Unexpected JSON response format", str(excinfo.exception))

    def test_fetch_matches_list_json_call_args(self):
        """Unit test for fetch_matches_list_json argument verification."""
        # No need to mock MockResponse here, testing call args, not API response data
        mock_api_request = MagicMock(return_value={'matchlista': []})
        with patch.object(FogisApiClient, "_api_request", new=mock_api_request) as mocked_request:
            self.client.fetch_matches_list_json()
        mocked_request.assert_called_once()
        call_args = mocked_request.call_args
        args = call_args.args
        kwargs = call_args.kwargs
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0],
                         "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/GetMatcherAttRapportera")
        self.assertIsInstance(args[1], dict)
        # self.assertNotIn('method', kwargs) or self.assertEqual(kwargs['method'], 'POST')

    def test_fetch_matches_list_json_api_call_only(self):  # Focused test - API call only
        """Unit test for fetch_matches_list_json verifying API call (no filtering)."""
        mock_api_request = MagicMock(return_value={'matchlista': []})  # Mock API request - empty response is fine
        with patch.object(FogisApiClient, "_api_request", new=mock_api_request) as mocked_request:
            self.client.fetch_matches_list_json()  # Call fetch_matches_list_json WITHOUT filter argument

        mocked_request.assert_called_once()  # Verify _api_request was called

        call_args = mocked_request.call_args
        args = call_args.args

        self.assertEqual(len(args), 2, "Incorrect number of arguments passed to _api_request")
        self.assertEqual(args[0], "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/GetMatcherAttRapportera",
                         "Incorrect API URL")
        self.assertIsInstance(args[1], dict, "Payload is not a dictionary")

        call_filter = args[1]['filter']  # Get the filter dictionary from call_args
        self.assertEqual(8, len(call_filter), "Incorrect number of parameters in filter dictionary (8 expected)")
        self.assertEqual(call_filter.get('typ'), 'alla', "Default 'typ' parameter incorrect")
        self.assertEqual(call_filter.get('datumTyp'), 0, "Default 'datumTyp' parameter incorrect")
        self.assertIn('datumFran', call_filter,
                      "Missing 'datumFran' parameter")  # Just check for presence, not exact value (date is dynamic)
        self.assertIn('datumTill', call_filter, "Missing 'datumTill' parameter")  # Same for 'datumTill'
        self.assertIn('status', call_filter)  # <--- Verify 'status' filter is in filter (as default)
        self.assertIn('alderskategori', call_filter)  # <--- Verify 'alderskategori' filter is in filter
        self.assertIn('kon', call_filter)  # <--- Verify 'kon' filter is in filter

    def test_fetch_matches_list_json_server_date_filter_call_args(self):
        """Unit test for fetch_matches_list_json verifying server-side date filter arguments."""
        mock_api_request = MagicMock(return_value={'matchlista': []})
        with patch.object(FogisApiClient, "_api_request", new=mock_api_request) as mocked_request:
            filter_payload = {  # Create a filter dictionary for date range
                "datumFran": "2024-04-01",
                "datumTill": "2024-04-07",
                "datumTyp": 1,  # Fixed dates
                "sparadDatum": "2024-04-17"
            }
            self.client.fetch_matches_list_json(
                filter=filter_payload)  # Call fetch_matches_list_json WITH filter dictionary

        mocked_request.assert_called_once()
        call_args = mocked_request.call_args
        args = call_args.args
        self.assertEqual(len(args), 2)
        self.assertIsInstance(args[1], dict)
        call_filter = args[1]['filter']  # Get the filter dictionary from call_args

        # --- Verify payload dictionary content - check for date range filters ---
        self.assertEqual(8, len(call_filter), "Incorrect number of parameters in filter dictionary (8 expected)")
        self.assertEqual(call_filter.get('datumFran'), "2024-04-01", "Incorrect 'datumFran' parameter")
        self.assertEqual(call_filter.get('datumTill'), "2024-04-07", "Incorrect 'datumTill' parameter")
        self.assertEqual(call_filter.get('datumTyp'), 1, "Incorrect 'datumTyp' parameter")
        self.assertEqual(call_filter.get('sparadDatum'), "2024-04-17", "Incorrect 'sparadDatum' parameter")
        self.assertEqual(call_filter.get('typ'), 'alla', "Default 'typ' parameter incorrect")  # Also check default 'typ'
        self.assertIn('status', call_filter)
        self.assertIn('alderskategori', call_filter)
        self.assertIn('kon', call_filter)
        self.assertNotIn('fotbollstypid', call_filter, "Unexpected 'fotbollstypid' filter")  # <--- Verify 'fotbollstypid' filter is NOT in filter



if __name__ == '__main__':
    unittest.main()