#!/bin/bash

# Create necessary directories if they don't exist
mkdir -p data logs test-results

# Check if .env.dev exists, create it if it doesn't
if [ ! -f .env.dev ]; then
    echo "Creating .env.dev file..."
    echo "# Development environment variables" > .env.dev
    echo "FOGIS_USERNAME=dev_username" >> .env.dev
    echo "FOGIS_PASSWORD=dev_password" >> .env.dev
    echo "FLASK_ENV=development" >> .env.dev
    echo "FLASK_DEBUG=1" >> .env.dev
fi

# Start the development environment
echo "Starting development environment..."
docker compose -f docker-compose.dev.yml up --build -d

# Show logs
echo "Showing logs (Ctrl+C to exit)..."
docker compose -f docker-compose.dev.yml logs -f
