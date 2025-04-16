"""
Pytest fixtures for integration tests with the mock FOGIS API server.
"""
import logging
import multiprocessing
import time
from typing import Dict, Generator

import pytest
import requests

from integration_tests.mock_fogis_server import MockFogisServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_mock_server(host: str, port: int) -> None:
    """
    Start the mock FOGIS API server in a separate process.

    Args:
        host: The host to run the server on
        port: The port to run the server on
    """
    server = MockFogisServer(host=host, port=port)
    server.run()


@pytest.fixture(scope="session")
def mock_fogis_server() -> Generator[Dict[str, str], None, None]:
    """
    Fixture that starts a mock FOGIS API server for testing.

    Yields:
        Dict with server information including the base URL
    """
    # Use a random available port
    host = "127.0.0.1"
    port = 5000

    # Start the server in a separate process
    server_process = multiprocessing.Process(
        target=start_mock_server,
        args=(host, port),
    )
    server_process.daemon = True
    server_process.start()

    # Wait for the server to start
    base_url = f"http://{host}:{port}"
    max_retries = 5
    retry_delay = 1

    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                logger.info(f"Mock FOGIS server started at {base_url}")
                break
        except requests.exceptions.ConnectionError:
            pass

        logger.info(f"Waiting for mock FOGIS server to start (attempt {i+1}/{max_retries})...")
        time.sleep(retry_delay)
    else:
        server_process.terminate()
        raise RuntimeError("Failed to start mock FOGIS server")

    # Yield the server information
    yield {
        "base_url": base_url,
        "host": host,
        "port": str(port),
    }

    # Clean up
    logger.info("Stopping mock FOGIS server")
    server_process.terminate()
    server_process.join(timeout=5)
    if server_process.is_alive():
        logger.warning("Mock FOGIS server process did not terminate gracefully, forcing...")
        server_process.kill()


@pytest.fixture
def test_credentials() -> Dict[str, str]:
    """
    Fixture that provides test credentials for the mock FOGIS API.

    Returns:
        Dict with username and password
    """
    return {
        "username": "test_user",
        "password": "test_password",
    }
