from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/opt/airflow/ingestion')

from fetch_weather import fetch_weather, load_to_postgres

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
    from sqlalchemy import create_engine

    hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = hook.get_connection('postgres_default')
    engine = create_engine(
        f"postgresql+psycopg2://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
    )

    df = fetch_weather(
        city="Detroit",
        lat=42.3314,
        lon=-83.0458,
        days_back=1
    )
    load_to_postgres(df, engine)

with DAG(
    dag_id='weather_ingest',
    default_args=default_args,
    description='Daily weather ingest from Open_Meteo API',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['weather', 'ingest'],
) as dag:

    ingest_task = PythonOperator(
        task_id='fetch_and_load_weather',
        python_callable=run_ingest
    )