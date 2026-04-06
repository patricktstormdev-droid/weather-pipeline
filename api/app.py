from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
CORS(app, origins=["https://weather-pipeline.vercel.app", "http://localhost:5173"])

DATABASE_URL = os.getenv("DATABASE_URL")

def query(sql):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

@app.route("/")

def root():
    return jsonify({"status": "ok"})

@app.route("/api/summary")
def summary():
    return jsonify(query("""
        SELECT
            COUNT(*)::int                                        AS total_days,
            ROUND(AVG(temp_avg_f)::numeric, 1)                  AS avg_temp_f,
            ROUND(MAX(temp_max_f)::numeric, 1)                  AS max_temp_f,
            ROUND(MIN(temp_min_f)::numeric, 1)                  AS min_temp_f,
            ROUND(SUM(precipitation_mm)::numeric, 1)            AS total_precipitation_mm,
            COUNT(*) FILTER (WHERE is_anomaly = true)::int      AS anomaly_days
        FROM weather_spark_features
    """))

@app.route("/api/trends")
def trends():
    return jsonify(query("""
        SELECT
            date,
            city,
            temp_max_f,
            temp_min_f,
            temp_avg_f,
            precipitation_mm,
            windspeed_max_mph,
            humidity_max_pct,
            rolling_7day_avg_temp_f,
            rolling_7day_avg_precip_mm,
            rolling_30day_min_temp_f,
            rolling_30day_max_temp_f
        FROM weather_trends
        ORDER BY date ASC
    """))

@app.route("/api/anomalies")
def anomalies():
    return jsonify(query("""
        SELECT
            date,
            city,
            temp_avg_f,
            rolling_30day_avg_temp_f,
            temp_stddev_30day,
            is_anomaly
        FROM weather_spark_features
        WHERE is_anomaly = true
        ORDER BY date DESC
    """))

@app.route("/api/spark-features")
def spark_features():
    return jsonify(query("""
        SELECT
            date,
            city,
            temp_avg_f,
            rolling_7day_avg_temp_f,
            rolling_30day_avg_temp_f,
            temp_stddev_30day,
            is_anomaly
        FROM weather_spark_features
        ORDER BY date ASC
    """))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)