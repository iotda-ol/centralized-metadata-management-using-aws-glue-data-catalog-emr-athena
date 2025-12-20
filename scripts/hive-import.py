#!/usr/bin/env python3
"""
Hive Metastore to AWS Glue Data Catalog Import Script

This script migrates table metadata from an existing Apache Hive metastore
to AWS Glue Data Catalog, enabling centralized metadata management.

Prerequisites:
- AWS CLI configured with appropriate credentials
- PyHive or direct JDBC access to Hive metastore
- boto3 library installed
"""

import boto3
import sys
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HiveToGlueImporter:
    """Imports Hive metastore tables to AWS Glue Data Catalog"""
    
    def __init__(self, region_name: str, glue_database: str):
        """
        Initialize the importer
        
        Args:
            region_name: AWS region name
            glue_database: Target Glue database name
        """
        self.glue_client = boto3.client('glue', region_name=region_name)
        self.glue_database = glue_database
        
    def create_glue_database_if_not_exists(self):
        """Create the Glue database if it doesn't exist"""
        try:
            self.glue_client.get_database(Name=self.glue_database)
            logger.info(f"Database {self.glue_database} already exists")
        except self.glue_client.exceptions.EntityNotFoundException:
            self.glue_client.create_database(
                DatabaseInput={
                    'Name': self.glue_database,
                    'Description': 'Imported from Hive metastore'
                }
            )
            logger.info(f"Created database {self.glue_database}")
    
    def import_table(self, table_metadata: Dict[str, Any]) -> str:
        """
        Import a single table to Glue Data Catalog
        
        Args:
            table_metadata: Dictionary containing table metadata from Hive
            
        Returns:
            'success', 'skipped', or 'failed' status string
        """
        try:
            table_input = {
                'Name': table_metadata['name'],
                'StorageDescriptor': table_metadata['storage_descriptor'],
                'PartitionKeys': table_metadata.get('partition_keys', []),
                'TableType': table_metadata.get('table_type', 'EXTERNAL_TABLE'),
                'Parameters': table_metadata.get('parameters', {})
            }
            
            # Add optional fields if present
            if 'description' in table_metadata:
                table_input['Description'] = table_metadata['description']
            if 'owner' in table_metadata:
                table_input['Owner'] = table_metadata['owner']
            
            self.glue_client.create_table(
                DatabaseName=self.glue_database,
                TableInput=table_input
            )
            
            logger.info(f"Successfully imported table: {table_metadata['name']}")
            return 'success'
            
        except self.glue_client.exceptions.AlreadyExistsException:
            logger.warning(f"Table {table_metadata['name']} already exists, skipping")
            return 'skipped'
        except Exception as e:
            logger.error(f"Error importing table {table_metadata['name']}: {str(e)}")
            return 'failed'
    
    def import_tables_from_hive_metadata(self, hive_tables: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Import multiple tables from Hive metadata
        
        Args:
            hive_tables: List of table metadata dictionaries
            
        Returns:
            Dictionary with import statistics
        """
        stats = {'successful': 0, 'failed': 0, 'skipped': 0}
        
        self.create_glue_database_if_not_exists()
        
        for table in hive_tables:
            result = self.import_table(table)
            if result == 'success':
                stats['successful'] += 1
            elif result == 'skipped':
                stats['skipped'] += 1
            else:  # failed
                stats['failed'] += 1
        
        logger.info(f"Import complete. Stats: {stats}")
        return stats


def example_hive_table_format() -> Dict[str, Any]:
    """
    Returns an example of the expected Hive table metadata format
    
    This format should be extracted from your Hive metastore using
    DESCRIBE FORMATTED commands or direct metastore database queries.
    """
    return {
        'name': 'example_table',
        'description': 'Example table imported from Hive',
        'table_type': 'EXTERNAL_TABLE',
        'owner': 'hadoop',
        'storage_descriptor': {
            'Columns': [
                {
                    'Name': 'id',
                    'Type': 'bigint',
                    'Comment': 'Unique identifier'
                },
                {
                    'Name': 'name',
                    'Type': 'string',
                    'Comment': 'Name field'
                },
                {
                    'Name': 'timestamp',
                    'Type': 'timestamp',
                    'Comment': 'Event timestamp'
                }
            ],
            'Location': 's3://your-bucket/data/example_table/',
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                'Parameters': {
                    'field.delim': ',',
                    'serialization.format': ','
                }
            },
            'Compressed': False,
            'StoredAsSubDirectories': False
        },
        'partition_keys': [
            {
                'Name': 'year',
                'Type': 'string',
                'Comment': 'Partition by year'
            },
            {
                'Name': 'month',
                'Type': 'string',
                'Comment': 'Partition by month'
            }
        ],
        'parameters': {
            'EXTERNAL': 'TRUE',
            'transient_lastDdlTime': '1234567890'
        }
    }


def main():
    """Main execution function"""
    # Configuration
    AWS_REGION = 'us-east-1'
    GLUE_DATABASE = 'centralized_metadata_db'
    
    # Initialize importer
    importer = HiveToGlueImporter(
        region_name=AWS_REGION,
        glue_database=GLUE_DATABASE
    )
    
    # Example: Import tables
    # In production, you would extract this from your Hive metastore
    example_tables = [example_hive_table_format()]
    
    # Perform import
    stats = importer.import_tables_from_hive_metadata(example_tables)
    
    logger.info("Import process completed")
    logger.info(f"Results: {stats}")
    
    return 0 if stats['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
