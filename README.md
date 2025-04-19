# FOGIS API Client

[![PyPI version](https://badge.fury.io/py/fogis-api-client-timmyBird.svg)](https://badge.fury.io/py/fogis-api-client-timmyBird)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for interacting with the FOGIS API (Svenska Fotbollförbundet).

## Features

* **Authentication Options**: Login with credentials or session cookies
* **Lazy Authentication**: Automatically authenticates when needed
* **Match Management**: Fetch match lists, details, and results
* **Event Reporting**: Report goals, cards, substitutions, and other match events
* **Team Information**: Access team players, officials, and match assignments
* **Type Safety**: Comprehensive type annotations for better IDE support
* **Error Handling**: Detailed error messages and exception handling
* **Logging**: Built-in logging for debugging and monitoring
* **Docker Support**: Easy deployment and development with Docker

## Installation

### Using pip

```bash
pip install fogis-api-client-timmyBird
```

### From Source

```bash
git clone https://github.com/timmybird/fogis_api_client_python.git
cd fogis_api_client_python
pip install -e .
```

### Using Docker

```bash
# Pull the Docker image
docker pull timmybird/fogis_api_client_python:latest

# Run a script using the Docker image
docker run --rm -v $(pwd):/app \
  -e FOGIS_USERNAME="your_username" \
  -e FOGIS_PASSWORD="your_password" \
  timmybird/fogis_api_client_python:latest \
  python /app/your_script.py
```

See the [Docker Usage](docs/getting_started.md#docker-usage) section in the documentation for more details.

## Quick Start

```python
from fogis_api_client import FogisApiClient, FogisLoginError, FogisAPIRequestError, configure_logging

# Configure logging with enhanced options
configure_logging(level="INFO")

# Initialize with credentials
client = FogisApiClient(username="your_username", password="your_password")

# Fetch matches (lazy login happens automatically)
try:
    matches = client.fetch_matches_list_json()
    print(f"Found {len(matches)} matches")

    # Display the next 3 matches
    for match in matches[:3]:
        print(f"{match['datum']} {match['tid']}: {match['hemmalag']} vs {match['bortalag']} at {match['arena']}")

except FogisLoginError as e:
    print(f"Authentication error: {e}")
except FogisAPIRequestError as e:
    print(f"API request error: {e}")
```

## Documentation

Comprehensive documentation is available in the [docs](docs/) directory:

* [Getting Started Guide](docs/getting_started.md)
* [API Reference](docs/api_reference.md)
* [User Guides](docs/user_guides/)
* [Architecture Overview](docs/architecture.md)
* [Troubleshooting](docs/troubleshooting.md)

#### Usage

```python
import logging
from fogis_api_client.fogis_api_client import FogisApiClient, FogisLoginError, FogisAPIRequestError

logging.basicConfig(level=logging.INFO)

username = "your_fogis_username"
password = "your_fogis_password"

try:
    client = FogisApiClient(username, password)
    # No need to call login() explicitly - the client implements lazy login
    matches = client.fetch_matches_list_json()
    if matches:
        print(f"Found {len(matches)} matches.")
    else:
        print("No matches found.")
except FogisLoginError as e:
    print(f"Login failed: {e}")
except FogisAPIRequestError as e:
    print(f"API request error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

You can also call `login()` explicitly if you want to pre-authenticate:

```python
client = FogisApiClient(username, password)
client.login()  # Explicitly authenticate
# ... make API requests
```

#### Cookie-Based Authentication

For improved security, you can authenticate using cookies instead of storing credentials:

```python
# First, get cookies from a logged-in session
client = FogisApiClient(username, password)
client.login()
cookies = client.get_cookies()  # Save these cookies securely

# Later, in another session, use the saved cookies
client = FogisApiClient(cookies=cookies)
# No need to call login() - already authenticated with cookies
matches = client.fetch_matches_list_json()
```

You can validate if the cookies are still valid:

```python
client = FogisApiClient(cookies=cookies)
if client.validate_cookies():
    print("Cookies are valid")
else:
    print("Cookies have expired, need to login with credentials again")
```

---
#### Docker Support

The package includes Docker support for easy deployment and development:

##### Production Deployment

1. Create a `.env` file with your credentials:
   ```
   FOGIS_USERNAME=your_fogis_username
   FOGIS_PASSWORD=your_fogis_password
   ```

2. Start the service:
   ```bash
   docker compose up -d
   ```

3. Access the API at http://localhost:8080

##### Development Environment

For development, we provide a more comprehensive setup:

1. Start the development environment:
   ```bash
   ./dev.sh
   ```

2. Run integration tests:
   ```bash
   ./run_integration_tests.sh
   ```

For more details on the development environment, see [README.dev.md](README.dev.md).

---
#### API Endpoints

The FOGIS API Gateway provides the following endpoints:

##### Basic Endpoints
- `GET /` - Returns a test JSON response
- `GET /hello` - Returns a simple hello world message

##### Match Endpoints
- `GET /matches` - Returns a list of matches
- `POST /matches/filter` - Returns a filtered list of matches based on provided criteria
- `GET /match/<match_id>` - Returns details for a specific match
- `GET /match/<match_id>/result` - Returns result information for a specific match
- `GET /match/<match_id>/officials` - Returns officials information for a specific match
- `POST /match/<match_id>/finish` - Marks a match report as completed/finished

##### Match Events Endpoints
- `GET /match/<match_id>/events` - Returns events for a specific match
- `POST /match/<match_id>/events` - Reports a new event for a match
- `POST /match/<match_id>/events/clear` - Clears all events for a match

##### Team Endpoints
- `GET /team/<team_id>/players` - Returns player information for a specific team
- `GET /team/<team_id>/officials` - Returns officials information for a specific team

#### Query Parameters

Many endpoints support query parameters for filtering, sorting, and pagination:

##### `/matches` Endpoint
- `from_date` - Start date for filtering matches (format: YYYY-MM-DD)
- `to_date` - End date for filtering matches (format: YYYY-MM-DD)
- `limit` - Maximum number of matches to return
- `offset` - Number of matches to skip (for pagination)
- `sort_by` - Field to sort by (options: datum, hemmalag, bortalag, tavling)
- `order` - Sort order, 'asc' or 'desc'

##### `/match/<match_id>` Endpoint
- `include_events` - Whether to include events in the response (default: true)
- `include_players` - Whether to include players in the response (default: false)
- `include_officials` - Whether to include officials in the response (default: false)

##### `/match/<match_id>/events` Endpoint
- `type` - Filter events by type (e.g., 'goal', 'card', 'substitution')
- `player` - Filter events by player name
- `team` - Filter events by team name
- `limit` - Maximum number of events to return
- `offset` - Number of events to skip (for pagination)
- `sort_by` - Field to sort by (options: time, type, player, team)
- `order` - Sort order, 'asc' or 'desc'

##### `/team/<team_id>/players` Endpoint
- `name` - Filter players by name
- `position` - Filter players by position
- `number` - Filter players by jersey number
- `limit` - Maximum number of players to return
- `offset` - Number of players to skip (for pagination)
- `sort_by` - Field to sort by (options: name, position, number)
- `order` - Sort order, 'asc' or 'desc'

##### `/team/<team_id>/officials` Endpoint
- `name` - Filter officials by name
- `role` - Filter officials by role
- `limit` - Maximum number of officials to return
- `offset` - Number of officials to skip (for pagination)
- `sort_by` - Field to sort by (options: name, role)
- `order` - Sort order, 'asc' or 'desc'

##### Filter Parameters for `/matches/filter` Endpoint
The `/matches/filter` endpoint accepts the following parameters in the request body (JSON):
- `from_date` - Start date for filtering matches (format: YYYY-MM-DD)
- `to_date` - End date for filtering matches (format: YYYY-MM-DD)
- `status` - Match status (e.g., "upcoming", "completed")
- `age_category` - Age category for filtering matches
- `gender` - Gender for filtering matches
- `football_type` - Type of football (e.g., "indoor", "outdoor")

---
#### Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run the pre-merge check to ensure all tests pass:
   ```bash
   ./pre-merge-check.sh
   ```
5. Commit your changes: `git commit -m "Add your feature"`
6. Push to the branch: `git push origin feature/your-feature-name`
7. Create a pull request

##### Pre-Commit Hooks

We use pre-commit hooks to ensure code quality. To set up pre-commit hooks, use our setup script:

```bash
./setup_precommit.sh
```

This script will install pre-commit, set up the hooks, and verify the installation works correctly.

Alternatively, you can set up manually:

```bash
pip install pre-commit
pre-commit install
pip install pytest pytest-cov types-requests
```

The hooks will automatically run before each commit, checking for:
- Code formatting (Black, isort)
- Linting issues (flake8)
- Type checking (mypy)
- Tests (using unittest, compatible with the project's test suite)
- Optional: pytest tests and documentation freshness checks

For more details on pre-commit hooks, see [CONTRIBUTING.md](CONTRIBUTING.md#pre-commit-hooks).

##### Pre-Merge Check

Before merging any changes, always run the pre-merge check script to ensure all tests pass:

```bash
./pre-merge-check.sh
```

This script:
- Runs all unit tests
- Builds and tests the Docker image (if Docker is available)
- Ensures your changes won't break existing functionality

## Troubleshooting

If you encounter issues while using the FOGIS API Client, check the [Troubleshooting Guide](docs/troubleshooting.md) for solutions to common problems.

### Common Issues

1. **Authentication Failures**
   - Check your credentials
   - Verify your account is active
   - Ensure you have the necessary permissions

2. **API Request Errors**
   - Check your network connection
   - Verify the FOGIS API is accessible
   - Ensure your request parameters are valid

3. **Data Errors**
   - Verify that the requested resource exists
   - Check for API changes
   - Ensure your data is properly formatted

4. **Match Reporting Issues**
   - Ensure all required fields are included
   - Verify that the match is in a reportable state
   - Check that player and team IDs are correct

5. **Performance Issues**
   - Implement caching for frequently accessed data
   - Use more specific queries to reduce data size
   - Process large data sets in chunks

## Error Handling

The package includes custom exceptions for common API errors:

- **FogisLoginError**: Raised when login fails due to invalid credentials, missing credentials, or session expiration.

- **FogisAPIRequestError**: Raised for general API request errors such as network issues, server errors, or invalid parameters.

- **FogisDataError**: Raised when there's an issue with the data from FOGIS, such as invalid response format, missing fields, or parsing errors.

## License

MIT License
