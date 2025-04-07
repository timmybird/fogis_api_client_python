# fogis_api_client
### A Python client for interacting with the FOGIS API (Svensk Fotboll).

#### Features
* Authentication with FOGIS API.
* Lazy login - automatically authenticates when needed.
* Fetching match lists, team players, officials, and events.
* Reporting match events and results.
* Error handling and logging.
---
#### Installation
```bash
pip install fogis-api-client-timmyBird
```
---
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

The HTTP API wrapper provides the following endpoints:

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

##### Pre-Merge Check

Before merging any changes, always run the pre-merge check script to ensure all tests pass:

```bash
./pre-merge-check.sh
```

This script:
- Runs all unit tests
- Builds and tests the Docker image (if Docker is available)
- Ensures your changes won't break existing functionality

---
#### Error Handling
The package includes custom exceptions for common API errors:

`FogisLoginError`: Raised when login fails.

`FogisAPIRequestError`: Raised for general API request errors.

---
#### License
MIT License
