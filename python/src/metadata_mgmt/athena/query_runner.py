"""
Athena Query Runner
Executes and manages Athena SQL queries
"""

import boto3
import time
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

from metadata_mgmt.utils.logging_config import get_logger
from metadata_mgmt.utils.exceptions import AthenaException
from metadata_mgmt.utils.retry import retry

logger = get_logger(__name__)


class QueryRunner:
    """Manages Athena query execution"""

    def __init__(
        self,
        workgroup: str = 'primary',
        region_name: Optional[str] = None,
        client: Optional[Any] = None
    ):
        """
        Initialize Query Runner

        Args:
            workgroup: Athena workgroup name
            region_name: AWS region name
            client: Optional boto3 Athena client (for testing)
        """
        self.client = client or boto3.client('athena', region_name=region_name)
        self.workgroup = workgroup
        logger.info(f"QueryRunner initialized with workgroup: {workgroup}")

    @retry(max_attempts=3)
    def execute_query(
        self,
        query: str,
        database: Optional[str] = None,
        output_location: Optional[str] = None,
        wait: bool = True,
        max_wait_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Execute Athena SQL query

        Args:
            query: SQL query string
            database: Database name
            output_location: S3 output location
            wait: Wait for query completion
            max_wait_seconds: Maximum wait time in seconds

        Returns:
            Query results or execution metadata

        Raises:
            AthenaException: If query execution fails
        """
        try:
            # Start query execution
            execution_params = {
                'QueryString': query,
                'WorkGroup': self.workgroup
            }

            if database:
                execution_params['QueryExecutionContext'] = {'Database': database}

            if output_location:
                execution_params['ResultConfiguration'] = {'OutputLocation': output_location}

            response = self.client.start_query_execution(**execution_params)
            query_id = response['QueryExecutionId']
            logger.info(f"Started query execution: {query_id}")

            if wait:
                self.wait_for_query(query_id, max_wait_seconds)
                return self.get_query_results(query_id)
            else:
                return {'QueryExecutionId': query_id}

        except ClientError as e:
            logger.error(f"Failed to execute query: {e}")
            raise AthenaException(f"Query execution failed: {e}")

    @retry(max_attempts=3)
    def wait_for_query(
        self,
        query_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 2
    ) -> str:
        """
        Wait for query to complete

        Args:
            query_id: Query execution ID
            max_wait_seconds: Maximum wait time
            poll_interval: Seconds between status checks

        Returns:
            Final query state

        Raises:
            AthenaException: If query fails or times out
        """
        elapsed = 0
        while elapsed < max_wait_seconds:
            response = self.client.get_query_execution(QueryExecutionId=query_id)
            state = response['QueryExecution']['Status']['State']

            if state == 'SUCCEEDED':
                logger.info(f"Query {query_id} succeeded")
                return state
            elif state in ['FAILED', 'CANCELLED']:
                reason = response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                logger.error(f"Query {query_id} failed: {reason}")
                raise AthenaException(f"Query failed: {reason}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise AthenaException(f"Query {query_id} timed out after {max_wait_seconds}s")

    @retry(max_attempts=3)
    def get_query_results(
        self,
        query_id: str,
        max_results: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get query results

        Args:
            query_id: Query execution ID
            max_results: Maximum number of results to return

        Returns:
            List of result rows as dictionaries

        Raises:
            AthenaException: If fetching results fails
        """
        try:
            results = []
            paginator = self.client.get_paginator('get_query_results')

            for page in paginator.paginate(
                QueryExecutionId=query_id,
                PaginationConfig={'MaxItems': max_results}
            ):
                # Get column names from first page
                if not results:
                    column_info = page['ResultSet']['ResultSetMetadata']['ColumnInfo']
                    columns = [col['Name'] for col in column_info]

                    # Skip header row
                    rows = page['ResultSet']['Rows'][1:]
                else:
                    rows = page['ResultSet']['Rows']

                # Convert rows to dictionaries
                for row in rows:
                    values = [field.get('VarCharValue', '') for field in row['Data']]
                    results.append(dict(zip(columns, values)))

            logger.info(f"Retrieved {len(results)} results for query {query_id}")
            return results

        except ClientError as e:
            logger.error(f"Failed to get query results: {e}")
            raise AthenaException(f"Failed to get results: {e}")
