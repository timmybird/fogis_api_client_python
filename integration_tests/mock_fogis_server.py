"""
Mock FOGIS API Server for integration testing.

This module provides a Flask-based mock server that simulates the FOGIS API endpoints
for integration testing without requiring real credentials or internet access.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List

from flask import Flask, Response, jsonify, request, session

# Import data factory for the mock server
from integration_tests.sample_data_factory import MockDataFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockFogisServer:
    """
    A Flask-based mock server that simulates the FOGIS API endpoints.
    """

    def __init__(self, host: str = "localhost", port: int = 5000):
        """
        Initialize the mock server.

        Args:
            host: The host to run the server on
            port: The port to run the server on
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.app.secret_key = "mock_fogis_server_secret_key"

        # Store registered users
        self.users = {
            "test_user": "test_password",
        }

        # Store session data
        self.sessions: Dict[str, Dict] = {}

        # Store reported events
        self.reported_events: List[Dict] = []

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register the API routes."""

        # Login route
        @self.app.route("/mdk/Login.aspx", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                # Try both field name formats
                username = request.form.get("ctl00$cphMain$tbUsername") or request.form.get(
                    "ctl00$MainContent$UserName"
                )
                password = request.form.get("ctl00$cphMain$tbPassword") or request.form.get(
                    "ctl00$MainContent$Password"
                )

                if username in self.users and self.users[username] == password:
                    # Successful login
                    session["authenticated"] = True
                    session["username"] = username

                    # Set cookies - use the same cookie names as expected by the client
                    # The client checks for FogisMobilDomarKlient.ASPXAUTH (with a dot)
                    resp = Response("Login successful")
                    resp.set_cookie("FogisMobilDomarKlient.ASPXAUTH", "mock_auth_cookie")
                    resp.set_cookie("ASP.NET_SessionId", "mock_session_id")
                    resp.headers["Location"] = "/mdk/"
                    resp.status_code = 302
                    return resp
                else:
                    # Failed login - return 200 with a login page that has an error message
                    # This matches the behavior of the real FOGIS API
                    return """
                    <html>
                    <body>
                        <div class="error-message">Invalid username or password</div>
                        <form method="post" id="aspnetForm">
                            <input type="hidden" name="__VIEWSTATE"
                                value="viewstate_value" />
                            <input type="hidden" name="__EVENTVALIDATION"
                                value="eventvalidation_value" />
                            <input type="text" name="ctl00$cphMain$tbUsername" />
                            <input type="password" name="ctl00$cphMain$tbPassword" />
                            <input type="text" name="ctl00$MainContent$UserName" />
                            <input type="password" name="ctl00$MainContent$Password" />
                            <input type="submit" name="ctl00$cphMain$btnLogin" value="Logga in" />
                            <input type="submit" name="ctl00$MainContent$LoginButton"
                                value="Logga in" />
                        </form>
                    </body>
                    </html>
                    """
            else:
                # Return a mock login page with form fields
                return """
                <html>
                <body>
                    <form method="post" id="aspnetForm">
                        <input type="hidden" name="__VIEWSTATE"
                            value="viewstate_value" />
                        <input type="hidden" name="__EVENTVALIDATION"
                            value="eventvalidation_value" />
                        <input type="text" name="ctl00$cphMain$tbUsername" />
                        <input type="password" name="ctl00$cphMain$tbPassword" />
                        <input type="text" name="ctl00$MainContent$UserName" />
                        <input type="password" name="ctl00$MainContent$Password" />
                        <input type="submit" name="ctl00$cphMain$btnLogin" value="Logga in" />
                        <input type="submit" name="ctl00$MainContent$LoginButton"
                            value="Logga in" />
                    </form>
                </body>
                </html>
                """

        # Match list endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/HamtaMatchLista", methods=["POST"])
        def fetch_matches_list():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Parse filter from request (not used in mock implementation)
            # request.json would contain filter parameters in a real implementation

            # Generate a fresh match list using the factory
            match_list_response = MockDataFactory.generate_match_list()

            # Return the response
            return jsonify(match_list_response)

        # Match details endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/HamtaMatch", methods=["POST"])
        def fetch_match():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate match details using the factory
            match_data = MockDataFactory.generate_match_details(match_id)

            return jsonify({"d": json.dumps(match_data)})

        # Match players endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/HamtaMatchSpelare", methods=["POST"])
        def fetch_match_players():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate players data using the factory
            players_data = MockDataFactory.generate_match_players(match_id)

            # For match players, we need to keep the JSON structure
            return jsonify({"d": json.dumps(players_data)})

        # Match officials endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/HamtaMatchFunktionarer", methods=["POST"])
        def fetch_match_officials():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate officials data using the factory
            officials_data = MockDataFactory.generate_match_officials(match_id)

            # For match officials, we need to keep the JSON structure
            return jsonify({"d": json.dumps(officials_data)})

        # Match events endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/HamtaMatchHandelser", methods=["POST"])
        def fetch_match_events():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate events data using the factory
            events_data = MockDataFactory.generate_match_events(match_id)

            # For match events, the response format is different
            # It's a direct array in the "d" field rather than a JSON string
            return jsonify({"d": events_data})

        # Match result endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/GetMatchresultatlista", methods=["POST"])
        def fetch_match_result():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate result data using the factory
            result_data = MockDataFactory.generate_match_result(match_id)

            # For match results, the response format is different -
            # it's a direct array in the "d" field
            # rather than a JSON string
            return jsonify({"d": result_data})

        # Report match event endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/SparaMatchhandelse", methods=["POST"])
        def report_match_event():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get event data from request
            event_data = request.json or {}

            # Store the reported event
            self.reported_events.append(event_data)

            # Return success response
            return jsonify({"d": json.dumps({"success": True, "id": len(self.reported_events)})})

        # Clear match events endpoint
        @self.app.route("/mdk/MatchWebMetoder.aspx/RensaMatchhandelser", methods=["POST"])
        @self.app.route("/mdk/Fogis/Match/ClearMatchEvents", methods=["POST"])
        def clear_match_events():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request (not used in mock implementation)
            # In a real implementation, we would use match_id to clear specific events

            # Clear all events (simplified implementation)
            self.reported_events = []

            # Return success response
            return jsonify({"d": json.dumps({"success": True})})

        # Mark reporting finished endpoint
        @self.app.route("/mdk/Fogis/Match/SparaMatchGodkannDomarrapport", methods=["POST"])
        def mark_reporting_finished():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request (not used in mock implementation)
            # In a real implementation, we would use match_id to mark specific match as reported

            # Return success response with a dictionary containing success=true
            # This matches what the client expects
            return jsonify({"d": json.dumps({"success": True})})

        # Team players endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/GetMatchdeltagareListaForMatchlag", methods=["POST"]
        )
        def fetch_team_players_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get team ID from request
            data = request.json or {}
            team_id = data.get("matchlagid")  # Use the correct parameter name

            # Generate team players data using the factory
            players_data = MockDataFactory.generate_team_players(team_id)

            # Return the response
            return jsonify({"d": json.dumps(players_data)})

        # Team officials endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/GetMatchlagledareListaForMatchlag", methods=["POST"]
        )
        def fetch_team_officials_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get team ID from request
            data = request.json or {}
            team_id = data.get("matchlagid")  # Use the correct parameter name

            # Generate team officials data using the factory
            officials_data = MockDataFactory.generate_team_officials(team_id)

            # Return the response
            return jsonify({"d": json.dumps(officials_data)})

        # Match details endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/GetMatch", methods=["POST"]
        )
        def fetch_match_details_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate match data using the factory
            match_data = MockDataFactory.generate_match_details(match_id)

            # Return the response
            return jsonify({"d": json.dumps(match_data)})

        # Match players endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/GetMatchdeltagareLista", methods=["POST"]
        )
        def fetch_match_players_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate match players data using the factory
            players_data = MockDataFactory.generate_match_players(match_id)

            # Return the response
            return jsonify({"d": json.dumps(players_data)})

        # Match officials endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/GetMatchfunktionarerLista", methods=["POST"]
        )
        def fetch_match_officials_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate match officials data using the factory
            officials_data = MockDataFactory.generate_match_officials(match_id)

            # Return the response
            return jsonify({"d": json.dumps(officials_data)})

        # Match events endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/GetMatchhandelselista", methods=["POST"]
        )
        def fetch_match_events_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate match events data using the factory
            events_data = MockDataFactory.generate_match_events(match_id)

            # Return the response
            return jsonify({"d": json.dumps(events_data)})

        # Match result endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/GetMatchresultat", methods=["POST"]
        )
        def fetch_match_result_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Get match ID from request
            data = request.json or {}
            match_id = data.get("matchid")

            # Generate match result data using the factory
            result_data = MockDataFactory.generate_match_result(match_id)

            # Return the response
            return jsonify({"d": json.dumps(result_data)})

        # Clear match events endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/ClearMatchEvents", methods=["POST"]
        )
        def clear_match_events_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Return success response
            return jsonify({"d": json.dumps({"success": True})})

        # Report match event endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/SparaMatchhandelse", methods=["POST"]
        )
        def report_match_event_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Return success response
            return jsonify({"d": json.dumps({"success": True})})

        # Mark reporting finished endpoint
        @self.app.route(
            "/mdk/MatchWebMetoder.aspx/SparaMatchGodkannDomarrapport", methods=["POST"]
        )
        def mark_reporting_finished_endpoint():
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Return success response
            return jsonify({"d": json.dumps({"success": True})})

        # Main dashboard route after login
        @self.app.route("/mdk/", methods=["GET"])
        def dashboard():
            # Check if the user is authenticated
            auth_result = self._check_auth()
            if auth_result is not True:
                return auth_result

            # Return a simple dashboard page
            return "<html><body><h1>FOGIS Mock Dashboard</h1></body></html>"

        # Health check endpoint
        @self.app.route("/health", methods=["GET"])
        def health():
            return jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Hello world endpoint (for testing)
        @self.app.route("/hello", methods=["GET"])
        def hello():
            return jsonify({"message": "Hello, brave new world!"})

    def _check_auth(self):
        """Check if the request is authenticated."""
        # Check if the user is authenticated via session or cookies
        if session.get("authenticated") or request.cookies.get("FogisMobilDomarKlient.ASPXAUTH"):
            return True

        # For testing purposes, we'll also accept cookie-based authentication
        if "FogisMobilDomarKlient.ASPXAUTH" in request.cookies:
            return True

        # If we're here, the user is not authenticated
        return Response("Unauthorized", status=401)

    def run(self):
        """Run the mock server."""
        logger.info(f"Starting mock FOGIS server on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port)

    def get_url(self) -> str:
        """Get the URL of the mock server."""
        return f"http://{self.host}:{self.port}"


if __name__ == "__main__":
    # Run the mock server when executed directly
    server = MockFogisServer()
    server.run()
