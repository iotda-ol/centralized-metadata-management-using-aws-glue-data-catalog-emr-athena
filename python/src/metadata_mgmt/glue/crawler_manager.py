"""
Crawler Manager
Manages AWS Glue Crawlers for automatic schema discovery
"""

import boto3
import time
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

from metadata_mgmt.utils.logging_config import get_logger
from metadata_mgmt.utils.exceptions import CatalogException
from metadata_mgmt.utils.retry import retry

logger = get_logger(__name__)


class CrawlerManager:
    """Manages AWS Glue Crawler operations"""

    def __init__(self, region_name: Optional[str] = None, client: Optional[Any] = None):
        """
        Initialize Crawler Manager

        Args:
            region_name: AWS region name
            client: Optional boto3 Glue client (for testing)
        """
        self.client = client or boto3.client('glue', region_name=region_name)
        logger.info("CrawlerManager initialized")

    @retry(max_attempts=3)
    def create_crawler(
        self,
        name: str,
        role: str,
        database: str,
        s3_targets: List[str],
        schedule: Optional[str] = None,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create Glue crawler

        Args:
            name: Crawler name
            role: IAM role ARN
            database: Target database name
            s3_targets: List of S3 paths to crawl
            schedule: Cron expression for schedule
            description: Crawler description

        Returns:
            Response from create_crawler API

        Raises:
            CatalogException: If crawler creation fails
        """
        try:
            targets = {
                'S3Targets': [{'Path': path} for path in s3_targets]
            }

            crawler_config = {
                'Name': name,
                'Role': role,
                'DatabaseName': database,
                'Targets': targets,
                'SchemaChangePolicy': {
                    'UpdateBehavior': 'UPDATE_IN_DATABASE',
                    'DeleteBehavior': 'LOG'
                }
            }

            if description:
                crawler_config['Description'] = description

            if schedule:
                crawler_config['Schedule'] = schedule

            response = self.client.create_crawler(**crawler_config)
            logger.info(f"Created crawler: {name}")
            return response

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AlreadyExistsException':
                logger.warning(f"Crawler {name} already exists")
                return {'ResponseMetadata': {'HTTPStatusCode': 200}}
            else:
                logger.error(f"Failed to create crawler {name}: {e}")
                raise CatalogException(f"Failed to create crawler: {e}")

    @retry(max_attempts=3)
    def start_crawler(self, name: str) -> Dict[str, Any]:
        """
        Start crawler

        Args:
            name: Crawler name

        Returns:
            Response from start_crawler API

        Raises:
            CatalogException: If starting crawler fails
        """
        try:
            response = self.client.start_crawler(Name=name)
            logger.info(f"Started crawler: {name}")
            return response

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CrawlerRunningException':
                logger.warning(f"Crawler {name} is already running")
                return {'ResponseMetadata': {'HTTPStatusCode': 200}}
            else:
                logger.error(f"Failed to start crawler {name}: {e}")
                raise CatalogException(f"Failed to start crawler: {e}")

    @retry(max_attempts=3)
    def stop_crawler(self, name: str) -> Dict[str, Any]:
        """
        Stop crawler

        Args:
            name: Crawler name

        Returns:
            Response from stop_crawler API

        Raises:
            CatalogException: If stopping crawler fails
        """
        try:
            response = self.client.stop_crawler(Name=name)
            logger.info(f"Stopped crawler: {name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to stop crawler {name}: {e}")
            raise CatalogException(f"Failed to stop crawler: {e}")

    @retry(max_attempts=3)
    def get_crawler_status(self, name: str) -> str:
        """
        Get crawler status

        Args:
            name: Crawler name

        Returns:
            Crawler state (READY, RUNNING, STOPPING)

        Raises:
            CatalogException: If getting status fails
        """
        try:
            response = self.client.get_crawler(Name=name)
            state = response['Crawler']['State']
            logger.info(f"Crawler {name} state: {state}")
            return state

        except ClientError as e:
            logger.error(f"Failed to get crawler status: {e}")
            raise CatalogException(f"Failed to get crawler status: {e}")

    def wait_for_crawler(
        self,
        name: str,
        max_wait_seconds: int = 3600,
        poll_interval: int = 10
    ) -> str:
        """
        Wait for crawler to complete

        Args:
            name: Crawler name
            max_wait_seconds: Maximum wait time
            poll_interval: Seconds between status checks

        Returns:
            Final crawler state

        Raises:
            CatalogException: If crawler fails or times out
        """
        elapsed = 0
        while elapsed < max_wait_seconds:
            state = self.get_crawler_status(name)

            if state == 'READY':
                logger.info(f"Crawler {name} completed")
                return state
            elif state == 'STOPPING':
                logger.info(f"Crawler {name} is stopping")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise CatalogException(f"Crawler {name} timed out after {max_wait_seconds}s")

    @retry(max_attempts=3)
    def delete_crawler(self, name: str) -> Dict[str, Any]:
        """
        Delete crawler

        Args:
            name: Crawler name

        Returns:
            Response from delete_crawler API

        Raises:
            CatalogException: If deletion fails
        """
        try:
            response = self.client.delete_crawler(Name=name)
            logger.info(f"Deleted crawler: {name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to delete crawler {name}: {e}")
            raise CatalogException(f"Failed to delete crawler: {e}")
