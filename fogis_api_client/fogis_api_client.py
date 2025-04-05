import logging
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
from urllib.parse import urlparse, parse_qs

# Custom exceptions
class FogisLoginError(Exception):
    """Exception raised when login to FOGIS fails."""
    pass

class FogisAPIRequestError(Exception):
    """Exception raised when an API request to FOGIS fails."""
    pass

class FogisDataError(Exception):
    """Exception raised when there's an issue with the data from FOGIS."""
    pass

class FogisApiClient:
    """
    A client for interacting with the FOGIS API.
    
    This client implements lazy login, meaning it will automatically authenticate
    when making API requests if not already logged in. You can also explicitly call
    login() if you want to pre-authenticate.
    """
    BASE_URL = "https://fogis.svenskfotboll.se/mdk"  # Define base URL as a class constant
    logger = logging.getLogger(__name__)

    def __init__(self, username, password):
        """
        Initializes the FogisApiClient with login credentials.
        
        Authentication happens automatically on the first API request (lazy login),
        but you can also call login() explicitly if needed.
        
        Args:
            username (str): FOGIS username
            password (str): FOGIS password
        """
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.cookies = None

    def login(self):
        """
        Logs into the FOGIS API and stores the session cookies.
        
        Note: It is not necessary to call this method explicitly as the client
        implements lazy login and will authenticate automatically when needed.
        
        Returns:
            dict: The session cookies if login is successful
        
        Raises:
            FogisLoginError: If login fails
            FogisAPIRequestError: If there is an error during the login request
        """
        if self.cookies:
            return self.cookies

        login_url = f"{FogisApiClient.BASE_URL}/Login.aspx?ReturnUrl=%2fmdk%2f"

        try:
            # Get the login page to retrieve the __VIEWSTATE and __EVENTVALIDATION
            response = self.session.get(login_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
            eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']

            # Prepare login data
            login_data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate,
                '__EVENTVALIDATION': eventvalidation,
                'ctl00$cphMain$tbUsername': self.username,
                'ctl00$cphMain$tbPassword': self.password,
                'ctl00$cphMain$btnLogin': 'Logga in'
            }

            # Submit login form
            response = self.session.post(login_url, data=login_data)
            response.raise_for_status()

            # Check if login was successful
            if 'FogisMobilDomarKlient.ASPXAUTH' in self.session.cookies:
                self.cookies = {key: value for key, value in self.session.cookies.items()}
                self.logger.info("Login successful")
                return self.cookies
            else:
                self.logger.error("Login failed: Invalid credentials or session issue")
                raise FogisLoginError("Login failed: Invalid credentials or session issue")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Login failed: {e}")
            raise FogisAPIRequestError(f"Login request failed: {e}")

    def fetch_matches_list_json(self):
        """
        Fetches the list of matches for the logged-in referee.
        
        Returns:
            list: A list of match dictionaries
            
        Raises:
            FogisLoginError: If not logged in
            FogisAPIRequestError: If there's an error with the API request
            FogisDataError: If the response data is invalid
        """
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchLista"
        payload = {}  # No payload needed for this request
        
        response_data = self._api_request(url, payload)
        
        if 'matcher' in response_data:
            return response_data['matcher']
        else:
            self.logger.error("Invalid response data: 'matcher' key not found")
            raise FogisDataError("Invalid response data: 'matcher' key not found")

    def fetch_match_json(self, match_id):
        """
        Fetches detailed information for a specific match.
        
        Args:
            match_id (str): The ID of the match to fetch
            
        Returns:
            dict: Match details
            
        Raises:
            FogisLoginError: If not logged in
            FogisAPIRequestError: If there's an error with the API request
            FogisDataError: If the response data is invalid
        """
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatch"
        payload = {"matchid": match_id}
        
        return self._api_request(url, payload)

    def fetch_match_players_json(self, match_id):
        """
        Fetches player information for a specific match.
        
        Args:
            match_id (str): The ID of the match
            
        Returns:
            dict: Player information for the match
            
        Raises:
            FogisLoginError: If not logged in
            FogisAPIRequestError: If there's an error with the API request
        """
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchSpelare"
        payload = {"matchid": match_id}
        
        return self._api_request(url, payload)

    def fetch_match_officials_json(self, match_id):
        """
        Fetches officials information for a specific match.
        
        Args:
            match_id (str): The ID of the match
            
        Returns:
            dict: Officials information for the match
            
        Raises:
            FogisLoginError: If not logged in
            FogisAPIRequestError: If there's an error with the API request
        """
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchFunktionarer"
        payload = {"matchid": match_id}
        
        return self._api_request(url, payload)

    def fetch_match_events_json(self, match_id):
        """
        Fetches events information for a specific match.
        
        Args:
            match_id (str): The ID of the match
            
        Returns:
            dict: Events information for the match
            
        Raises:
            FogisLoginError: If not logged in
            FogisAPIRequestError: If there's an error with the API request
        """
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/HamtaMatchHandelser"
        payload = {"matchid": match_id}
        
        return self._api_request(url, payload)

    def delete_match_event(self, event_id):
        """
        Deletes a specific event from a match.
        
        Args:
            event_id (str): The ID of the event to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            FogisLoginError: If not logged in
            FogisAPIRequestError: If there's an error with the API request
        """
        url = f"{FogisApiClient.BASE_URL}/MatchWebMetoder.aspx/TaBortMatchHandelse"
        payload = {"matchhandelseid": event_id}
        
        response_data = self._api_request(url, payload)
        
        # Check if deletion was successful
        return response_data.get('success', False)

    def clear_match_events(self, match_id):
        """
        Clear all events for a match.
        """
        payload = {"matchid": match_id}
        return self._api_request(
            url=f"{FogisApiClient.BASE_URL}/Fogis/Match/ClearMatchEvents",
            payload=payload
        )

    def hello_world(self):
        return "Hello, brave new world!"

    def mark_reporting_finished(self, match_id):
        """
        Mark a match report as completed/finished in the FOGIS system.
        
        This is the final step in the referee reporting workflow that finalizes 
        the match report and submits it officially.
        
        Args:
            match_id (str): The ID of the match to mark as finished
            
        Returns:
            dict: The response from the FOGIS API
            
        Raises:
            FogisAPIRequestError: If there's an error with the API request
            
        Example:
            >>> client = FogisApiClient(username, password)
            >>> client.login()
            >>> result = client.mark_reporting_finished(match_id="123456")
            >>> print(f"Report marked as finished: {result['success']}")
        """
        # Validate match_id
        if not match_id:
            raise ValueError("match_id cannot be empty")
            
        payload = {"matchid": match_id}
        return self._api_request(
            url=f"{FogisApiClient.BASE_URL}/Fogis/Match/SparaMatchGodkannDomarrapport",
            payload=payload
        )

    def _api_request(self, url, payload=None, method="POST"):
        """
        Internal helper function to make API requests to FOGIS.
        Automatically logs in if not already authenticated.
        
        Args:
            url (str): The URL to make the request to
            payload (dict, optional): The payload to send with the request
            method (str, optional): The HTTP method to use (default: "POST")
            
        Returns:
            dict: The response data from the API
            
        Raises:
            FogisLoginError: If login fails
            FogisAPIRequestError: If there is an error with the API request
            FogisDataError: If the response data is invalid
        """
        # Lazy login - automatically log in if not already authenticated
        if not self.cookies:
            self.logger.info("Not logged in. Performing automatic login...")
            self.login()
            
            # Double-check that login was successful
            if not self.cookies:
                self.logger.error("Automatic login failed.")
                raise FogisLoginError("Automatic login failed.")

        api_headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://fogis.svenskfotboll.se",
            "Referer": f"{FogisApiClient.BASE_URL}/",  # Referer now using BASE_URL
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": "; ".join([f"{key}={value}" for key, value in self.cookies.items()])
        }
        
        try:
            if method.upper() == 'POST':
                response = self.session.post(url, json=payload, headers=api_headers)
            else:
                response = self.session.get(url, params=payload, headers=api_headers)
                
            response.raise_for_status()
            
            # Parse the response JSON
            response_json = response.json()
            
            # FOGIS API returns data in a 'd' key
            if 'd' in response_json:
                # The 'd' value is a JSON string that needs to be parsed again
                if isinstance(response_json['d'], str):
                    try:
                        return json.loads(response_json['d'])
                    except json.JSONDecodeError:
                        # If it's not valid JSON, return as is
                        return response_json['d']
                else:
                    # If 'd' is already a dict/list, return it directly
                    return response_json['d']
            else:
                return response_json
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise FogisAPIRequestError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse API response: {e}")
            raise FogisDataError(f"Failed to parse API response: {e}")
