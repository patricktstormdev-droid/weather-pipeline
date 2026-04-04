{{ config(
    materialized='incremental',
    unique_key=['date', 'city']
) }}

with base as (
    select * from {{ ref('stg_weather') }}
    
    {% if is_incremental() %}
        where date > (select max(date) from {{ this }})
    {% endif %}
),

weekly as (
    select
        date,
        city,
        temp_max_f,
        temp_min_f,
        temp_avg_f,
        precipitation_mm,
        windspeed_max_mph,
        humidity_max_pct,
        avg(temp_avg_f) over (
            order by date
            rows between 6 preceding and current row
        ) as rolling_7day_avg_temp_f,
        avg(precipitation_mm) over (
            order by date
            rows between 6 preceding and current row
        ) as rolling_7day_avg_precip_mm,
        min(temp_min_f) over (
            order by date
            rows between 29 preceding and current row
        ) as rolling_30day_min_temp_f,
        max(temp_max_f) over (
            order by date
            rows between 29 preceding and current row
        ) as rolling_30day_max_temp_f
    from base
)

select * from weekly
order by date desc