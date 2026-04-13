from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg2 import pool as pg_pool
import threading
import psycopg2
import psycopg2.extras
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Initialize Sentry for error tracking
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "production")
    )

app = Flask(__name__)
CORS(app, origins=[
    "https://weather-pipeline.vercel.app",
    "https://weather-pipeline.vercel.app/dashboard.app",
    "http://localhost:5173",
    "http://localhost:3000"
])

DATABASE_URL = os.getenv("DATABASE_URL")

# --- Connection pool (lazy init — no DB connection at import time) ---

_pool = None
_pool_lock = threading.Lock()

def get_pool():
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = pg_pool.SimpleConnectionPool(1, 10, DATABASE_URL)
    return _pool

def query(sql, params=None):
    conn = get_pool().getconn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        return [dict(r) for r in rows]
    finally:
        get_pool().putconn(conn)

# --- Error handlers ---

@app.errorhandler(500)
def handle_500(e):
    if sentry_dsn:
        sentry_sdk.capture_exception(e)
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    if sentry_dsn:
        sentry_sdk.capture_exception(e)
    return jsonify({"error": str(e)}), 500

# --- Routes ---

@app.route("/health")
def health():
    try:
        conn = get_pool().getconn()
        get_pool().putconn(conn)
        return jsonify({"status": "healthy", "database": "ok"}), 200
    except Exception as e:
        if sentry_dsn:
            sentry_sdk.capture_exception(e)
        return jsonify({"status": "unhealthy", "database": "error", "error": str(e)}), 503

@app.route("/")
def root():
    return jsonify({"status": "ok"})

@app.route("/api/summary")
def summary():
    return jsonify(query("""
        SELECT
            COUNT(*)::int                                        AS total_days,
            MIN(date)::text                                      AS date_start,
            MAX(date)::text                                      AS date_end,
            ROUND(AVG(temp_avg_f)::numeric, 1)                  AS avg_temp_f,
            ROUND(MAX(temp_max_f)::numeric, 1)                  AS max_temp_f,
            (SELECT date::text FROM weather_spark_features WHERE temp_max_f = (SELECT MAX(temp_max_f) FROM weather_spark_features) LIMIT 1) AS date_max_temp,
            ROUND(MIN(temp_min_f)::numeric, 1)                  AS min_temp_f,
            (SELECT date::text FROM weather_spark_features WHERE temp_min_f = (SELECT MIN(temp_min_f) FROM weather_spark_features) LIMIT 1) AS date_min_temp,
            ROUND(SUM(precipitation_mm)::numeric, 1)            AS total_precipitation_mm,
            COUNT(*) FILTER (WHERE is_anomaly = true)::int      AS anomaly_days
        FROM weather_spark_features
    """))

@app.route("/api/trends")
def trends():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    conditions = []
    params = []
    if start_date:
        conditions.append("date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("date <= %s")
        params.append(end_date)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return jsonify(query(f"""
        SELECT
            date::text,
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
        {where}
        ORDER BY date ASC
    """, params or None))

@app.route("/api/anomalies")
def anomalies():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    conditions = ["is_anomaly = true"]
    params = []
    if start_date:
        conditions.append("date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("date <= %s")
        params.append(end_date)

    where = "WHERE " + " AND ".join(conditions)
    return jsonify(query(f"""
        SELECT
            date::text,
            city,
            temp_avg_f,
            rolling_30day_avg_temp_f,
            temp_stddev_30day,
            is_anomaly
        FROM weather_spark_features
        {where}
        ORDER BY date DESC
    """, params or None))

@app.route("/api/spark-features")
def spark_features():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    conditions = []
    params = []
    if start_date:
        conditions.append("date >= %s")
        params.append(start_date)
    if end_date:
        conditions.append("date <= %s")
        params.append(end_date)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return jsonify(query(f"""
        SELECT
            date::text,
            city,
            temp_avg_f,
            rolling_7day_avg_temp_f,
            rolling_30day_avg_temp_f,
            temp_stddev_30day,
            is_anomaly
        FROM weather_spark_features
        {where}
        ORDER BY date ASC
    """, params or None))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)