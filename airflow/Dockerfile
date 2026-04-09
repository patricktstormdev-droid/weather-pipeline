FROM apache/airflow:2.8.1-python3.11

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy DAGs (they'll be mounted as volume in docker-compose, but needed here for standalone)
COPY dags/ /opt/airflow/dags/
COPY ingestion/ /opt/airflow/ingestion/
COPY dbt/ /opt/airflow/dbt/
COPY spark/ /opt/airflow/spark/

# Set Airflow home
ENV AIRFLOW_HOME=/opt/airflow

# Run migrations and create admin user on startup
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["airflow", "webserver"]
