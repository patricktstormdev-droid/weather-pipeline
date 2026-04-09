-- Test: No NULL values in key columns
{{ config(
    pre_hook="SET SEARCH_PATH TO {{ target.schema }}"
) }}

SELECT *
FROM {{ ref('weather_trends') }}
WHERE date IS NULL
   OR city IS NULL
   OR temp_avg_f IS NULL
