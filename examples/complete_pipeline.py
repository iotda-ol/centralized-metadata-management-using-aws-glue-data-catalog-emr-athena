"""
Example: Create a complete data pipeline
This script demonstrates creating databases, tables, running crawlers, and querying data
"""

import sys
import time
from metadata_mgmt.glue.catalog_manager import CatalogManager
from metadata_mgmt.athena.query_runner import QueryRunner
from metadata_mgmt.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_databases(catalog: CatalogManager):
    """Create Glue databases"""
    logger.info("Creating databases...")
    
    databases = [
        ('raw_data', 'Raw ingested data'),
        ('processed_data', 'Cleaned and processed data'),
        ('analytics', 'Analytics-ready data')
    ]
    
    for name, description in databases:
        catalog.create_database(name, description)
        logger.info(f"Created database: {name}")


def create_tables(catalog: CatalogManager, data_lake_bucket: str):
    """Create Glue tables"""
    logger.info("Creating tables...")
    
    # Events table schema
    events_schema = [
        {'Name': 'event_id', 'Type': 'string'},
        {'Name': 'user_id', 'Type': 'string'},
        {'Name': 'event_type', 'Type': 'string'},
        {'Name': 'timestamp', 'Type': 'timestamp'},
        {'Name': 'properties', 'Type': 'string'}
    ]
    
    # Partition keys
    partition_keys = [
        {'Name': 'year', 'Type': 'string'},
        {'Name': 'month', 'Type': 'string'},
        {'Name': 'day', 'Type': 'string'}
    ]
    
    # Create events table
    catalog.create_table(
        database='raw_data',
        table='events',
        schema=events_schema,
        location=f's3://{data_lake_bucket}/raw/events/',
        format='parquet',
        partition_keys=partition_keys
    )
    logger.info("Created events table")
    
    # Users table schema
    users_schema = [
        {'Name': 'user_id', 'Type': 'string'},
        {'Name': 'username', 'Type': 'string'},
        {'Name': 'email', 'Type': 'string'},
        {'Name': 'created_at', 'Type': 'timestamp'}
    ]
    
    # Create users table
    catalog.create_table(
        database='raw_data',
        table='users',
        schema=users_schema,
        location=f's3://{data_lake_bucket}/raw/users/',
        format='parquet'
    )
    logger.info("Created users table")


def run_sample_queries(runner: QueryRunner):
    """Run sample Athena queries"""
    logger.info("Running sample queries...")
    
    # Query 1: Count events
    query1 = """
    SELECT COUNT(*) as event_count
    FROM raw_data.events
    WHERE year='2024' AND month='01'
    """
    
    logger.info("Executing query: Count events")
    results1 = runner.execute_query(query1, database='raw_data')
    logger.info(f"Result: {results1}")
    
    # Query 2: User activity summary
    query2 = """
    SELECT 
        user_id,
        event_type,
        COUNT(*) as event_count
    FROM raw_data.events
    WHERE year='2024' AND month='01'
    GROUP BY user_id, event_type
    ORDER BY event_count DESC
    LIMIT 10
    """
    
    logger.info("Executing query: User activity summary")
    results2 = runner.execute_query(query2, database='raw_data')
    for row in results2:
        logger.info(f"User: {row['user_id']}, Type: {row['event_type']}, Count: {row['event_count']}")


def main():
    """Main execution"""
    # Configuration
    data_lake_bucket = 'your-data-lake-bucket'  # Update with your bucket name
    
    # Initialize managers
    catalog = CatalogManager()
    runner = QueryRunner(workgroup='primary')
    
    try:
        # Step 1: Create databases
        create_databases(catalog)
        
        # Step 2: Create tables
        create_tables(catalog, data_lake_bucket)
        
        # Step 3: Wait for metadata to propagate
        logger.info("Waiting for metadata to propagate...")
        time.sleep(5)
        
        # Step 4: Run queries (if data exists)
        logger.info("Ready to query data. Upload data to S3 and run queries.")
        # Uncomment when you have data:
        # run_sample_queries(runner)
        
        logger.info("Pipeline setup complete!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
