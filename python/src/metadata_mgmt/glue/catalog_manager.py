"""
Glue Catalog Manager
Manages AWS Glue Data Catalog operations including databases, tables, and partitions
"""

import boto3
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

from metadata_mgmt.utils.logging_config import get_logger
from metadata_mgmt.utils.exceptions import CatalogException
from metadata_mgmt.utils.retry import retry

logger = get_logger(__name__)


class CatalogManager:
    """Manages AWS Glue Data Catalog operations"""

    def __init__(self, region_name: Optional[str] = None, client: Optional[Any] = None):
        """
        Initialize Catalog Manager

        Args:
            region_name: AWS region name
            client: Optional boto3 Glue client (for testing)
        """
        self.client = client or boto3.client('glue', region_name=region_name)
        logger.info("CatalogManager initialized")

    @retry(max_attempts=3)
    def create_database(
        self,
        name: str,
        description: str = "",
        location: Optional[str] = None,
        parameters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Glue database

        Args:
            name: Database name
            description: Database description
            location: Database location URI
            parameters: Additional parameters

        Returns:
            Response from create_database API call

        Raises:
            CatalogException: If database creation fails
        """
        try:
            database_input = {
                'Name': name,
                'Description': description
            }

            if location:
                database_input['LocationUri'] = location

            if parameters:
                database_input['Parameters'] = parameters

            response = self.client.create_database(DatabaseInput=database_input)
            logger.info(f"Created database: {name}")
            return response

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AlreadyExistsException':
                logger.warning(f"Database {name} already exists")
                return {'ResponseMetadata': {'HTTPStatusCode': 200}}
            else:
                logger.error(f"Failed to create database {name}: {e}")
                raise CatalogException(f"Failed to create database: {e}")

    @retry(max_attempts=3)
    def create_table(
        self,
        database: str,
        table: str,
        schema: List[Dict[str, str]],
        location: str,
        format: str = 'parquet',
        partition_keys: Optional[List[Dict[str, str]]] = None,
        parameters: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Glue table

        Args:
            database: Database name
            table: Table name
            schema: List of column definitions [{'Name': 'col1', 'Type': 'string'}]
            location: S3 location of data
            format: Data format (parquet, orc, json, csv)
            partition_keys: Optional partition key definitions
            parameters: Additional table parameters

        Returns:
            Response from create_table API call

        Raises:
            CatalogException: If table creation fails
        """
        try:
            storage_descriptor = {
                'Columns': schema,
                'Location': location,
                'InputFormat': self._get_input_format(format),
                'OutputFormat': self._get_output_format(format),
                'SerdeInfo': {
                    'SerializationLibrary': self._get_serde_lib(format)
                }
            }

            table_input = {
                'Name': table,
                'StorageDescriptor': storage_descriptor,
            }

            if partition_keys:
                table_input['PartitionKeys'] = partition_keys

            if parameters:
                table_input['Parameters'] = parameters

            response = self.client.create_table(
                DatabaseName=database,
                TableInput=table_input
            )
            logger.info(f"Created table: {database}.{table}")
            return response

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AlreadyExistsException':
                logger.warning(f"Table {database}.{table} already exists")
                return {'ResponseMetadata': {'HTTPStatusCode': 200}}
            else:
                logger.error(f"Failed to create table {database}.{table}: {e}")
                raise CatalogException(f"Failed to create table: {e}")

    @retry(max_attempts=3)
    def get_table(self, database: str, table: str) -> Dict[str, Any]:
        """
        Get table metadata

        Args:
            database: Database name
            table: Table name

        Returns:
            Table metadata

        Raises:
            CatalogException: If table not found
        """
        try:
            response = self.client.get_table(DatabaseName=database, Name=table)
            logger.info(f"Retrieved table: {database}.{table}")
            return response['Table']

        except ClientError as e:
            logger.error(f"Failed to get table {database}.{table}: {e}")
            raise CatalogException(f"Table not found: {database}.{table}")

    def _get_input_format(self, format: str) -> str:
        """Get InputFormat for data format"""
        formats = {
            'parquet': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'orc': 'org.apache.hadoop.hive.ql.io.orc.OrcInputFormat',
            'json': 'org.apache.hadoop.mapred.TextInputFormat',
            'csv': 'org.apache.hadoop.mapred.TextInputFormat'
        }
        return formats.get(format.lower(), formats['parquet'])

    def _get_output_format(self, format: str) -> str:
        """Get OutputFormat for data format"""
        formats = {
            'parquet': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
            'orc': 'org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat',
            'json': 'org.apache.hadoop.hive.IgnoreKeyTextOutputFormat',
            'csv': 'org.apache.hadoop.hive.IgnoreKeyTextOutputFormat'
        }
        return formats.get(format.lower(), formats['parquet'])

    def _get_serde_lib(self, format: str) -> str:
        """Get SerDe library for data format"""
        formats = {
            'parquet': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
            'orc': 'org.apache.hadoop.hive.ql.io.orc.OrcSerde',
            'json': 'org.openx.data.jsonserde.JsonSerDe',
            'csv': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
        }
        return formats.get(format.lower(), formats['parquet'])
