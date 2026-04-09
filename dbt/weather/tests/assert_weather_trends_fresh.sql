-- Test: Data freshness - weather_trends should have data from last 3 days
{{ config(
    pre_hook="SET SEARCH_PATH TO {{ target.schema }}"
) }}

SELECT *
FROM {{ ref('weather_trends') }}
GROUP BY 1
HAVING MAX(date) < CURRENT_DATE - INTERVAL '3 days'
