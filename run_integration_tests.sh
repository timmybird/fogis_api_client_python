#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p test-results

# Start the development environment if it's not already running
if ! docker ps | grep -q fogis-api-client-dev; then
    echo "Starting development environment..."
    docker compose -f docker-compose.dev.yml up -d fogis-api-client

    # Wait for the service to be healthy with a timeout
    echo "Waiting for API service to be healthy..."
    TIMEOUT=300  # 5 minutes timeout
    START_TIME=$(date +%s)

    while ! docker ps | grep -q "fogis-api-client-dev.*healthy"; do
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

        if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
            echo "Timeout waiting for API service to become healthy after $TIMEOUT seconds."
            echo "Checking container logs for errors:"
            docker logs fogis-api-client-dev
            echo "Container status:"
            docker ps | grep fogis-api-client-dev

            # Try to continue anyway, the tests will fail if the service is not working
            break
        fi

        echo "Still waiting... ($ELAPSED_TIME seconds elapsed)"
        sleep 5
    done
fi

# Run the integration tests
echo "Running integration tests..."
docker compose -f docker-compose.dev.yml run --rm integration-tests

# Show test results
echo "Integration tests completed."
