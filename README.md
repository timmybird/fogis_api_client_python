# fogis_api_client
### A Python client for interacting with the FOGIS API (Svensk Fotboll).

#### Features
* Authentication with FOGIS API.
* Fetching match lists, team players, officials, and events.
* Reporting match events and results.
* Error handling and logging.
* HTTP API wrapper with Docker support
* Development environment with integration tests

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
    client.login()
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

- `GET /` - Returns a test JSON response
- `GET /hello` - Returns a simple hello world message
- `GET /matches` - Returns a list of matches
- `GET /match/<match_id>` - Returns details for a specific match

---
#### Error Handling
The package includes custom exceptions for common API errors:

`FogisLoginError`: Raised when login fails.

`FogisAPIRequestError`: Raised for general API request errors.

---

#### Contributing
Contributions are welcome! Please open an issue or a pull request if you find any bugs or have suggestions.

See [README.dev.md](README.dev.md) for development setup instructions.

---
#### License
MIT License
