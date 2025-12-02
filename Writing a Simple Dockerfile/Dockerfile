# Use official Python runtime as base image
FROM python:3.11-slim

# Set metadata for the image
LABEL maintainer="student@alnafi.com"
LABEL description="Enhanced Python web application with environment variables"
LABEL version="2.0"

# Set environment variables
ENV APP_NAME="Dockerized Python Web App"
ENV APP_VERSION="2.0.0"
ENV ENVIRONMENT="production"
ENV DEBUG="false"
ENV PORT="8080"
ENV PYTHONUNBUFFERED="1"

# Set working directory inside the container
WORKDIR /usr/src/app

# Copy requirements file first (for better layer caching)
COPY app/requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Make the Python script executable
RUN chmod +x app.py

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /usr/src/app
USER appuser

# Expose the port the app runs on
EXPOSE $PORT

# Add health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Define the command to run the application
CMD ["python", "app.py"]
