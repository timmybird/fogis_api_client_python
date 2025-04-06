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

from fogis_api_client.fogis_api_client import FogisApiClient
from fogis_api_client.match_list_filter import MatchListFilter
from fogis_api_client_swagger import get_swagger_blueprint, spec

# Get environment variables
fogis_username = os.environ.get("FOGIS_USERNAME", "test_user")
fogis_password = os.environ.get("FOGIS_PASSWORD", "test_pass")
debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"

# Initialize the Fogis API client but don't login yet
# Login will happen automatically when needed (lazy login)
client = FogisApiClient(fogis_username, fogis_password)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize the Flask app
app = Flask(__name__)
if CORS:
    CORS(app)  # Enable CORS for all routes if available

# Register Swagger UI blueprint
swagger_ui_blueprint, SWAGGER_URL, API_URL = get_swagger_blueprint()
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Add endpoint to serve the OpenAPI specification
@app.route('/api/swagger.json')
def get_swagger():
    return jsonify(spec.to_dict())


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
        matches_list = client.fetch_matches_list_json()
        return jsonify(matches_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/match/<match_id>")
def match(match_id):
    """
    Endpoint to fetch match details from Fogis API Client.
    """
    try:
        match_data = client.fetch_match_json(match_id)
        return jsonify(match_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/match/<match_id>/result")
def match_result(match_id):
    """
    Endpoint to fetch result information for a specific match.
    """
    try:
        result_data = client.fetch_match_result_json(match_id)
        return jsonify(result_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/match/<match_id>/events", methods=["GET"])
def match_events(match_id):
    """
    Endpoint to fetch events for a specific match.
    """
    try:
        # Use the dedicated method for fetching match events
        events_data = client.fetch_match_events_json(match_id)
        return jsonify(events_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/match/<match_id>/events", methods=["POST"])
def report_match_event(match_id):
    """
    Endpoint to report a new event for a match.
    """
    # Check if JSON data was provided
    if not request.is_json or not request.json:
        return jsonify({"error": "No event data provided"}), 400

    try:
        event_data = request.json

        # Add match_id to the event data if not already present
        if "matchid" not in event_data:
            event_data["matchid"] = match_id

        result = client.report_match_event(event_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/match/<match_id>/events/clear", methods=["POST"])
def clear_match_events(match_id):
    """
    Endpoint to clear all events for a match.
    """
    try:
        result = client.clear_match_events(match_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/match/<match_id>/officials")
def match_officials(match_id):
    """
    Endpoint to fetch officials information for a specific match.
    """
    try:
        officials_data = client.fetch_match_officials_json(match_id)
        return jsonify(officials_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/team/<team_id>/players")
def team_players(team_id):
    """
    Endpoint to fetch player information for a specific team.
    """
    try:
        players_data = client.fetch_team_players_json(team_id)
        return jsonify(players_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/team/<team_id>/officials")
def team_officials(team_id):
    """
    Endpoint to fetch officials information for a specific team.
    """
    try:
        officials_data = client.fetch_team_officials_json(team_id)
        return jsonify(officials_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/match/<match_id>/finish", methods=["POST"])
def finish_match_report(match_id):
    """
    Endpoint to mark a match report as completed/finished.
    """
    try:
        result = client.mark_reporting_finished(match_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/matches/filter", methods=["POST"])
def filtered_matches():
    """
    Endpoint to fetch matches with specific filters.
    """
    try:
        filter_data = request.json or {}

        # Create a MatchListFilter with the provided filter data
        match_filter = MatchListFilter()

        # Apply filter parameters if they exist
        if "from_date" in filter_data:
            match_filter.from_date = filter_data["from_date"]
        if "to_date" in filter_data:
            match_filter.to_date = filter_data["to_date"]
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
        return jsonify(matches_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
