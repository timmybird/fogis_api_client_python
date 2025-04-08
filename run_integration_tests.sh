#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p test-results

# Start the development environment if it's not already running
if ! docker ps | grep -q fogis-api-client-dev; then
    echo "Starting development environment..."

    # Remove any existing containers to ensure a clean start
    docker compose -f docker-compose.dev.yml down -v 2>/dev/null || true

    # Create the network if it doesn't exist
    docker network create fogis-network 2>/dev/null || true

    # Start the service in the foreground to see logs
    echo "Starting API service and showing logs for 10 seconds..."
    docker compose -f docker-compose.dev.yml up fogis-api-client &
    DOCKER_PID=$!
    sleep 10
    kill $DOCKER_PID 2>/dev/null || true

    # Now start it in the background
    echo "Starting API service in the background..."
    docker compose -f docker-compose.dev.yml up -d fogis-api-client

    # Wait for the service to be healthy with a timeout
    echo "Waiting for API service to be healthy..."
    TIMEOUT=300  # 5 minutes timeout
    START_TIME=$(date +%s)

    # Try to manually check if the service is responding
    echo "Checking if API service is responding..."
    docker exec fogis-api-client-dev curl -v http://localhost:8080/ || echo "Initial curl check failed, but continuing..."

    while ! docker ps | grep -q "fogis-api-client-dev.*healthy"; do
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

        if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
            echo "Timeout waiting for API service to become healthy after $TIMEOUT seconds."
            echo "Checking container logs for errors:"
            docker logs fogis-api-client-dev
            echo "Container status:"
            docker ps | grep fogis-api-client-dev
            echo "Trying to access the API directly:"
            docker exec fogis-api-client-dev curl -v http://localhost:8080/ || echo "Curl check failed"

            # Try to restart the container
            echo "Attempting to restart the container..."
            docker restart fogis-api-client-dev
            sleep 10

            # Check if it's healthy now
            if docker ps | grep -q "fogis-api-client-dev.*healthy"; then
                echo "Container is now healthy after restart!"
                break
            else
                echo "Container is still unhealthy after restart. Continuing anyway..."
                break
            fi
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
