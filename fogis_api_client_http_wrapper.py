import os
import signal
import sys
from flask import Flask, jsonify
try:
    from flask_cors import CORS  # Import CORS for development
except ImportError:
    # CORS is optional, only needed for development
    CORS = None

from fogis_api_client.fogis_api_client import FogisApiClient

# Get environment variables
fogis_username = os.environ.get("FOGIS_USERNAME")
fogis_password = os.environ.get("FOGIS_PASSWORD")
debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"

# Initialize the Fogis API client
client = FogisApiClient(fogis_username, fogis_password)
client.login()


# Import the Fogis API Client functions (for now, dummy functions)
# In the future, we will import the actual Fogis API Client library
def fetch_matches_list_from_fogis_api():
    """
    Dummy function to simulate fetching matches list from Fogis API Client.
    Replace with actual Fogis API Client call later.
    """
    return [
        {"match_id": "1", "team1": "Team A", "team2": "Team B", "date": "2024-01-20"},
        {"match_id": "2", "team1": "Team C", "team2": "Team D", "date": "2024-01-21"}
    ]


def fetch_match_details_from_fogis_api(match_id):
    """
    Dummy function to simulate fetching match details from Fogis API Client.
    Replace with actual Fogis API Client call later.
    """
    return {
        "match_id": match_id,
        "team1": "Team X",
        "team2": "Team Y",
        "date": "2024-01-25",
        "referees": ["Referee 1", "Assistant Referee 1", "Assistant Referee 2"]
    }


app = Flask(__name__)
if CORS is not None:
    CORS(app)  # Enable CORS for development


@app.route('/matches')
def get_matches_list():
    """
    API endpoint to return a list of matches.
    Calls the Fogis API Client (dummy function for now).
    """
    matches = client.fetch_matches_list_json()
    return jsonify(matches)


@app.route('/match/<match_id>')
def get_match_details(match_id):
    """
    API endpoint to return details for a specific match.
    Calls the Fogis API Client (dummy function for now).
    """
    match_detail = fetch_match_details_from_fogis_api(match_id)
    return jsonify(match_detail)


@app.route('/hello')
def hello():
    return jsonify(client.hello_world())


@app.route('/')
def index():
    my_list = [{"item": 1}, {"item": 2}, {"unicode_item": "åäö"}]  # List as data
    return jsonify(my_list, ensure_ascii=False)


# Handle signals for graceful shutdown
def signal_handler(sig, frame):
    print('Received shutdown signal, exiting gracefully...')
    # Perform any cleanup here if needed
    sys.exit(0)


if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Use threaded mode in development for hot reloading
    if debug_mode:
        print("Running in DEBUG mode")
        app.run(host='0.0.0.0', port=8080, debug=True)
    else:
        print("Running in PRODUCTION mode")
        # Use threaded=False to avoid issues with signal handling in production
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=False)
