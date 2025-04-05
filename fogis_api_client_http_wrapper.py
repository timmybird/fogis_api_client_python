import os
import signal
import sys
import logging
from flask import Flask, jsonify, request

try:
    from flask_cors import CORS  # Import CORS for development
except ImportError:
    # CORS is optional, only needed for development
    CORS = None

from fogis_api_client.fogis_api_client import FogisApiClient, FogisLoginError, FogisAPIRequestError, FogisDataError
from fogis_api_client.match_list_filter import MatchListFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get environment variables
fogis_username = os.environ.get("FOGIS_USERNAME", "test_user")
fogis_password = os.environ.get("FOGIS_PASSWORD", "test_pass")
debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"

# Initialize the Fogis API client but don't login yet
# Login will happen automatically when needed (lazy login)
client = FogisApiClient(fogis_username, fogis_password)

# Initialize the Flask app
app = Flask(__name__)
if CORS:
    CORS(app)  # Enable CORS for all routes if available


def handle_error(e, match_id=None, team_id=None):
    """
    Standardized error handling function that returns appropriate HTTP status codes
    and error messages based on the exception type.

    Args:
        e (Exception): The exception that was raised
        match_id (str, optional): The match ID that was being processed
        team_id (str, optional): The team ID that was being processed

    Returns:
        tuple: A tuple containing the JSON response and HTTP status code
    """
    context = {}
    if match_id:
        context["match_id"] = match_id
    if team_id:
        context["team_id"] = team_id

    if isinstance(e, FogisLoginError):
        logger.error(f"Login error: {str(e)}", extra=context)
        return jsonify({
            "error": "Authentication failed",
            "message": str(e),
            "error_type": "authentication_error"
        }), 401
    elif isinstance(e, FogisAPIRequestError):
        logger.error(f"API request error: {str(e)}", extra=context)
        return jsonify({
            "error": "Failed to communicate with FOGIS API",
            "message": str(e),
            "error_type": "api_error"
        }), 502  # Bad Gateway
    elif isinstance(e, FogisDataError):
        logger.error(f"Data error: {str(e)}", extra=context)
        return jsonify({
            "error": "Invalid data received from FOGIS API",
            "message": str(e),
            "error_type": "data_error"
        }), 500
    elif isinstance(e, ValueError):
        logger.warning(f"Validation error: {str(e)}", extra=context)
        return jsonify({
            "error": "Invalid input parameter",
            "message": str(e),
            "error_type": "validation_error"
        }), 400
    else:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True, extra=context)
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e),
            "error_type": "server_error"
        }), 500


@app.route("/")
def index():
    """
    Test endpoint to verify the API is running.
    """
    return jsonify({"status": "ok", "message": "Fogis API Client HTTP Wrapper"})


@app.route("/hello")
def hello():
    """
    Test endpoint that calls the hello_world method of the Fogis API Client.
    """
    return jsonify({"message": client.hello_world()})


@app.route("/matches")
def matches():
    """
    Endpoint to fetch matches list from Fogis API Client.
    """
    try:
        logger.info("Fetching matches list")
        matches_list = client.fetch_matches_list_json()
        logger.info(f"Successfully fetched {len(matches_list)} matches")
        return jsonify(matches_list)
    except Exception as e:
        return handle_error(e)


@app.route("/match/<match_id>")
def match(match_id):
    """
    Endpoint to fetch match details from Fogis API Client.
    """
    if not match_id:
        logger.warning("Match ID is required but was not provided")
        return jsonify({
            "error": "Match ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Fetching details for match {match_id}")
        match_data = client.fetch_match_json(match_id)
        logger.info(f"Successfully fetched details for match {match_id}")
        return jsonify(match_data)
    except Exception as e:
        return handle_error(e, match_id=match_id)


@app.route("/match/<match_id>/result")
def match_result(match_id):
    """
    Endpoint to fetch result information for a specific match.
    """
    if not match_id:
        logger.warning("Match ID is required but was not provided")
        return jsonify({
            "error": "Match ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Fetching result for match {match_id}")
        result_data = client.fetch_match_result_json(match_id)
        logger.info(f"Successfully fetched result for match {match_id}")
        return jsonify(result_data)
    except Exception as e:
        return handle_error(e, match_id=match_id)


@app.route("/match/<match_id>/events", methods=["GET"])
def match_events(match_id):
    """
    Endpoint to fetch events for a specific match.
    """
    if not match_id:
        logger.warning("Match ID is required but was not provided")
        return jsonify({
            "error": "Match ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Fetching events for match {match_id}")
        # Use the dedicated method for fetching match events
        events_data = client.fetch_match_events_json(match_id)
        logger.info(f"Successfully fetched {len(events_data)} events for match {match_id}")
        return jsonify(events_data)
    except Exception as e:
        return handle_error(e, match_id=match_id)


@app.route("/match/<match_id>/events", methods=["POST"])
def report_match_event(match_id):
    """
    Endpoint to report a new event for a match.
    """
    if not match_id:
        logger.warning("Match ID is required but was not provided")
        return jsonify({
            "error": "Match ID is required",
            "error_type": "validation_error"
        }), 400

    # Check if JSON data was provided
    if not request.is_json or not request.json:
        logger.warning(f"No event data provided for match {match_id}")
        return jsonify({
            "error": "No event data provided",
            "error_type": "validation_error"
        }), 400

    try:
        event_data = request.json
        logger.info(f"Reporting event for match {match_id}: {event_data}")

        # Add match_id to the event data if not already present
        if "matchid" not in event_data:
            event_data["matchid"] = match_id

        # Validate required fields
        if "type" not in event_data:
            logger.warning(f"Event type is required but was not provided for match {match_id}")
            return jsonify({
                "error": "Event type is required",
                "error_type": "validation_error"
            }), 400

        result = client.report_match_event(event_data)
        logger.info(f"Successfully reported event for match {match_id}")
        return jsonify(result)
    except Exception as e:
        return handle_error(e, match_id=match_id)


@app.route("/match/<match_id>/events/clear", methods=["POST"])
def clear_match_events(match_id):
    """
    Endpoint to clear all events for a match.
    """
    if not match_id:
        logger.warning("Match ID is required but was not provided")
        return jsonify({
            "error": "Match ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Clearing all events for match {match_id}")
        result = client.clear_match_events(match_id)
        logger.info(f"Successfully cleared all events for match {match_id}")
        return jsonify(result)
    except Exception as e:
        return handle_error(e, match_id=match_id)


@app.route("/match/<match_id>/officials")
def match_officials(match_id):
    """
    Endpoint to fetch officials information for a specific match.
    """
    if not match_id:
        logger.warning("Match ID is required but was not provided")
        return jsonify({
            "error": "Match ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Fetching officials for match {match_id}")
        officials_data = client.fetch_match_officials_json(match_id)
        logger.info(f"Successfully fetched officials for match {match_id}")
        return jsonify(officials_data)
    except Exception as e:
        return handle_error(e, match_id=match_id)


@app.route("/team/<team_id>/players")
def team_players(team_id):
    """
    Endpoint to fetch player information for a specific team.
    """
    if not team_id:
        logger.warning("Team ID is required but was not provided")
        return jsonify({
            "error": "Team ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Fetching players for team {team_id}")
        players_data = client.fetch_team_players_json(team_id)
        logger.info(f"Successfully fetched players for team {team_id}")
        return jsonify(players_data)
    except Exception as e:
        return handle_error(e, team_id=team_id)


@app.route("/team/<team_id>/officials")
def team_officials(team_id):
    """
    Endpoint to fetch officials information for a specific team.
    """
    if not team_id:
        logger.warning("Team ID is required but was not provided")
        return jsonify({
            "error": "Team ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Fetching officials for team {team_id}")
        officials_data = client.fetch_team_officials_json(team_id)
        logger.info(f"Successfully fetched officials for team {team_id}")
        return jsonify(officials_data)
    except Exception as e:
        return handle_error(e, team_id=team_id)


@app.route("/match/<match_id>/finish", methods=["POST"])
def finish_match_report(match_id):
    """
    Endpoint to mark a match report as completed/finished.
    """
    if not match_id:
        logger.warning("Match ID is required but was not provided")
        return jsonify({
            "error": "Match ID is required",
            "error_type": "validation_error"
        }), 400

    try:
        logger.info(f"Marking match {match_id} report as finished")
        result = client.mark_reporting_finished(match_id)
        logger.info(f"Successfully marked match {match_id} report as finished")
        return jsonify(result)
    except Exception as e:
        return handle_error(e, match_id=match_id)


@app.route("/matches/filter", methods=["POST"])
def filtered_matches():
    """
    Endpoint to fetch matches with specific filters.
    """
    try:
        filter_data = request.json or {}
        logger.info(f"Fetching matches with filters: {filter_data}")

        # Create a MatchListFilter with the provided filter data
        match_filter = MatchListFilter()

        # Apply filter parameters if they exist
        if "from_date" in filter_data:
            # Validate date format
            try:
                # Simple validation - could be enhanced with proper date parsing
                if not filter_data["from_date"] or len(filter_data["from_date"].split("-")) != 3:
                    return jsonify({
                        "error": "Invalid from_date format. Use YYYY-MM-DD",
                        "error_type": "validation_error"
                    }), 400
                match_filter.from_date = filter_data["from_date"]
            except (ValueError, AttributeError):
                logger.warning(f"Invalid from_date format: {filter_data['from_date']}")
                return jsonify({
                    "error": "Invalid from_date format. Use YYYY-MM-DD",
                    "error_type": "validation_error"
                }), 400

        if "to_date" in filter_data:
            # Validate date format
            try:
                # Simple validation - could be enhanced with proper date parsing
                if not filter_data["to_date"] or len(filter_data["to_date"].split("-")) != 3:
                    return jsonify({
                        "error": "Invalid to_date format. Use YYYY-MM-DD",
                        "error_type": "validation_error"
                    }), 400
                match_filter.to_date = filter_data["to_date"]
            except (ValueError, AttributeError):
                logger.warning(f"Invalid to_date format: {filter_data['to_date']}")
                return jsonify({
                    "error": "Invalid to_date format. Use YYYY-MM-DD",
                    "error_type": "validation_error"
                }), 400

        if "status" in filter_data:
            match_filter.status = filter_data["status"]
        if "age_category" in filter_data:
            match_filter.age_category = filter_data["age_category"]
        if "gender" in filter_data:
            match_filter.gender = filter_data["gender"]
        if "football_type" in filter_data:
            match_filter.football_type = filter_data["football_type"]

        # Fetch filtered matches
        matches_list = match_filter.fetch_filtered_matches(client)
        logger.info(f"Successfully fetched {len(matches_list)} matches with filters")
        return jsonify(matches_list)
    except Exception as e:
        return handle_error(e)


def signal_handler(sig, frame):
    """
    Handle SIGTERM and SIGINT signals to gracefully shut down the server.
    """
    print("Shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Start the Flask app
    app.run(host="0.0.0.0", port=8080, debug=debug_mode)
