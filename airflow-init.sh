#!/bin/bash
set -e

# Initialize Airflow database
airflow db migrate

# Create default admin user (will skip if already exists)
airflow users create \
    --username admin \
    --password "${AIRFLOW_ADMIN_PASSWORD:-airflow}" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com 2>/dev/null || true

echo "Airflow initialized successfully"
exec "$@"
