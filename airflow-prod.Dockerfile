FROM apache/airflow:2.8.1-python3.11

USER root
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Airflow metadata
ENV AIRFLOW_HOME=/opt/airflow

# Init script
COPY airflow-init.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["airflow", "webserver"]
