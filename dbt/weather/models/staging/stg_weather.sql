with source as (
    select * from {{ source('public', 'weather_raw') }}
),

cleaned as (
    select
        date,
        city,
        round(cast(temp_max_f as numeric), 1) as temp_max_f,
        round(cast(temp_min_f as numeric), 1) as temp_min_f,
        round(cast((temp_max_f + temp_min_f) / 2 as numeric), 1) as temp_avg_f,
        round(cast(precipitation_mm as numeric), 2) as precipitation_mm,
        round(cast(windspeed_max_mph as numeric), 1) as windspeed_max_mph,
        round(cast(humidity_max_pct as numeric), 1) as humidity_max_pct,
        ingested_at
    from source
    where date is not null
        and temp_max_f is not null
        and temp_min_f is not null
)

select * from cleaned