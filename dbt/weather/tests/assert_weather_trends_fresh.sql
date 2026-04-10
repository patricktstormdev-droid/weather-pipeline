-- Test: Data freshness - weather_trends should have data from last 90 days (reasonable for trend analysis)
{{ config(
    pre_hook="SET SEARCH_PATH TO {{ target.schema }}"
) }}

SELECT MAX(date)::date as latest_date
FROM {{ ref('weather_trends') }}
HAVING MAX(date) < CURRENT_DATE - INTERVAL '90 days'
