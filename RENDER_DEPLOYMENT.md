# Render Deployment Guide

## Deployed Services

You should have these on Render already:
1. **weather-pipeline-db** — PostgreSQL database
2. **weather-pipeline-api** — Flask API (points to database)

## Deploying Airflow to Render (NEW STEP)

Follow these steps to deploy the Airflow scheduler + webserver:

### 1. Create a New Web Service on Render

Go to [Render Dashboard](https://dashboard.render.com):
- Click **New +** → **Web Service**
- Connect your GitHub `weather-pipeline` repo
- Select `main` branch

### 2. Configure the Service

- **Name:** `weather-pipeline-airflow`
- **Root Directory:** (leave blank - root of repo)
- **Dockerfile:** `airflow-prod.Dockerfile`
- **Region:** Same as your database (Ohio)
- **Plan:** Standard ($7/month) — Free tier won't work for Airflow

### 3. Add Environment Variables

Click **Environment** and add:

```
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql://USER:PASSWORD@your-render-db-host/airflow
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=false
AIRFLOW__CORE__FERNET_KEY=<generate below>
AIRFLOW_ADMIN_PASSWORD=<strong_password>
RENDER_DATABASE_URL=postgresql://USER:PASSWORD@your-render-db-host/weather_pipeline_db
PYTHONUNBUFFERED=1
```

**Where to get these values:**

- `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN` — Same as your database connection string in `.env`
- `RENDER_DATABASE_URL` — Your weather database URL (same as API uses)
- `AIRFLOW__CORE__FERNET_KEY` — Generate in a terminal:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

### 4. Configure Health Check

- **HTTP GET Path:** `/health`
- **Port:** `8080`
- **Initial Delay:** 60 seconds
- **Timeout:** 10 seconds

### 5. Deploy

Click **Create Web Service** — Render will build and deploy automatically.

### 6. Access Airflow UI

Once deployed (green checkmark), visit:
```
https://weather-pipeline-airflow-xxx.onrender.com
```

Login with:
- Username: `admin`
- Password: (the one you set in `AIRFLOW_ADMIN_PASSWORD`)

### 7. Enable the DAG

1. In Airflow UI, find `weather_ingest`
2. Toggle the **off** switch to **on** (enables scheduling)
3. It will run daily at midnight UTC
4. Or click the play icon to trigger manually

## What Happens

**Airflow will run daily:**
1. **fetch_and_load_weather** — Fetch data from Open-Meteo API
2. **dbt_run** — Transform data with dbt
3. **dbt_test** — Test data quality
4. **spark_analysis** — Detect anomalies
5. **sync_to_render** — Replicate weather tables to Render database

Your Vercel frontend will pull from the Render database via the API.

---

## Troubleshooting

**"Slow build or killed build"**
- Upgrade to Standard tier ($7/month)
- Free tier (512MB) is too small for Airflow

**"psql: command not found"**
- Already fixed in Dockerfile

**"RENDER_DATABASE_URL not set"**
- Make sure it's in Environment variables on Render, not just locally

**"Can't connect to postgres"**
- Make sure the database connection string is correct
- Test: `psql <connection_string>` from local terminal

---

## Cost Estimate

- Render Airflow service: ~$7/month (Standard tier minimum)
- Database: included with existing setup
- API: included with existing setup
- Vercel frontend: free tier included

**Total: ~$7/month for 24/7 automated pipeline**
