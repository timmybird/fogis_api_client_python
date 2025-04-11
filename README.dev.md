# Fogis API Client - Development Guide

This guide explains how to set up and use the development environment for the Fogis API Client.

## Development Environment

We provide a Docker-based development environment that makes it easy to develop and test the API client.

### Prerequisites

- Docker and Docker Compose
- Git

### Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fogis_api_client_python.git
   cd fogis_api_client_python
   ```

2. Create a `.env.dev` file with your development credentials:
   ```
   FOGIS_USERNAME=your_dev_username
   FOGIS_PASSWORD=your_dev_password
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

3. Start the development environment:
   ```
   ./dev.sh
   ```

   This will:
   - Build the Docker image for development
   - Start the container with the API client
   - Mount your local code into the container for live reloading
   - Show the logs from the container

4. Access the API at http://localhost:8080

### Running Integration Tests

To run the integration tests:

```
./run_integration_tests.sh
```

This will:
- Start the development environment if it's not already running
- Run the integration tests against the API
- Show the test results

### Development Workflow

1. Make changes to the code
2. The Flask server will automatically reload when you change Python files
3. Run the integration tests to verify your changes
4. Commit your changes when ready

### Docker Compose Configuration

The development environment uses `docker-compose.dev.yml`, which includes:

- Volume mounts for live code reloading
- Debug mode enabled
- Integration test service

### Project Structure

- `fogis_api_client/` - The main package
- `tests/` - Unit tests
- `integration_tests/` - Integration tests
- `docker-compose.dev.yml` - Development Docker Compose configuration
- `docker-compose.yml` - Production Docker Compose configuration
- `Dockerfile.dev` - Development Dockerfile
- `Dockerfile` - Production Dockerfile

## Contributing

1. Create a feature branch
2. Make your changes
3. Run the tests
4. Submit a pull request
