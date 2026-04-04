from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

## Python script to perform trend analaysis on weather data using Spark ##
## Reads raw weather data from PostgreSQL, computes rolling averages and detects anomalies ##

DB_URL = "jdbc:postgresql://postgres:5432/airflow"
DB_PROPS = {
    "user": "airflow",
    "password": "airflow",
    "driver": "org.postgresql.Driver"
}

def create_spark_session():
    return SparkSession.builder \
        .appName("WeatherTrendAnalysis") \
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3") \
        .getOrCreate()

def read_from_postgres(spark):
    return spark.read.jdbc(
        url=DB_URL,
        table="weather_raw",
        properties=DB_PROPS
    )

def compute_trends(df):
    # First, calculate the average temperature
    df = df.withColumn(
        "temp_avg_f",
        F.round((F.col("temp_max_f") + F.col("temp_min_f")) / 2, 1)
    )

    window_7day = Window.partitionBy("city").orderBy("date").rowsBetween(-6, 0)
    window_30day = Window.partitionBy("city").orderBy("date").rowsBetween(-29, 0)

    return df.withColumn(
        "rolling_7day_avg_temp_f",
        F.round(F.avg("temp_avg_f").over(window_7day), 2)
    ).withColumn(
        "rolling_30day_avg_temp_f",
        F.round(F.avg("temp_avg_f").over(window_30day), 2)
    ).withColumn(
        "temp_stddev_30day",
        F.round(F.stddev("temp_avg_f").over(window_30day), 2)
    ).withColumn(
        "is_anomaly",
        F.when(
            F.abs(F.col("temp_avg_f") - F.col("rolling_30day_avg_temp_f"))
            > (2 * F.col("temp_stddev_30day")), True
        ).otherwise(False)
    )

def write_to_postgres(df):
    df.write.jdbc(
        url=DB_URL,
        table="weather_spark_features",
        mode="overwrite",
        properties=DB_PROPS
    )
    print("Successfully wrote weather_spark_features table")

if __name__ == "__main__":
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("Reading from PostgreSQL...")
    df = read_from_postgres(spark)

    print("Computing trends and anomalies...")
    df_trends = compute_trends(df)

    print("Writing results to PostgreSQL...")
    write_to_postgres(df_trends)

    anomalies = df_trends.filter(F.col("is_anomaly") == True)
    print(f"\nAnomaly days detected: {anomalies.count()}")
    anomalies.select("date", "city", "temp_avg_f", "rolling_30day_avg_temp_f").show(10)

    spark.stop()