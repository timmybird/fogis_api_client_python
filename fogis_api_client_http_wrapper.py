import os
import signal
import sys
from flask import Flask, jsonify, request

try:
    from flask_cors import CORS  # Import CORS for development
except ImportError:
    # CORS is optional, only needed for development
    CORS = None

from fogis_api_client.fogis_api_client import FogisApiClient

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
