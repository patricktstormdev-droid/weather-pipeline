import requests
import pandas as pd
from sqlalchemy import text
from datetime import datetime, timedelta, timezone

def fetch_weather(city: str, lat: float, lon: float, days_back: int = 90):
    end_date = (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days_back + 5)).strftime("%Y-%m-%d")

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
    df["ingested_at"] = datetime.now(timezone.utc)
    df["date"] = pd.to_datetime(df["date"])

    return df

def load_to_postgres(df: pd.DataFrame, engine):
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
                PRIMARY KEY (date, city)
            )
        """))

    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO weather_raw
                    (date, city, temp_max_f, temp_min_f, precipitation_mm,
                     windspeed_max_mph, humidity_max_pct, ingested_at)
                VALUES
                    (:date, :city, :temp_max_f, :temp_min_f, :precipitation_mm,
                     :windspeed_max_mph, :humidity_max_pct, :ingested_at)
                ON CONFLICT (date, city) DO UPDATE SET
                    temp_max_f = EXCLUDED.temp_max_f,
                    temp_min_f = EXCLUDED.temp_min_f,
                    precipitation_mm = EXCLUDED.precipitation_mm,
                    windspeed_max_mph = EXCLUDED.windspeed_max_mph,
                    humidity_max_pct = EXCLUDED.humidity_max_pct,
                    ingested_at = EXCLUDED.ingested_at
            """), {
                "date": row["date"].date() if hasattr(row["date"], "date") else row["date"],
                "city": row["city"],
                "temp_max_f": float(row["temp_max_f"]) if row["temp_max_f"] else None,
                "temp_min_f": float(row["temp_min_f"]) if row["temp_min_f"] else None,
                "precipitation_mm": float(row["precipitation_mm"]) if row["precipitation_mm"] else None,
                "windspeed_max_mph": float(row["windspeed_max_mph"]) if row["windspeed_max_mph"] else None,
                "humidity_max_pct": float(row["humidity_max_pct"]) if row["humidity_max_pct"] else None,
                "ingested_at": row["ingested_at"]
            })

    print(f"Loaded {len(df)} records into weather_raw table.")

if __name__ == "__main__":
    from sqlalchemy import create_engine
    engine = create_engine(
        "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
    )
    df = fetch_weather(
        city="Detroit",
        lat=42.3314,
        lon=-83.0458,
        days_back=90
    )
    print(df.head())
    load_to_postgres(df, engine)