import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List

import requests
from bs4 import BeautifulSoup

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


class FogisAPIError(Exception): # Base class for all Fogis API exceptions
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


class MatchFilterBuilder:
    """
    Builder class for constructing filter dictionaries for fetching matches from the FOGIS API.
    Provides a fluent interface for building filter criteria with validation and clear documentation.
    Validation errors are collected during the building process and raised when the `build()` method is called.
    """
    VALID_STATUSES = ["avbruten", "uppskjuten", "installd"]
    STATUS_DESCRIPTIONS = {
        "avbruten": "interrupted/abandoned",
        "uppskjuten": "postponed/rescheduled",
        "installd": "cancelled"
    }
    VALID_AGE_CATEGORIES = [1, 2, 3, 4, 5]
    AGE_CATEGORY_DESCRIPTIONS = {
        1: "undefined",
        2: "children",
        3: "youth",
        4: "adults/senior",
        5: "veteran"
    }
    VALID_GENDERS = [2, 3, 4]
    GENDER_DESCRIPTIONS = {
        2: "men",
        3: "women",
        4: "mixed"
    }

    def __init__(self):
        self._filter = {}  # Internal dictionary to store filter parameters
        self._errors = []  # List to store validation error messages

    def date_range(self, start_date: date, end_date: date) -> 'MatchFilterBuilder':
        """Sets the date range filter. (Docstring remains same as before)"""
        if not isinstance(start_date, date) or not isinstance(end_date, date):
            self._errors.append("Start and end dates must be datetime.date objects.")  # Append error, don't raise
        elif start_date > end_date:
            self._errors.append("Start date cannot be after end date.")  # Append error, don't raise
        else:
            self._filter['datumFran'] = start_date.strftime('%Y-%m-%d')
            self._filter['datumTill'] = end_date.strftime('%Y-%m-%d')
        return self

    def date_type(self, date_type: int) -> 'MatchFilterBuilder':
        """Sets the date type filter. (Docstring remains same as before)"""
        if not isinstance(date_type, int) or date_type not in [0, 1]:
            self._errors.append("Date type must be an integer, either 0 or 1.")  # Append error, don't raise
        else:
            self._filter['datumTyp'] = date_type
        return self

    def status(self, statuses: List[str]) -> 'MatchFilterBuilder':
        """Sets the match status filter. (Docstring remains same as before)"""
        if not isinstance(statuses, list) or not all(isinstance(s, str) for s in statuses):
            self._errors.append("Status filter must be a list of strings.")  # Append error, don't raise
        else:
            invalid_statuses = []
            for status in statuses:
                if status not in self.VALID_STATUSES:
                    invalid_statuses.append(status)
            if invalid_statuses:
                valid_statuses_str = ', '.join([f'{s} ({self.STATUS_DESCRIPTIONS[s]})' for s in self.VALID_STATUSES])
                self._errors.append(
                    f"Invalid statuses: {', '.join(invalid_statuses)}. Valid statuses are: {valid_statuses_str}")  # Append error
            else:
                self._filter['status'] = statuses
        return self

    def age_categories(self, categories: List[int]) -> 'MatchFilterBuilder':
        """Sets the age category filter. (Docstring remains same as before)"""
        if not isinstance(categories, list) or not all(isinstance(cat, int) for cat in categories):
            self._errors.append("Age categories filter must be a list of integers.")  # Append error, don't raise
        else:
            invalid_categories = []
            for category in categories:
                if category not in self.VALID_AGE_CATEGORIES:
                    invalid_categories.append(str(category))  # Convert to str for consistent error message
            if invalid_categories:
                valid_categories_str = ', '.join(
                    [f'{cat} ({self.AGE_CATEGORY_DESCRIPTIONS[cat]})' for cat in self.VALID_AGE_CATEGORIES])
                self._errors.append(
                    f"Invalid age category IDs: {', '.join(invalid_categories)}. Valid IDs are: {valid_categories_str}")  # Append error
            else:
                self._filter['alderskategori'] = categories
        return self

    def genders(self, genders: List[int]) -> 'MatchFilterBuilder':
        """Sets the gender filter. (Docstring remains same as before)"""
        if not isinstance(genders, list) or not all(isinstance(gen, int) for gen in genders):
            self._errors.append("Genders filter must be a list of integers.")  # Append error, don't raise
        else:
            invalid_genders = []
            for gender in genders:
                if gender not in self.VALID_GENDERS:
                    invalid_genders.append(str(gender))  # Convert to str for consistent error message
            if invalid_genders:
                valid_genders_str = ', '.join(
                    [f'{gen} ({self.GENDER_DESCRIPTIONS[gen]})' for gen in self.VALID_GENDERS])
                self._errors.append(
                    f"Invalid gender IDs: {', '.join(invalid_genders)}. Valid IDs are: {valid_genders_str}")  # Append error
            else:
                self._filter['kon'] = genders
        return self

    def saved_date(self, saved_date: date) -> 'MatchFilterBuilder':
        """Sets the saved date filter. (Docstring remains same as before)"""
        if not isinstance(saved_date, date):
            self._errors.append("Saved date must be a datetime.date object.")  # Append error, don't raise
        else:
            self._filter['sparadDatum'] = saved_date.strftime('%Y-%m-%d')
        return self

    def build(self) -> Dict[str, Any]:
        """
        Builds and returns the filter dictionary.

        Raises:
            FogisFilterValidationError: If any validation errors were encountered during filter construction.

        Returns:
            Dict[str, Any]: The constructed filter dictionary if no errors occurred.
        """
        if self._errors:
            error_message = "Filter validation errors encountered:\n" + "\n".join([f"- {err}" for err in self._errors])
            raise FogisFilterValidationError(error_message)  # Raise exception if errors
        return self._filter


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
            raise FogisAPIRequestError(f"Value Error in _api_request: {ve}") from ve # Chaining ValueError

    def fetch_matches_list_json(self, filter: Optional[Dict[str, Any]] = None):
        """Fetches the list of matches in JSON format from FOGIS API.

        Args:
            filter (Optional[dict], optional): A dictionary containing filter criteria. Defaults to None, which fetches matches for the default date range (one week back and 365 days ahead).
                *   `datumFran` (Optional[str]): Start date for the date range filter (YYYY-MM-DD).
                *   `datumTill` (Optional[str]): End date for the date range filter (YYYY-MM-DD).
                *   `datumTyp` (Optional[int]): 0 for relative dates, 1 for fixed dates. Defaults to 0 (relative).
                *   `status` (Optional[List[str]]): A list of match statuses to filter by.
                    Valid values include: `"avbruten"`, `"uppskjuten"`, `"installd"`.
                    **Note: This list is not exhaustive and other valid status values may exist within the FOGIS API.**
                *   `alderskategori` (Optional[List[int]]): A list of age category IDs to filter by.
                    Valid values include: `1`, `2`, `3`, `4`, `5`. See documentation for ID mappings to category names.
                *   `kon` (Optional[List[int]]): A list of gender IDs to filter by.
                    Valid values include: `2`, `3`, `4`. See documentation for ID mappings to gender names.
                *   `sparadDatum`(Optional[str]): The date when the filter was saved as (YYYY-MM-DD), use unknown - defaults to today's  date

        Returns:
            list: A list of match dictionaries, or None if fetching fails.

        Raises:
            FogisFilterValidationError: If the provided filter parameters are invalid.

        Example `filter` payload:

        ```python
        filter_payload = {
            "datumFran": "2024-03-01",
            "datumTill": "2024-03-31",
            "status": ["avbruten", "spelad"], # Example with "spelad" - might not be valid, needs verification
            "alderskategori": [3, 4],
            "kon": [4]
        }
        matches = api_client.fetch_matches_list_json(filter=filter_payload)
        ```
        """
        today = datetime.today().strftime('%Y-%m-%d')
        default_datum_fran = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        default_datum_till = (datetime.today() + timedelta(days=365)).strftime('%Y-%m-%d')

        payload_filter = {
            "datumFran": default_datum_fran,
            "datumTill": default_datum_till,
            "datumTyp": 0,  # Default to relative dates
            "typ": "alla",
            "status": ["avbruten", "uppskjuten", "installd"],
            "alderskategori": [1, 2, 3, 4, 5],
            "kon": [3, 2, 4],
            "sparadDatum": today
        }

        if filter:
            if not isinstance(filter, dict):
                raise FogisFilterValidationError("Filter parameter must be a dictionary.")

            if 'datumFran' in filter:
                if not isinstance(filter['datumFran'], str):
                    raise FogisFilterValidationError(
                        "Filter parameter 'datumFran' must be a string in YYYY-MM-DD format.")
                # Basic date format validation (more robust validation could be added)
                try:
                    datetime.strptime(filter['datumFran'], '%Y-%m-%d')
                except ValueError:
                    raise FogisFilterValidationError("Filter parameter 'datumFran' must be in YYYY-MM-DD format.")
                payload_filter['datumFran'] = filter['datumFran']

            if 'datumTill' in filter:
                if not isinstance(filter['datumTill'], str):
                    raise FogisFilterValidationError(
                        "Filter parameter 'datumTill' must be a string in YYYY-MM-DD format.")
                # Basic date format validation (more robust validation could be added)
                try:
                    datetime.strptime(filter['datumTill'], '%Y-%m-%d')
                except ValueError:
                    raise FogisFilterValidationError("Filter parameter 'datumTill' must be in YYYY-MM-DD format.")
                payload_filter['datumTill'] = filter['datumTill']

            if 'datumTyp' in filter:
                if not isinstance(filter['datumTyp'], int):
                    raise FogisFilterValidationError("Filter parameter 'datumTyp' must be an integer.")
                payload_filter['datumTyp'] = filter['datumTyp']

            if 'status' in filter:
                if not isinstance(filter['status'], list):
                    raise FogisFilterValidationError("Filter parameter 'status' must be a list of strings.")
                if not all(
                        isinstance(item, str) for item in filter['status']):  # Check if all items in list are strings
                    raise FogisFilterValidationError("Filter parameter 'status' must be a list of strings.")
                payload_filter['status'] = filter['status']

            if 'alderskategori' in filter:
                if not isinstance(filter['alderskategori'], list):
                    raise FogisFilterValidationError("Filter parameter 'alderskategori' must be a list of integers.")
                if not all(isinstance(item, int) for item in
                           filter['alderskategori']):  # Check if all items in list are integers
                    raise FogisFilterValidationError("Filter parameter 'alderskategori' must be a list of integers.")
                payload_filter['alderskategori'] = filter['alderskategori']

            if 'kon' in filter:
                if not isinstance(filter['kon'], list):
                    raise FogisFilterValidationError("Filter parameter 'kon' must be a list of integers.")
                if not all(isinstance(item, int) for item in filter['kon']):  # Check if all items in list are integers
                    raise FogisFilterValidationError("Filter parameter 'kon' must be a list of integers.")
                payload_filter['kon'] = filter['kon']

            if 'sparadDatum' in filter:
                if not isinstance(filter['sparadDatum'], str):
                    raise FogisFilterValidationError(
                        "Filter parameter 'sparadDatum' must be a string in YYYY-MM-DD format.")
                try:
                    datetime.strptime(filter['sparadDatum'], '%Y-%m-%d')
                except ValueError:
                    raise FogisFilterValidationError("Filter parameter 'sparadDatum' must be in YYYY-MM-DD format.")
                payload_filter['sparadDatum'] = filter['sparadDatum']

        matches_url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/GetMatcherAttRapportera"
        data = self._api_request(matches_url, {"filter": payload_filter}) # Wrap payload_filter in "filter" key
        return data['matchlista'] if data and 'matchlista' in data else None

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
