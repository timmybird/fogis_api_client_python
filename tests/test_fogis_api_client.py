from unittest.mock import MagicMock, call
import pytest
import requests

from ..fogis_api_client import FogisApiClient, FogisDataError, FogisAPIRequestError, FogisLoginError


from unittest.mock import Mock, call, ANY

class MockResponse:
    """
    A mock class to simulate requests.Response for testing.
    """
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data

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


def test_fetch_matches_list_json(mocker):
    """Test fetching matches list from API and validate data structure."""
    # 1. Generate synthetic match list data
    sample_matches_data = generate_synthetic_matches_data(num_matches=5)  # Generate 5 synthetic matches
    sample_response_data = {'matchlista': sample_matches_data}

    # 2. Mock _api_request (remains the same)
    mocked_api_request = mocker.patch.object(FogisApiClient, "_api_request")
    mocked_api_request.return_value = sample_response_data

    # 3. Create FogisApiClient instance (remains the same)
    api_client = FogisApiClient("testuser", "testpassword")

    # 4. Call fetch_matches_list_json() (remains the same)
    matches_list = api_client.fetch_matches_list_json()

    # 5. Assertions - Validate against SYNTHETIC DATA
    assert matches_list is not None
    assert isinstance(matches_list, list)
    assert len(matches_list) == 5  # Assert length based on num_matches parameter

    # --- Validate the first synthetic match ---
    first_match = matches_list[0]
    assert isinstance(first_match, dict)
    assert first_match["matchid"] == 1000  # Assert against synthetic match ID
    assert first_match["label"] == "Synthetic Match 1 Label"  # Assert against synthetic label
    assert first_match["lag1namn"] == "Synthetic Team 1 - 1"  # Assert against synthetic team name
    # ... (add more assertions for other fields based on synthetic data pattern) ...

    # --- Validate Referees for the first match ---
    first_match_referees = first_match['domaruppdraglista']
    assert isinstance(first_match_referees, list)
    assert len(first_match_referees) == 3  # Expect 3 referees in synthetic data
    first_referee = first_match_referees[0]
    assert isinstance(first_referee, dict)
    assert "domarrollnamn" in first_referee
    assert "personnamn" in first_referee
    # ... (add more assertions for referee data) ...

    # --- Validate Team Contacts for the first match (Team 1) ---
    first_match_team1_contacts = [contact for contact in first_match['kontaktpersoner'] if
                                  contact['lagid'] == first_match['matchlag1id']]  # Filter for Team 1 contacts
    assert isinstance(first_match_team1_contacts, list)
    assert len(first_match_team1_contacts) == 2  # Expect 2 contacts per team in synthetic data
    first_team1_contact = first_match_team1_contacts[0]
    assert isinstance(first_team1_contact, dict)
    assert "lagnamn" in first_team1_contact
    assert "personnamn" in first_team1_contact
    assert first_team1_contact["lagid"] == first_match['matchlag1id']  # Verify correct team ID association
    # ... (add more assertions for team 1 contacts) ...

    # --- Validate Team Contacts for the first match (Team 2) ---
    first_match_team2_contacts = [contact for contact in first_match['kontaktpersoner'] if
                                  contact['lagid'] == first_match['matchlag2id']]  # Filter for Team 2 contacts
    assert isinstance(first_match_team2_contacts, list)
    assert len(first_match_team2_contacts) == 2  # Expect 2 contacts per team
    # ... (add assertions for team 2 contacts) ...

    # --- Optionally, loop through all matches and validate referees/contacts for each match ---
    for match in matches_list:
        assert isinstance(match, dict)
        assert "domaruppdraglista" in match
        assert "kontaktpersoner" in match
        # ... (add more common assertions for referees/contacts in all matches) ...


def test_fetch_team_players_json(mocker):
    """Test fetching team players list from API and validate data structure using SYNTHETIC DATA."""  # Updated description
    # 1. Generate synthetic team players list data
    team_id_to_test = 12345  # Example team ID
    sample_players_data = generate_synthetic_team_players_data(num_players=7)  # Generate 7 synthetic players
    sample_response_data = sample_players_data  # No 'matchlista' wrapping needed for team players

    # 2. Mock _api_request
    mocked_api_request = mocker.patch.object(FogisApiClient, "_api_request")
    mocked_api_request.return_value = {'d': sample_response_data}  # Still wrap in {'d': ...}

    # 3. Create FogisApiClient instance
    api_client = FogisApiClient("testuser", "testpassword")

    # 4. Call fetch_team_players_json()
    players_list = api_client.fetch_team_players_json(team_id_to_test)

    # 5. Assertions - Validate based on the CORRECT sample_players_data
    assert players_list is not None
    assert isinstance(players_list, dict)  # <--- Assert it's a dictionary

    players_data_list = players_list['d']  # <--- Extract the list from 'd'

    assert isinstance(players_data_list, list)  # <--- Now assert the extracted data is a list
    assert len(players_data_list) == 7  # Expect 16 players in the CORRECT sample data

    # --- Validate the first player in the list ---
    first_player = players_data_list[0]  # <--- Use players_data_list
    assert isinstance(first_player, dict)
    assert first_player["spelareid"] == 6000
    assert first_player["fornamn"] == "Synthetic Player 1"
    assert first_player["efternamn"] == "PlayerLastname"
    assert first_player["trojnummer"] == 1
    assert first_player["matchlagid"] == 0  # Corrected key: matchlagid, not lagid

    # --- Optionally, validate the last player ---
    last_player = players_data_list[-1]  # <--- Use players_data_list
    assert isinstance(last_player, dict)
    assert last_player["spelareid"] == 6006
    assert last_player["fornamn"] == "Synthetic Player 7"
    assert last_player["efternamn"] == "PlayerLastname"
    assert last_player["trojnummer"] == 7
    assert last_player["matchlagid"] == 0  # Corrected key: matchlagid

    # --- Validate common properties for all players ---
    for player in players_data_list:  # <--- Iterate over players_data_list
        assert isinstance(player, dict)
        assert "spelareid" in player
        assert "fornamn" in player
        assert "efternamn" in player
        assert "trojnummer" in player
        assert "matchlagid" in player  # Corrected key: matchlagid
        assert "matchdeltagareid" in player  # Added assertion for matchdeltagareid - present in sample data
        # Add more common assertions if needed


def test_fetch_team_officials_json(mocker):
    """Test fetching team officials list from API and validate data structure."""
    # 1. Load sample JSON response
    team_id = 123456
    sample_officials_response = generate_synthetic_team_officials_data(team_id=team_id, team_name="Test Team")

    # 2. Mock _api_request
    mocked_api_request = mocker.patch.object(FogisApiClient, "_api_request")
    mocked_api_request.return_value = {'d': sample_officials_response}  # Return the entire {'d': [...]} structure

    # 3. Create FogisApiClient instance
    api_client = FogisApiClient("testuser", "testpassword")

    # 4. Call fetch_team_officials_json()
    officials_list = api_client.fetch_team_officials_json(team_id)

    # 5. Assertions - Validate based on sample_officials_data
    assert officials_list is not None
    assert isinstance(officials_list, dict)  # <--- Assert that officials_list is a dictionary

    officials_data_list = officials_list['d']  # <--- Extract the list of officials from the 'd' key
    assert isinstance(officials_data_list, list)  # <--- Now assert that officials_data_list is a list
    assert len(officials_data_list) == 2  # Expect 3 officials in sample data

    # --- Validate the first official in the list ---
    first_official = officials_data_list[0]  # <--- Use officials_data_list here, not officials_list
    assert isinstance(first_official, dict)
    assert first_official["matchlagledareid"] == 60000
    assert first_official["fornamn"] == "Synthetic Official 1 - Team Test Team"
    assert first_official["efternamn"] == "OfficialLastname"
    assert first_official["lagrollnamn"] == "Lagledare"
    assert first_official["matchlagid"] == team_id

    # --- Optionally, validate the last official ---
    last_official = officials_data_list[-1]
    assert isinstance(last_official, dict)
    assert last_official["matchlagledareid"] == 60001
    assert last_official["fornamn"] == "Synthetic Official 2 - Team Test Team"
    assert last_official["efternamn"] == "OfficialLastname"
    assert last_official["lagrollnamn"] == "Tränare"
    assert last_official["matchlagid"] == team_id

    # --- Validate common properties for all officials ---
    for official in officials_data_list:  # <--- Iterate over officials_data_list
        assert isinstance(official, dict)
        assert "matchlagledareid" in official
        assert "fornamn" in official
        assert "efternamn" in official
        assert "lagrollnamn" in official
        assert "matchlagid" in official
        # Add more common assertions if needed


def test_fetch_match_events_json(mocker):
    """Test fetching match events list from API and validate data structure."""
    # 1. Load sample JSON response
    sample_events_response = generate_synthetic_match_events_data(num_events=20)
    # 2. Mock _api_request
    mocked_api_request = mocker.patch.object(FogisApiClient, "_api_request")
    mocked_api_request.return_value = {'d': sample_events_response}

    # 3. Create FogisApiClient instance
    api_client = FogisApiClient("testuser", "testpassword")

    # 4. Call fetch_match_events_json()
    match_id_to_test = 5760945  # Match ID from your sample data
    events_list = api_client.fetch_match_events_json(match_id_to_test)

    # 5. Assertions - Validate based on sample_events_data
    assert events_list is not None
    assert isinstance(events_list, dict)  # <--- Assert that events_list is a dictionary

    events_data_list = events_list['d']  # <--- Extract the list of events from the 'd' key
    assert isinstance(events_data_list, list)  # <--- Now assert that events_data_list is a list
    assert len(events_data_list) == 20  # Expect 17 events in sample data

    # --- Validate the first event in the list ---
    first_event = events_data_list[0]  # <--- Use events_data_list here, not events_list
    assert isinstance(first_event, dict)
    assert first_event["matchhandelseid"] == 8000
    assert first_event["matchhandelsetypnamn"] == "Spelmål"
    assert first_event["matchminut"] == 5
    assert first_event["period"] == 1
    assert first_event["matchid"] == 0
    # Add more assertions for other fields of the first event

    # --- Optionally, validate the last event ---
    last_event = events_data_list[-1]  # <--- Use events_data_list here
    assert isinstance(last_event, dict)
    assert last_event["matchhandelseid"] == 8019
    assert last_event["matchhandelsetypnamn"] == "Byte in"
    assert last_event["matchminut"] == 24
    assert last_event["period"] == 2

    # --- Validate common properties for all events ---
    for event in events_data_list:  # <--- Iterate over events_data_list
        assert isinstance(event, dict)
        assert "matchhandelseid" in event
        assert "matchhandelsetypnamn" in event
        assert "matchminut" in event
        assert "period" in event
    # Add more common assertions if needed


def test_fetch_match_result_json(mocker):
    """Test fetching match results list from API and validate data structure."""
    # 1. Load sample JSON response
    sample_result_data = generate_synthetic_match_results_data()

    # 2. Mock _api_request
    mocked_api_request = mocker.patch.object(FogisApiClient, "_api_request")
    mocked_api_request.return_value = sample_result_data  # Return the entire {'d': [...]} structure

    # 3. Create FogisApiClient instance
    api_client = FogisApiClient("testuser", "testpassword")

    # 4. Call fetch_match_result_json()
    match_id_to_test = 5747111  # Match ID from your sample data
    results_list = api_client.fetch_match_result_json(match_id_to_test)

    # 5. Assertions - Validate based on sample_result_data
    assert results_list is not None

    assert isinstance(results_list, list)  # <--- Now assert that results_data_list is a list
    assert len(results_list) == 2  # Expect 2 result entries (Fulltime and Halftime)

    # --- Validate the first result (Full time Result) ---
    full_time_result = results_list[0]  # <--- Use results_data_list
    assert isinstance(full_time_result, dict)
    assert full_time_result["matchresultattypid"] == 1
    assert full_time_result["matchresultattypnamn"] == "Slutresultat"
    assert full_time_result["matchlag1mal"] == 3
    assert full_time_result["matchlag2mal"] == 1
    # Add more assertions for other fields if needed

    # --- Validate the second result (Halftime Result) ---
    halftime_result = results_list[1]  # <--- Use results_data_list
    assert isinstance(halftime_result, dict)
    assert halftime_result["matchresultattypid"] == 2
    assert halftime_result["matchresultattypnamn"] == "Resultat efter period 1"
    assert halftime_result["matchlag1mal"] == 1
    assert halftime_result["matchlag2mal"] == 0
    # Add more assertions for other fields if needed

    # --- Optionally, validate common properties for all results ---
    for result in results_list:  # <--- Iterate over results_data_list
        assert isinstance(result, dict)
        assert "matchresultattypid" in result
        assert "matchresultattypnamn" in result
        assert "matchlag1mal" in result
        assert "matchlag2mal" in result
    # Add more common assertions if needed


def test_report_regular_goal_event_payload(mocker):
    """Unit test for report_match_event - payload verification for Regular Goal event."""

    # 1. Mock Dependencies (only api_client needed for this test)
    MagicMock(spec=FogisApiClient)
    mocker.patch.object(FogisApiClient, "login", return_value=True)

    # 2. Mock _api_request Using mocker.patch
    mocked_api_request = mocker.patch.object(
        FogisApiClient, "_api_request", return_value={"d": None}  # Mock to return None, successful for our test
    )

    # 3. Define Synthetic event_data Payload for Regular Goal (Manually Construct Expected Payload)
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

    # 4. Define Expected API Request Payload (Manually Construct Expected Payload)
    expected_payload = {
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

    # 5. Create FogisApiClient Instance
    api_client = FogisApiClient("testuser", "testpassword")
    api_client.cookies = {'TestCookie': 'TestValue'}

    # 6. Call report_match_event()
    api_client.report_match_event(event_data)  # Call report_match_event with synthetic data

    # 7. Assertions - Verify API Request Payload Content
    mocked_api_request.assert_called_once()  # Verify _api_request was called exactly once
    request_payload = mocked_api_request.call_args.args[1]  # Get captured payload from positional argument

    # --- Assert that the captured request payload is EXACTLY the same as expected_payload ---
    assert request_payload == expected_payload, "Request payload does not match expected payload"


def test_login_success(mocker):
    """Unit test for successful login."""
    client = FogisApiClient("testuser", "testpass")

    # Directly patch FogisApiClient.session
    mocked_session = mocker.patch.object(client, "session", autospec=True)

    # Mock initial GET for login page
    mock_initial_response = MockResponse(
        json_data=None,  # Not relevant for initial GET
        status_code=200
    )
    mock_initial_response.text = '<form id="aspnetForm"><input type="hidden" name="__VIEWSTATE" value="mock_viewstate"></form>'
    mocked_session.get.return_value = mock_initial_response

    # Mock successful login POST (302 redirect)
    mock_login_response = MockResponse(
        json_data=None,  # Not relevant for redirect
        status_code=302
    )
    mock_login_response.headers = {'Location': '/mdk/default.aspx'}
    mock_login_response.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}
    mocked_session.post.return_value = mock_login_response

    # Explicitly mock requests.utils.dict_from_cookiejar to return a dictionary with the auth cookie
    mocked_dict_from_cookiejar = mocker.patch("requests.utils.dict_from_cookiejar")
    mocked_dict_from_cookiejar.return_value = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}

    cookies = client.login()

    assert cookies is not None
    assert 'FogisMobilDomarKlient.ASPXAUTH' in cookies
    mocked_session.get.assert_called()
    mocked_session.post.assert_called_once()


def test_login_failure_invalid_credentials(mocker):
    """Unit test for login failure due to invalid credentials."""
    client = FogisApiClient("wronguser", "wrongpass")

    # Directly patch FogisApiClient.session
    mocked_session = mocker.patch.object(client, "session", autospec=True)

    # Mock initial GET for login page
    mock_initial_response = MockResponse(
        json_data=None,  # Not relevant for initial GET
        status_code=200
    )
    mock_initial_response.text = '<form id="aspnetForm"><input type="hidden" name="__VIEWSTATE" value="mock_viewstate"></form>'
    mocked_session.get.return_value = mock_initial_response

    # Mock failed login POST (e.g., status code 200 but no redirect or auth cookie)
    mock_login_response = MockResponse(
        json_data=None,
        status_code=200  # Simulate login page returning with error, not redirecting
    )
    mock_login_response.cookies = {}  # Use an empty dictionary (no auth cookie)
    mocked_session.post.return_value = mock_login_response

    # Mock requests.utils.dict_from_cookiejar (important - consistent mocking)
    mocked_dict_from_cookiejar = mocker.patch("requests.utils.dict_from_cookiejar")
    mocked_dict_from_cookiejar.return_value = {}  # Mock to return empty dict for cookies

    with pytest.raises(FogisLoginError) as excinfo:
        client.login()

    assert "Login failed" in str(excinfo.value)
    # mocked_session.get.assert_called() # Removed/Commented out - Incorrect assertion for failure case
    mocked_session.post.assert_called_once()


def test_api_request_post_success(mocker):
    """Unit test for successful _api_request POST."""
    client = FogisApiClient("testuser", "testpass") # Create an instance of FogisApiClient
    client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}

    mock_session_instance = Mock() # Create a Mock instance directly (no need to patch the class)
    mock_api_response = MockResponse(
        json_data={'d': {'key': 'value'}},
        status_code=200
    )
    mock_session_instance.post.return_value = mock_api_response

    # **PATCH THE INSTANCE ATTRIBUTE `client.session`**
    mocker.patch.object(client, 'session', mock_session_instance)

    url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/SomeEndpoint"
    payload = {"param1": "value1"}
    response_data = client._api_request(url, payload, method='POST')

    assert response_data == {'key': 'value'}

    mock_session_instance.post.assert_called_once_with(
        url,
        headers={  # Assert the *expected* headers directly
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
    assert 'Cookie' in called_headers
    assert 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie' in called_headers['Cookie']


def test_api_request_get_success(mocker):
    """Unit test for successful _api_request GET."""
    client = FogisApiClient("testuser", "testpass")
    client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}  # Simulate logged in state

    mock_session_instance = Mock() # Create a Mock instance directly
    mock_api_response = MockResponse(
        json_data={'d': {'items': [1, 2, 3]}},  # Simulate successful API response
        status_code=200
    )
    mock_session_instance.get.return_value = mock_api_response # Return the MockResponse object itself, not just json()

    # **PATCH THE INSTANCE ATTRIBUTE `client.session`**
    mocker.patch.object(client, 'session', mock_session_instance)

    url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/GetSomeData"
    response_data = client._api_request(url, method='GET')

    assert response_data == {'items': [1, 2, 3]}
    mock_session_instance.get.assert_called_once_with(
        url,
        headers={  # Assert the expected headers directly
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://fogis.svenskfotboll.se',
            'Referer': 'https://fogis.svenskfotboll.se/mdk/',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': 'FogisMobilDomarKlient.ASPXAUTH=mock_auth_cookie'
        }
    )

def test_api_request_not_logged_in(mocker):
    """Unit test for _api_request when not logged in."""
    client = FogisApiClient("testuser", "testpass")
    # client.cookies = None (implicitly not logged in)

    with pytest.raises(FogisLoginError) as excinfo:
        client._api_request("https://fogis.svenskfotboll.se/mdk/SomeEndpoint")

    assert "Not logged in" in str(excinfo.value)


def test_api_request_http_error(mocker):
    """Unit test for _api_request handling HTTP errors."""
    client = FogisApiClient("testuser", "testpass")
    client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}  # Simulate logged in state

    mock_session = mocker.patch("requests.Session", autospec=True)
    mock_session_instance = mock_session.return_value

    mock_api_response = MockResponse(
        json_data=None,
        status_code=404  # Simulate Not Found error
    )
    mock_session_instance.post.return_value = mock_api_response
    mock_session_instance.post.side_effect = requests.exceptions.HTTPError(
        "HTTP Error 404")  # Make raise_for_status actually raise

    url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/BrokenEndpoint"
    payload = {"param1": "value1"}

    with pytest.raises(FogisAPIRequestError) as excinfo:
        client._api_request(url, payload, method='POST')

    assert "API request error" in str(excinfo.value)


def test_api_request_invalid_json_response(mocker):
    """Unit test for _api_request handling invalid JSON response (missing 'd')."""
    client = FogisApiClient("testuser", "testpass")
    client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}  # Simulate logged in state

    mock_session_instance = Mock() # Create a Mock instance directly
    mock_api_response = MockResponse(
        json_data={'unexpected_key': 'value'},  # Simulate JSON without 'd' key
        status_code=200
    )
    mock_session_instance.post.return_value = mock_api_response # Return the MockResponse object

    # **PATCH THE INSTANCE ATTRIBUTE `client.session`**
    mocker.patch.object(client, 'session', mock_session_instance)

    url = "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/BadJsonResponse"
    payload = {"param1": "value1"}

    with pytest.raises(FogisDataError) as excinfo:
        client._api_request(url, payload, method='POST')

    assert "Unexpected JSON response format" in str(excinfo.value)

def test_fetch_matches_list_json_success(mocker):
    """Unit test for fetch_matches_list_json success."""
    client = FogisApiClient("testuser", "testpass")
    client.cookies = {'FogisMobilDomarKlient.ASPXAUTH': 'mock_auth_cookie'}  # Simulate logged in state

    mock_api_request = mocker.patch.object(client, "_api_request", autospec=True)  # Mock _api_request method
    mock_api_request.return_value = {'matchlista': [{'matchid': 1}, {'matchid': 2}]}  # Simulate successful response

    matches_list = client.fetch_matches_list_json()

    assert matches_list == [{'matchid': 1}, {'matchid': 2}]
    # 1. Assert call_count separately:
    mock_api_request.assert_called_once()

    # 2. Inspect call_args and assert arguments individually:
    call_args = mock_api_request.call_args
    args = call_args.args  # Positional args
    kwargs = call_args.kwargs  # Keyword args

    assert len(args) == 2  # Corrected: Assert that there are EXACTLY 2 positional args
    assert args[0] == "https://fogis.svenskfotboll.se/mdk/MatchWebMetoder.aspx/GetMatcherAttRapportera"
    assert isinstance(args[1], dict)
    assert 'method' not in kwargs or kwargs['method'] == 'POST'
