"""
PySpark ETL Job Example
Demonstrates data processing using PySpark with Glue Data Catalog integration
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, count, sum as _sum, avg, max as _max
from datetime import datetime
import sys

# Initialize Spark with Glue Catalog integration
spark = SparkSession.builder \
    .appName("ETL Job - Process Events") \
    .config("spark.sql.catalogImplementation", "hive") \
    .config("hive.metastore.client.factory.class",
            "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory") \
    .enableHiveSupport() \
    .getOrCreate()

# Configuration
INPUT_DATABASE = "raw_data"
INPUT_TABLE = "events"
OUTPUT_DATABASE = "processed_data"
OUTPUT_TABLE = "daily_user_summary"
OUTPUT_LOCATION = "s3://your-bucket/processed/daily_user_summary/"


def read_source_data():
    """Read raw events from Glue table"""
    print(f"Reading from {INPUT_DATABASE}.{INPUT_TABLE}")
    
    df = spark.table(f"{INPUT_DATABASE}.{INPUT_TABLE}")
    
    print(f"Loaded {df.count()} records")
    df.printSchema()
    
    return df


def transform_data(df):
    """Transform raw events into daily user summary"""
    print("Transforming data...")
    
    # Parse timestamp and extract date
    df_with_date = df.withColumn(
        "event_date",
        to_date(col("timestamp"))
    )
    
    # Aggregate by user and date
    summary = df_with_date.groupBy("user_id", "event_date").agg(
        count("*").alias("event_count"),
        count(col("event_type")).alias("distinct_event_types"),
        _max("timestamp").alias("last_event_time")
    )
    
    print(f"Generated {summary.count()} summary records")
    summary.show(10)
    
    return summary


def write_output(df):
    """Write processed data to Glue table"""
    print(f"Writing to {OUTPUT_DATABASE}.{OUTPUT_TABLE}")
    
    # Write as Parquet, partitioned by date
    df.write \
        .mode("overwrite") \
        .format("parquet") \
        .option("compression", "snappy") \
        .partitionBy("event_date") \
        .option("path", OUTPUT_LOCATION) \
        .saveAsTable(f"{OUTPUT_DATABASE}.{OUTPUT_TABLE}")
    
    print("Data written successfully")


def validate_output():
    """Validate the output data"""
    print("Validating output...")
    
    result = spark.sql(f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT user_id) as unique_users,
            MIN(event_date) as min_date,
            MAX(event_date) as max_date
        FROM {OUTPUT_DATABASE}.{OUTPUT_TABLE}
    """)
    
    result.show()
    
    stats = result.collect()[0]
    
    assert stats.total_records > 0, "No records in output table"
    assert stats.unique_users > 0, "No unique users in output"
    
    print("Validation passed!")


def main():
    """Main ETL execution"""
    try:
        print(f"Starting ETL job at {datetime.now()}")
        
        # Read source data
        raw_df = read_source_data()
        
        # Transform
        processed_df = transform_data(raw_df)
        
        # Write output
        write_output(processed_df)
        
        # Validate
        validate_output()
        
        print(f"ETL job completed successfully at {datetime.now()}")
        
    except Exception as e:
        print(f"ETL job failed: {str(e)}")
        sys.exit(1)
    
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
