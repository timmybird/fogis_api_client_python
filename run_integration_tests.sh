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
    TIMEOUT=120  # 2 minutes timeout
    START_TIME=$(date +%s)
    HEALTHY_START_TIME=""  # Initialize variable to track how long container has been healthy

    # Try to manually check if the service is responding
    echo "Checking if API service is responding..."
    echo "Docker container status:"
    docker ps
    echo "Docker container logs:"
    docker logs fogis-api-client-dev
    echo "Trying to access API from host:"
    curl -v http://localhost:8080/ || echo "Initial curl check failed, but continuing..."

    # Check container status every 5 seconds
    while true; do
        # Check if container is healthy
        if docker ps | grep -q "fogis-api-client-dev.*healthy"; then
            echo "Container is healthy! Checking if API is responding..."

            # Check if API is responding correctly - first try /health endpoint
            API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
            if [ "$API_RESPONSE" = "200" ]; then
                echo "API health endpoint is responding correctly! Proceeding with tests."
                break
            else
                # If /health doesn't respond with 200, try the root endpoint
                ROOT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
                if [ "$ROOT_RESPONSE" = "200" ]; then
                    echo "API root endpoint is responding correctly! Proceeding with tests."
                    break
                else
                    echo "Container is healthy but API returned status $API_RESPONSE for /health and $ROOT_RESPONSE for /. Waiting for API to be fully ready..."

                    # Track how long the container has been healthy but API not responding
                    if [ -z "$HEALTHY_START_TIME" ]; then
                        HEALTHY_START_TIME=$(date +%s)
                    else
                        HEALTHY_ELAPSED=$(($(date +%s) - HEALTHY_START_TIME))
                        if [ $HEALTHY_ELAPSED -gt 30 ]; then
                            echo "Container has been healthy for over 30 seconds. Proceeding with tests despite API status codes."
                            break
                        fi
                    fi
                fi
            fi
        else
            # Reset the healthy start time if container becomes unhealthy
            HEALTHY_START_TIME=""
        fi
        CURRENT_TIME=$(date +%s)
        ELAPSED_TIME=$((CURRENT_TIME - START_TIME))

        # Check container status in more detail
        echo "Current container status:"
        docker ps | grep fogis-api-client-dev || echo "Container not found!"

        # Try to access the API directly
        echo "Trying to access the API directly:"
        curl -v http://localhost:8080/ || echo "Curl check failed"

        # Check if the container is running but unhealthy
        if docker ps | grep -q "fogis-api-client-dev.*unhealthy"; then
            echo "Container is unhealthy. Checking logs:"
            docker logs fogis-api-client-dev --tail 20
        fi

        if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
            echo "Timeout waiting for API service to become healthy after $TIMEOUT seconds."
            echo "Checking container logs for errors:"
            docker logs fogis-api-client-dev
            echo "Container status:"
            docker ps | grep fogis-api-client-dev || echo "Container not found!"

            # Try to restart the container
            echo "Attempting to restart the container..."
            docker restart fogis-api-client-dev || echo "Failed to restart container"
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

    # Final check to confirm API is responding
    echo "Final API check before proceeding:"
    curl -v http://localhost:8080/
    echo ""
fi

# Run the integration tests
echo "Running integration tests..."
docker compose -f docker-compose.dev.yml run --rm integration-tests

# Show test results
echo "Integration tests completed."
