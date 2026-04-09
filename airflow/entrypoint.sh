#!/bin/bash
set -e

# Initialize Airflow database
airflow db migrate

# Create admin user if it doesn't exist
airflow users create \
    --username admin \
    --password "${AIRFLOW_ADMIN_PASSWORD:-airflow}" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    2>/dev/null || true  # Suppress error if user already exists

# Execute the passed command
exec "$@"
