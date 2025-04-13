# Docker Guide for FOGIS API Client

This guide explains how to use Docker with the FOGIS API Client, including setup, configuration, and troubleshooting.

## Quick Start

### Production Deployment

1. Create a `.env` file with your credentials:
   ```
   FOGIS_USERNAME=your_fogis_username
   FOGIS_PASSWORD=your_fogis_password
   ```

2. Start the service:
   ```bash
   docker compose up -d
   ```

3. Access the API at http://localhost:8080

### Development Environment

1. Start the development environment:
   ```bash
   docker compose -f docker-compose.override.yml up -d
   ```

2. Access the API at http://localhost:8080

## Docker Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FOGIS_USERNAME` | Your FOGIS username | `demo_user` | Yes (for production) |
| `FOGIS_PASSWORD` | Your FOGIS password | `demo_pass` | Yes (for production) |
| `FLASK_DEBUG` | Enable Flask debug mode | `0` | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` | No |
| `TZ` | Timezone | `Europe/Stockholm` | No |
| `USE_EXTERNAL_NETWORK` | Whether to use an external Docker network | `false` | No |
| `NETWORK_DRIVER` | Docker network driver | `bridge` | No |

### Volumes

The Docker configuration uses the following volumes:

- `./data:/app/data` - Persistent data storage
- `./logs:/app/logs` - Log files

### Ports

- `8080` - HTTP API port

### Health Checks

The Docker container includes a health check that verifies the API is responding correctly. The health check:

- Calls the `/health` endpoint and checks for a 200 status code
- Runs every 30 seconds
- Has a 10-second timeout
- Retries 3 times before marking the container as unhealthy
- Waits 60 seconds on startup before beginning health checks

For development (in docker-compose.override.yml), a more lenient health check is used:
- Calls the root endpoint (`/`) instead of `/health`
- Runs more frequently (every 15 seconds)
- Has more retries (5 times)
- Starts checking sooner (after 30 seconds)

## Docker Compose Files

### docker-compose.yml

The main Docker Compose file for production use. It includes:

- Basic service configuration
- Health checks
- Resource limits
- Logging configuration

### docker-compose.override.yml

Development overrides that are automatically applied when running `docker compose up`. It includes:

- Volume mounts for live code reloading
- Debug mode enabled
- Flask auto-reloading

## Building Custom Images

To build a custom Docker image:

```bash
docker build -t fogis-api-client:custom .
```

## Troubleshooting

### Common Issues

#### Container fails health check

If the container is marked as unhealthy:

1. Check the logs:
   ```bash
   docker logs fogis-api-client-service
   ```

2. Verify your credentials in the `.env` file

3. Try accessing the health endpoint directly:
   ```bash
   curl http://localhost:8080/health
   ```

#### Network issues

If you're having network issues:

1. Check if the network exists:
   ```bash
   docker network ls | grep fogis-network
   ```

2. If it doesn't exist, create it:
   ```bash
   docker network create fogis-network
   ```

3. Set `USE_EXTERNAL_NETWORK=false` in your environment to let Docker Compose create the network automatically

#### Permission issues with volumes

If you're having permission issues with the volumes:

1. Check the ownership of the directories:
   ```bash
   ls -la data logs
   ```

2. Create the directories with the correct permissions:
   ```bash
   mkdir -p data logs
   chmod 755 data logs
   ```

## Advanced Configuration

### Custom Network Configuration

To use a custom network configuration:

```bash
USE_EXTERNAL_NETWORK=true NETWORK_DRIVER=overlay docker compose up -d
```

### Resource Limits

The default resource limits are:

- CPU: 0.5 cores
- Memory: 512MB

To change these limits, modify the `deploy` section in `docker-compose.yml`.

### Logging Configuration

The default logging configuration uses JSON file logging with rotation. To change this, modify the `logging` section in `docker-compose.yml`.

## CI/CD Integration

The Docker configuration is designed to work well with CI/CD pipelines. The key considerations are:

1. Use the `USE_EXTERNAL_NETWORK=false` environment variable in CI environments
2. Set credentials using environment variables or a `.env` file
3. Use the health check to verify the service is running correctly

Example GitHub Actions workflow:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start service
        run: |
          echo "FOGIS_USERNAME=${{ secrets.FOGIS_USERNAME }}" > .env
          echo "FOGIS_PASSWORD=${{ secrets.FOGIS_PASSWORD }}" >> .env
          echo "USE_EXTERNAL_NETWORK=false" >> .env
          docker compose up -d

      - name: Wait for service to be healthy
        run: |
          timeout 60s bash -c 'until docker ps | grep fogis-api-client-service | grep -q "(healthy)"; do sleep 1; done'

      - name: Run tests
        run: |
          # Run your tests here
```

## Best Practices

1. Always use a `.env` file or environment variables for credentials
2. Don't hardcode sensitive information in Dockerfiles or Docker Compose files
3. Use the health check to verify the service is running correctly
4. Use resource limits to prevent container resource exhaustion
5. Use logging configuration to prevent disk space issues
6. Use the development environment for local development
7. Use the production environment for deployment
