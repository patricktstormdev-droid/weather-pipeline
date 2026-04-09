import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from datetime import datetime, timedelta, timezone
import requests
import pandas as pd
from sqlalchemy import create_engine, text

def task_failure_alert(context):
    """Send alert on task failure"""
    task_instance = context['task_instance']
    dag_run = context['dag_run']
    exception = context.get('exception')
    
    print(f"✗ Task failed: {task_instance.task_id}")
    print(f"DAG: {dag_run.dag_id}")
    print(f"Exception: {exception}")
    # In production, integrate with Slack/email here
    # Example: send_slack_message(f"Weather pipeline failed: {task_instance.task_id}")

default_args = {
    'owner': 'patrick',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': task_failure_alert,
    'email': [os.getenv('AIRFLOW_ALERT_EMAIL', 'patrick@example.com')],
    'email_on_failure': True,
    'email_on_retry': False,
}

def run_ingest():
    import sys
    sys.path.insert(0, '/opt/airflow/ingestion')
    from fetch_weather import fetch_weather, load_to_postgres
    from airflow.providers.postgres.hooks.postgres import PostgresHook

    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_connection('postgres_default')
    engine = create_engine(
        f"postgresql+psycopg2://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
    )

    for city, lat, lon in [
        ("Detroit", 42.3314, -83.0458),
        ("Chicago", 41.8781, -87.6298),
    ]:
        df = fetch_weather(city=city, lat=lat, lon=lon, days_back=1)
        load_to_postgres(df, engine)

with DAG(
    dag_id='weather_ingest',
    default_args=default_args,
    description='Daily weather ingest from Open-Meteo API',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['weather', 'ingest'],
) as dag:

    ingest_task = PythonOperator(
        task_id='fetch_and_load_weather',
        python_callable=run_ingest,
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt/weather && dbt run --target docker --profiles-dir /opt/airflow/dbt/weather',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dbt/weather && dbt test --target docker --profiles-dir /opt/airflow/dbt/weather',
    )

    spark_task = BashOperator(
        task_id='spark_analysis',
        bash_command='python /opt/airflow/spark/trend_analysis.py',
    )

    sync_to_render = BashOperator(
        task_id='sync_to_render',
        bash_command="""
            # Get source database connection details from environment or Airflow connection
            SOURCE_CONN='postgresql://airflow:airflow@postgres/airflow'
            
            # Dump only weather-related tables and restore to Render
            pg_dump -h postgres -U airflow -d airflow -t weather_raw -t weather_trends -t weather_spark_features | \
            psql ${RENDER_DATABASE_URL}
        """,
        env={'RENDER_DATABASE_URL': os.environ.get('RENDER_DATABASE_URL', '')},
    )

    ingest_task >> dbt_run >> dbt_test >> spark_task >> sync_to_render