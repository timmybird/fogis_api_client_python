#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p test-results

# Ensure the Docker network exists
echo "Ensuring Docker network exists..."
# First remove any existing network with the same name that might not be created by compose
docker network rm fogis-network 2>/dev/null || true
# Then create a fresh network
docker network create fogis-network

# Start the development environment if it's not already running
if ! docker ps | grep -q fogis-api-client-dev; then
    echo "Starting development environment..."
    docker compose -f docker-compose.dev.yml up -d fogis-api-client

    # Wait for the service to be healthy with a timeout
    echo "Waiting for API service to be healthy..."
    TIMEOUT=60
    ELAPSED=0
    while ! docker ps | grep -q "fogis-api-client-dev.*healthy"; do
        sleep 2
        ELAPSED=$((ELAPSED+2))
        if [ $ELAPSED -ge $TIMEOUT ]; then
            echo "Timeout waiting for service to be healthy. Continuing anyway..."
            break
        fi
    done
fi

# Run the integration tests
echo "Running integration tests..."
docker compose -f docker-compose.dev.yml run --rm integration-tests

# Show test results
echo "Integration tests completed."
