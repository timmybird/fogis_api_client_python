# Use a slim Python base image
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

COPY . .

# Install fogis_api_client in editable mode
# Assuming setup.py is in the volume-mounted directory
RUN pip install --no-cache-dir -e .

# Copy the FOGIS API Gateway script and Swagger documentation
COPY fogis_api_gateway.py .
COPY fogis_api_swagger.py .

# Install additional dependencies for the API Gateway
RUN pip install --no-cache-dir flask-swagger-ui apispec marshmallow

# Install test dependencies
RUN pip install --no-cache-dir pytest pytest-flask docker

# Define environment variables (Username and Password) - placeholders (you can keep or remove these, they are set in docker run anyway)
# ENV FOGIS_USERNAME=your_fogis_username_placeholder
# ENV FOGIS_PASSWORD=your_fogis_password_placeholder

# Command to run when the container starts - the FOGIS API Gateway
CMD ["python", "fogis_api_gateway.py"]