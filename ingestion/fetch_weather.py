import requests
import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta
from airflow.providers.postgres.hooks.postgres import PostgresHook


def fetch_weather(city: str, lat: float, lon: float, days_back: int = 90):
    end_date = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "relative_humidity_2m_max"
        ],
        "temperature_unit": "fahrenheit",
        "timezone": "America/Detroit"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["daily"])
    df.rename(columns={
        "time": "date",
        "temperature_2m_max": "temp_max_f",
        "temperature_2m_min": "temp_min_f",
        "precipitation_sum": "precipitation_mm",
        "windspeed_10m_max": "windspeed_max_mph",
        "relative_humidity_2m_max": "humidity_max_pct"
    }, inplace=True)

    df["city"] = city
    df["ingested_at"] = datetime.now()
    df["date"] = pd.to_datetime(df["date"])

    return df

def load_to_postgres(df: pd.DataFrame):
    hook = PostgresHook(postgres_conn_id='postgres_default')
    engine = hook.get_sqlalchemy_engine()

    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_raw (
                date DATE,
                city VARCHAR(50),
                temp_max_f FLOAT,
                temp_min_f FLOAT,
                precipitation_mm FLOAT,
                windspeed_max_mph FLOAT,
                humidity_max_pct FLOAT,
                ingested_at TIMESTAMP,
                PRIMARY KEY (date, city, ingested_at)
            )
        """))

    df.to_sql(
        "weather_raw",
        con=engine,
        if_exists="append",
        index=False,
        method="multi"
    )
    print(f"Loaded {len(df)} records into weather_raw table.")

if __name__ == "__main__":
    df = fetch_weather(
        city="Detroit",
        lat=42.3314,
        lon=-83.0458,
        days_back=90
    )
    print(df.head())
    load_to_postgres(df)