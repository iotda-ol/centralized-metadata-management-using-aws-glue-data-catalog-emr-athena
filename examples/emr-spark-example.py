#!/usr/bin/env python3
"""
EMR Spark Example using AWS Glue Data Catalog

This example demonstrates how to use Spark on EMR with AWS Glue Data Catalog
as the metadata store. The script shows common operations like reading from
catalog tables, performing transformations, and writing back to the catalog.

Prerequisites:
- EMR cluster with Spark configured to use Glue Data Catalog
- Appropriate IAM permissions for Glue and S3 access
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count, year, month

def create_spark_session():
    """
    Create Spark session configured for Glue Data Catalog
    
    Note: When running on EMR with proper configuration, Glue Data Catalog
    is automatically used as the Hive metastore.
    """
    spark = SparkSession.builder \
        .appName("GlueCatalogExample") \
        .enableHiveSupport() \
        .getOrCreate()
    
    return spark


def example_read_from_catalog(spark, database_name, table_name):
    """
    Read data from a table in Glue Data Catalog
    
    Args:
        spark: SparkSession
        database_name: Name of the Glue database
        table_name: Name of the table in the catalog
    """
    # Method 1: Using Spark SQL
    df = spark.sql(f"SELECT * FROM {database_name}.{table_name}")
    
    # Method 2: Using table() function
    # df = spark.table(f"{database_name}.{table_name}")
    
    print(f"Read {df.count()} rows from {database_name}.{table_name}")
    df.show(10)
    
    return df


def example_write_to_catalog(spark, df, database_name, table_name, mode="overwrite"):
    """
    Write DataFrame to Glue Data Catalog as a new table
    
    Args:
        spark: SparkSession
        df: DataFrame to write
        database_name: Target Glue database
        table_name: Target table name
        mode: Write mode (overwrite, append, etc.)
    """
    # Write to catalog
    df.write \
        .mode(mode) \
        .format("parquet") \
        .saveAsTable(f"{database_name}.{table_name}")
    
    print(f"Successfully wrote data to {database_name}.{table_name}")


def example_partitioned_write(spark, df, database_name, table_name, partition_cols):
    """
    Write DataFrame to catalog with partitions
    
    Args:
        spark: SparkSession
        df: DataFrame to write
        database_name: Target Glue database
        table_name: Target table name
        partition_cols: List of column names to partition by
    """
    df.write \
        .mode("overwrite") \
        .format("parquet") \
        .partitionBy(*partition_cols) \
        .saveAsTable(f"{database_name}.{table_name}")
    
    print(f"Successfully wrote partitioned data to {database_name}.{table_name}")
    print(f"Partition columns: {partition_cols}")


def example_query_with_partition_filter(spark, database_name, table_name):
    """
    Query table with partition filter for optimized reads
    
    Args:
        spark: SparkSession
        database_name: Glue database name
        table_name: Table name
    """
    # Query with partition filter (much faster than full scan)
    df = spark.sql(f"""
        SELECT *
        FROM {database_name}.{table_name}
        WHERE year = '2024' AND month = '01'
    """)
    
    print("Query with partition filter executed")
    df.show(10)
    
    return df


def example_aggregation(spark, database_name, table_name):
    """
    Perform aggregations on catalog table
    
    Args:
        spark: SparkSession
        database_name: Glue database name
        table_name: Table name
    """
    df = spark.table(f"{database_name}.{table_name}")
    
    # Perform aggregations
    agg_df = df.groupBy("category") \
        .agg(
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount"),
            count("*").alias("count")
        )
    
    print("Aggregation results:")
    agg_df.show()
    
    return agg_df


def example_join_tables(spark, database_name, table1, table2):
    """
    Join two tables from Glue Data Catalog
    
    Args:
        spark: SparkSession
        database_name: Glue database name
        table1: First table name
        table2: Second table name
    """
    df1 = spark.table(f"{database_name}.{table1}")
    df2 = spark.table(f"{database_name}.{table2}")
    
    # Perform join
    joined_df = df1.join(df2, df1.id == df2.customer_id, "inner")
    
    print(f"Joined {table1} and {table2}")
    joined_df.show(10)
    
    return joined_df


def example_create_view(spark, database_name, view_name, sql_query):
    """
    Create a view in Glue Data Catalog
    
    Args:
        spark: SparkSession
        database_name: Glue database name
        view_name: View name to create
        sql_query: SQL query for the view
    """
    spark.sql(f"USE {database_name}")
    spark.sql(f"CREATE OR REPLACE VIEW {view_name} AS {sql_query}")
    
    print(f"Created view: {database_name}.{view_name}")


def example_update_table_properties(spark, database_name, table_name):
    """
    Update table properties in Glue Data Catalog
    
    Args:
        spark: SparkSession
        database_name: Glue database name
        table_name: Table name
    """
    spark.sql(f"""
        ALTER TABLE {database_name}.{table_name}
        SET TBLPROPERTIES (
            'description' = 'Updated by Spark job',
            'last_modified' = current_timestamp()
        )
    """)
    
    print(f"Updated properties for {database_name}.{table_name}")


def example_show_catalog_info(spark, database_name):
    """
    Display information about databases and tables in Glue Data Catalog
    
    Args:
        spark: SparkSession
        database_name: Glue database name
    """
    # Show all databases
    spark.sql("SHOW DATABASES").show()
    
    # Show tables in database
    spark.sql(f"SHOW TABLES IN {database_name}").show()
    
    # Show table details
    spark.sql(f"DESCRIBE EXTENDED {database_name}.sales").show(truncate=False)


def main():
    """Main execution function"""
    # Configuration
    DATABASE_NAME = "centralized_metadata_db"
    SOURCE_TABLE = "sales"
    TARGET_TABLE = "sales_summary"
    
    # Create Spark session
    print("Creating Spark session...")
    spark = create_spark_session()
    
    print(f"Using Glue Data Catalog database: {DATABASE_NAME}")
    
    # Example 1: Show catalog information
    print("\n=== Example 1: Show Catalog Info ===")
    example_show_catalog_info(spark, DATABASE_NAME)
    
    # Example 2: Read from catalog
    print("\n=== Example 2: Read from Catalog ===")
    df = example_read_from_catalog(spark, DATABASE_NAME, SOURCE_TABLE)
    
    # Example 3: Query with partition filter
    print("\n=== Example 3: Partition Filter Query ===")
    filtered_df = example_query_with_partition_filter(
        spark, DATABASE_NAME, SOURCE_TABLE
    )
    
    # Example 4: Perform aggregations
    print("\n=== Example 4: Aggregations ===")
    agg_df = example_aggregation(spark, DATABASE_NAME, SOURCE_TABLE)
    
    # Example 5: Write aggregated results back to catalog
    print("\n=== Example 5: Write to Catalog ===")
    example_write_to_catalog(
        spark, agg_df, DATABASE_NAME, TARGET_TABLE, mode="overwrite"
    )
    
    # Example 6: Create a view
    print("\n=== Example 6: Create View ===")
    example_create_view(
        spark,
        DATABASE_NAME,
        "high_value_sales",
        f"SELECT * FROM {DATABASE_NAME}.{SOURCE_TABLE} WHERE amount > 1000"
    )
    
    print("\n=== All examples completed successfully! ===")
    
    # Stop Spark session
    spark.stop()


if __name__ == "__main__":
    main()
