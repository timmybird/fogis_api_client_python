import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup
from .enums import MatchStatus, AgeCategory, Gender, FootballType

event_types = {  # Updated - Consistent Integer Keys for ALL event types (where applicable)
    6: {"name": "Regular Goal", "goal": True},
    39: {"name": "Header Goal", "goal": True},
    28: {"name": "Corner Goal", "goal": True},
    29: {"name": "Free Kick Goal", "goal": True},
    15: {"name": "Own Goal", "goal": True},
    14: {"name": "Penalty Goal", "goal": True},
    18: {"name": "Penalty Missing Goal", "goal": False},
    19: {"name": "Penalty Save", "goal": False},
    26: {"name": "Penalty Hitting the Frame", "goal": False},
    20: {"name": "Yellow Card", "goal": False},
    8: {"name": "Red Card (Denying Goal Opportunity)", "goal": False},
    9: {"name": "Red Card (Other Reasons)", "goal": False},
    17: {"name": "Substitution", "goal": False},
    31: {"name": "Period Start", "goal": False, "control_event": True},
    32: {"name": "Period End", "goal": False, "control_event": True},
    23: {"name": "Match Slut", "goal": False, "control_event": True}
}


class FogisAPIError(Exception):  # Base class for all Fogis API exceptions
    """Base class for exceptions in the FOGIS API Client."""
    pass


class FogisLoginError(FogisAPIError):
    """Exception raised when login to FOGIS API fails."""
    pass


class FogisAPIRequestError(FogisAPIError):
    """Exception raised for general FOGIS API request errors."""
    pass


class FogisDataError(FogisAPIError):
    """Exception raised when there's an issue with FOGIS API data."""
    pass


class FogisFilterValidationError(FogisAPIError):
    """Exception raised when the provided filter parameters are invalid."""
    pass


class FogisApiClient:
    """
    A client for interacting with the FOGIS API.
    ...
    """
    BASE_URL = "https://fogis.svenskfotboll.se/mdk"  # Define base URL as a class constant
    logger = logging.getLogger(__name__)

    def __init__(self, username, password):
        """
        Initializes the FogisApiClient with login credentials.
        ...
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.cookies = None

    def login(self):
        """Logs into the FOGIS API and stores the session cookies."""
        if self.cookies:
            return self.cookies

        login_url = f"{FogisApiClient.BASE_URL}/Login.aspx?ReturnUrl=%2fmdk%2f"
        login_payload_base = {
            "ctl00$MainContent$UserName": self.username,
            "ctl00$MainContent$Password": self.password,
            "ctl00$MainContent$LoginButton": "Logga in"
        }
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "",
            "Host": "fogis.svenskfotboll.se",
            "Origin": "https://fogis.svenskfotboll.se",
            "Referer": f"{FogisApiClient.BASE_URL}/Login.aspx?ReturnUrl=%2fmdk%2f",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }

        try:
            initial_response = self.session.get(login_url, headers=headers)
            initial_response.raise_for_status()

            hidden_fields = {}
            soup = BeautifulSoup(initial_response.text, 'html.parser')
            form = soup.find('form', {'id': 'aspnetForm'})
            if form:
                for input_tag in form.find_all('input', {'type': 'hidden'}):
                    name = input_tag.get('name')
                    value = input_tag.get('value', '')
                    if name:
                        hidden_fields[name] = value
            login_payload = {**login_payload_base, **hidden_fields}

            if 'cookieconsent_status' not in self.session.cookies.keys():
                self.session.cookies.set('cookieconsent_status', 'dismiss', domain='fogis.svenskfotboll.se', path='/')

            login_response = self.session.post(login_url, data=login_payload, headers=headers, allow_redirects=False)
            login_response.raise_for_status()

            if login_response.status_code == 302 and 'FogisMobilDomarKlient.ASPXAUTH' in login_response.cookies.keys():
                redirect_url = login_response.headers['Location']
                if redirect_url.startswith('/'):
                    redirect_url = f"{FogisApiClient.BASE_URL}" + redirect_url
                redirect_response = self.session.get(redirect_url, headers=headers)
                redirect_response.raise_for_status()
                self.cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
                self.logger.info("Login successful!")
                return self.cookies
            else:
                self.logger.error(f"Login failed with status code: {login_response.status_code}")
                raise FogisLoginError(f"Login failed with status code: {login_response.status_code}")

        except requests.exceptions.RequestException as e:
            self.logger.exception("Login request error", exc_info=e)
            raise FogisAPIRequestError("Error during login request", e)

    def _api_request(self, url, payload=None, method='POST'):
        """
        Internal helper function to make API requests to FOGIS.
        ...
        """
        if not self.cookies:
            self.logger.error("Error: Not logged in. Please call login() first.")
            raise FogisLoginError("Not logged in. Please call login() first.")

        api_headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'https://fogis.svenskfotboll.se',
            'Referer': f"{FogisApiClient.BASE_URL}/",  # Referer now using BASE_URL
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': '; '.join([f"{key}={value}" for key, value in self.cookies.items()])
        }

        try:
            if method == 'POST':
                response = self.session.post(url, headers=api_headers, json=payload)
            elif method == 'GET':
                response = self.session.get(url, headers=api_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            response_json = response.json()
            if response_json and 'd' in response_json:
                return response_json['d']
            else:
                self.logger.warning(f"Unexpected JSON response format from {url}: {response_json}")
                raise FogisDataError(f"Unexpected JSON response format from {url}: {response_json}")

        except requests.exceptions.RequestException as e:
            self.logger.exception(f"API request error to {url}: {e}", exc_info=e)
            raise FogisAPIRequestError(f"API request error to {url}: {e}") from e
        except ValueError as ve:
            self.logger.error(f"Value Error in _api_request: {ve}")
            raise FogisAPIRequestError(f"Value Error in _api_request: {ve}") from ve  # Chaining ValueError


    def fetch_matches_list_json(self, filter: Optional[Dict[str, Any]] = None):
        """Fetches the list of matches in JSON format from FOGIS API.

        Now ONLY handles API fetching. Client-side filtering is applied separately using the MatchListFilter class.

        Args:
            filter (Optional[Dict[str, Any]], optional): An OPTIONAL dictionary containing server-side
                date range filter criteria (`datumFran`, `datumTill`, `datumTyp`, `sparadDatum`).
                Client-side filtering (status, age category, gender, football type)
                is now handled separately using the MatchListFilter class AFTER fetching.
                Defaults to None, which fetches matches for the default date range (one week back and 365 days ahead)
                without any server-side filtering beyond the default date range.

        Returns:
            list: A list of match dictionaries, or None if fetching fails.

        Raises:
            FogisFilterValidationError: If the provided filter parameters are invalid in the filter dictionary (if provided).
            FogisLoginError: If login fails.
            FogisAPIRequestError: If the API request fails with an HTTP error.
            FogisDataError: If the API response data is invalid or in an unexpected format.

        Example Usage (Fetching all matches within default date range):
        ```python
        api_client = FogisApiClient("your_username", "your_password")
        all_matches = api_client.fetch_matches_list_json() # No filter, fetches all matches within default date range
        if all_matches:
            print(f"Fetched {len(all_matches)} matches.")
        else:
            print("Failed to fetch matches.")
        ```

        For applying client-side filtering, use the MatchListFilter class separately AFTER fetching.
        See the MatchListFilter class documentation for examples of how to create and use filters.
        """
        today = datetime.today().strftime('%Y-%m-%d')
        default_datum_fran = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d') # One week ago
        default_datum_till = (datetime.today() + timedelta(days=365)).strftime('%Y-%m-%d') # 365 days ahead

        payload_filter = { # --- Build DEFAULT payload dictionary DIRECTLY
            "datumFran": default_datum_fran,
            "datumTill": default_datum_till,
            "datumTyp": 0,
            "typ": "alla",
            "status": ["avbruten", "uppskjuten", "installd"],
            "alderskategori": [1, 2, 3, 4, 5],
            "kon": [3, 2, 4],
            "sparadDatum": today,
        }

        if filter: # If a filter dictionary is provided as 'filter' argument (for server-side date filters)
            payload_filter.update(filter) # MERGE server-side filters from the provided dictionary


        matches_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatcherAttRapportera"
        data = self._api_request(matches_url, {"filter": payload_filter}) # Pass payload_filter to _api_request!
        all_matches = data['matchlista'] if data and 'matchlista' in data else []
        return all_matches

    def fetch_team_players_json(self, team_id):
        """Fetches the list of team players in JSON format for a given team ID."""
        players_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatchdeltagareListaForMatchlag"  # Using BASE_URL
        payload = {"matchlagid": team_id}
        return self._api_request(players_url, payload)

    def fetch_team_officials_json(self, team_id):
        """Fetches the list of team officials in JSON format for a given team ID."""
        officials_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatchlagledareListaForMatchlag"  # Using BASE_URL
        payload = {"matchlagid": team_id}
        return self._api_request(officials_url, payload)

    def fetch_match_events_json(self, match_id):
        """Fetches the list of match events in JSON format for a given match ID."""
        events_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatchhandelselista"  # Using BASE_URL
        payload = {"matchid": match_id}
        return self._api_request(events_url, payload)

    def report_match_event(self, event_data):
        """Reports a match event to the FOGIS API."""
        event_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SparaMatchhandelse"  # Using BASE_URL
        return self._api_request(event_url, event_data)

    def report_match_result(self, result_data):
        """Reports match results (halftime and fulltime) to the FOGIS API."""
        result_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SparaMatchresultatLista"  # Using BASE_URL
        return self._api_request(result_url, result_data)

    def fetch_match_result_json(self, match_id):  # ADD THIS FUNCTION
        """Fetches the list of match results in JSON format for a given match ID."""
        result_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatchresultatlista"  # Using BASE_URL
        payload = {"matchid": match_id}
        return self._api_request(result_url, payload)

    def report_team_official_action(self, action_data):
        """Reports team official disciplinary action to the FOGIS API."""
        action_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/SparaMatchlagledare"  # Using BASE_URL
        return self._api_request(action_url, action_data)

    def delete_match_event(self, event_id):
        """Deletes a match event from FOGIS API."""
        delete_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/RaderaMatchhandelse"  # Using BASE_URL
        payload = {"matchhandelseid": event_id}
        response_data = self._api_request(delete_url, payload)
        return response_data is None

    def clear_match_events(self, match_id):
        """Clears all match events for a given match."""
        match_events_json = self.fetch_match_events_json(match_id)
        if match_events_json:
            print(f"Found {len(match_events_json)} events to clear...")
            for event in match_events_json:
                event_id = event['matchhandelseid']
                if self.delete_match_event(event_id):
                    print(f"Deleted event ID: {event_id}")
                else:
                    print(f"Failed to delete event ID: {event_id}")
            print("Match events clear operation completed.")
            return True
        else:
            print("No match events found to clear.")
            return False
