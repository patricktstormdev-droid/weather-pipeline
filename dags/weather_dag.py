from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta, timezone
import requests
import pandas as pd
from sqlalchemy import create_engine, text

default_args = {
    'owner': 'patrick',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
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

    ingest_task >> dbt_run >> dbt_test >> spark_task