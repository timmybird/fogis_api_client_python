#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p test-results

# Create Docker network if it doesn't exist
echo "Creating Docker network if it doesn't exist..."
docker network create fogis-network 2>/dev/null || true

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
