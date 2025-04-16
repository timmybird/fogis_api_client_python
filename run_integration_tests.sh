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

    # Simple wait for the service to start
    echo "Waiting for API service to start..."
    sleep 15  # Give the container time to start

    # Check if the container is running
    if docker ps | grep -q fogis-api-client-dev; then
        echo "Container is running. Checking if API is responding..."

        # Try to access the API
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ || echo "failed")

        if [ "$RESPONSE" = "200" ]; then
            echo "API is responding with 200 OK. Proceeding with tests."
        else
            echo "API returned status $RESPONSE. Waiting a bit longer..."
            sleep 15  # Wait a bit longer

            # Try one more time
            RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ || echo "failed")
            if [ "$RESPONSE" = "200" ]; then
                echo "API is now responding with 200 OK. Proceeding with tests."
            else
                echo "API still returned status $RESPONSE. Proceeding with tests anyway."
                # Show container logs for debugging
                echo "Container logs:"
                docker logs fogis-api-client-dev --tail 20
            fi
        fi
    else
        echo "Container is not running! Starting it..."
        docker compose -f docker-compose.dev.yml up -d fogis-api-client
        sleep 15  # Wait for container to start
    fi

    # Final check to confirm API is responding
    echo "Final API check before proceeding:"
    curl -v http://localhost:8080/
    echo ""

    # Get debug information to help diagnose health check issues
    echo "Getting debug information:"
    curl -s http://localhost:8080/debug | jq . || echo "Debug endpoint failed"
fi

# Run the integration tests
echo "Running integration tests..."
docker compose -f docker-compose.dev.yml run --rm integration-tests

# Show test results
echo "Integration tests completed."
