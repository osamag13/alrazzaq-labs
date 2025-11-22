This lab demonstrates how to manage service dependencies in containerized applications using Podman, Podman-Compose, health checks, retry logic, and inter-container connectivity.

The environment simulates a multi-service setup with:

PostgreSQL (db) – backend database

Nginx (web) – frontend web server

Python app (app) – application that waits for DB and tests connectivity

All containers communicate through a shared network and use health checks or retry logic to ensure reliable startup order.

📁 Project Structure
container-dependencies-lab/
│
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── healthcheck.sh
└── app.py

1. Objective

How to enforce container startup order using depends_on
How to use built-in health checks for service readiness
How to write custom health-check scripts
How to implement retry logic inside entrypoint scripts
How to test connectivity between dependent services
How to deploy multi-container apps using Podman Compose

2. Requirements

Ensure required tools are installed:

podman --version
podman-compose --version
Your Podman version should be 4.x+ and Podman Compose 1.0.6+.

3. How to Run the Lab
Step 1 — Clone or initialize the directory
mkdir container-dependencies-lab
cd container-dependencies-lab

Step 2 — Ensure all files are present
Copy the prepared files into the directory:
docker-compose.yml
Dockerfile
entrypoint.sh
healthcheck.sh
app.py

Step 3 — Make scripts executable
chmod +x entrypoint.sh healthcheck.sh

Step 4 — Build and start the environment
podman-compose up --build -d

Step 5 — View container logs
podman-compose logs -f

4. File Descriptions
docker-compose.yml
Defines the three services (db, web, app), with proper image names for Podman, health checks, and dependency rules.
entrypoint.sh
Adds retry logic to wait until PostgreSQL is reachable before launching the Python app.
healthcheck.sh
Simple script to test DB port availability. Used for service health checking.
app.py
Small Python script that attempts to connect to PostgreSQL using credentials from environment variables.

5. Verifying Health Checks
Check the DB container’s health status:
podman inspect --format='{{.State.Health.Status}}' container-dependencies-lab_db_1

6. Troubleshooting
Container not starting?
podman-compose logs
Health check failing?
Increase retries or interval:
healthcheck:
  interval: 10s
  retries: 10
App failing to connect?
Ensure environment variables match:
POSTGRES_PASSWORD: example

7. Cleanup
To remove containers, networks, and volumes:
podman-compose down
podman system prune -f
