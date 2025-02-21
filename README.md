# fogis_api_client
### A Python client for interacting with the FOGIS API (Svensk Fotboll).

#### Features
* Authentication with FOGIS API.
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
#### Error Handling
The package includes custom exceptions for common API errors:

`FogisLoginError`: Raised when login fails.

`FogisAPIRequestError`: Raised for general API request errors.

---

#### Contributing
Contributions are welcome! Please open an issue or a pull request if you find any bugs or have suggestions.

---
#### License
MIT License