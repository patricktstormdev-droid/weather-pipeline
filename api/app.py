from flask import Flask, jsonify, request
from flask_cors import CORS
from psycopg2 import pool
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
        traces_sample_rate=0.1,  # Sample 10% of transactions for performance monitoring
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

def query(sql):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(r) for r in rows]

@app.errorhandler(500)
def handle_500(e):
    """Handle internal server errors and log to Sentry"""
    if sentry_dsn:
        sentry_sdk.capture_exception(e)
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all exceptions"""
    if sentry_dsn:
        sentry_sdk.capture_exception(e)
    return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    """Health check endpoint for monitoring"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
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

connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)

def query(sql, params=None):
    conn = connection_pool.getconn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()
        return [dict(r) for r in rows]
    finally:
        connection_pool.putconn(conn)

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
    return jsonify(query(f"SELECT ... FROM weather_trends {where} ORDER BY date ASC", params))

@app.route("/api/anomalies")
def anomalies():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    where_clause = "WHERE is_anomaly = true"
    if start_date:
        where_clause += f" AND date >= '{start_date}'"
    if end_date:
        where_clause += f" AND date <= '{end_date}'"
    
    return jsonify(query(f"""
        SELECT
            date::text,
            city,
            temp_avg_f,
            rolling_30day_avg_temp_f,
            temp_stddev_30day,
            is_anomaly
        FROM weather_spark_features
        {where_clause}
        ORDER BY date DESC
    """))

@app.route("/api/spark-features")
def spark_features():
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    where_clause = "WHERE 1=1"
    if start_date:
        where_clause += f" AND date >= '{start_date}'"
    if end_date:
        where_clause += f" AND date <= '{end_date}'"
    
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
        {where_clause}
        ORDER BY date ASC
    """))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)