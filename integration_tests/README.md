# Integration Tests with Mock FOGIS API Server

This directory contains integration tests for the FOGIS API client using a mock server. These tests verify that the client can interact correctly with the API without requiring real credentials or internet access.

## Overview

The integration tests use a Flask-based mock server that simulates the FOGIS API endpoints. The mock server provides responses that match the structure of the real API, allowing us to test the client's functionality without making actual API calls.

## Components

- `mock_fogis_server.py`: Implementation of the mock FOGIS API server
- `sample_data.py`: Sample data structures that mimic the responses from the FOGIS API
- `conftest.py`: Pytest fixtures for setting up the mock server and test environment
- `test_with_mock_server.py`: Integration tests for the FOGIS API client

## Running the Tests

To run the integration tests:

```bash
python -m pytest integration_tests/test_with_mock_server.py -v
```

## Adding New Tests

To add new tests:

1. Add any necessary sample data to `sample_data.py`
2. Add new endpoints to `mock_fogis_server.py` if needed
3. Create new test methods in `test_with_mock_server.py`

## Extending the Mock Server

To add support for new API endpoints:

1. Add a new route handler in the `_register_routes` method of the `MockFogisServer` class
2. Create sample data for the new endpoint in `sample_data.py`
3. Implement the route handler to return the sample data

Example:

```python
# In mock_fogis_server.py
@self.app.route("/mdk/MatchWebMetoder.aspx/NewEndpoint", methods=["POST"])
def new_endpoint():
    self._check_auth()

    # Get data from request
    data = request.json or {}

    # Return sample data
    return jsonify({"d": json.dumps(SAMPLE_NEW_ENDPOINT_DATA)})
```

## Troubleshooting

If you encounter issues with the mock server:

1. Check the logs for error messages
2. Verify that the mock server is running on the expected port
3. Ensure that the sample data matches the structure expected by the client
4. Check that the route paths match the ones used by the client

## Notes

- The mock server runs in a separate process during tests
- The server is automatically started and stopped by the pytest fixtures
- The client's `BASE_URL` is temporarily overridden to point to the mock server
- Test credentials are provided by the `test_credentials` fixture
