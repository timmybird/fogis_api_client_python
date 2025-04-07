#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p test-results

# Start the development environment if it's not already running
if ! docker ps | grep -q fogis-api-client-dev; then
    echo "Starting development environment..."
    docker compose -f docker-compose.dev.yml up -d fogis-api-client
    
    # Wait for the service to be healthy
    echo "Waiting for API service to be healthy..."
    while ! docker ps | grep -q "fogis-api-client-dev.*healthy"; do
        sleep 2
    done
fi

# Run the integration tests
echo "Running integration tests..."
docker compose -f docker-compose.dev.yml run --rm integration-tests

# Show test results
echo "Integration tests completed."
