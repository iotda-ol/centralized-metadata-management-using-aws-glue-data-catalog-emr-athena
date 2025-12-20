"""
S3 Utilities
Helper functions for S3 operations
"""

import boto3
from typing import List, Dict, Optional, Any
from botocore.exceptions import ClientError

from metadata_mgmt.utils.logging_config import get_logger
from metadata_mgmt.utils.exceptions import MetadataManagementException
from metadata_mgmt.utils.retry import retry

logger = get_logger(__name__)


class S3Utils:
    """Utility class for S3 operations"""

    def __init__(self, region_name: Optional[str] = None, client: Optional[Any] = None):
        """
        Initialize S3 Utils

        Args:
            region_name: AWS region name
            client: Optional boto3 S3 client (for testing)
        """
        self.client = client or boto3.client('s3', region_name=region_name)
        logger.info("S3Utils initialized")

    @retry(max_attempts=3)
    def upload_file(
        self,
        file_path: str,
        bucket: str,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload file to S3

        Args:
            file_path: Local file path
            bucket: S3 bucket name
            key: S3 object key
            metadata: Optional object metadata

        Returns:
            Response from upload_file API

        Raises:
            MetadataManagementException: If upload fails
        """
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata

            response = self.client.upload_file(file_path, bucket, key, ExtraArgs=extra_args)
            logger.info(f"Uploaded file to s3://{bucket}/{key}")
            return response

        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise MetadataManagementException(f"Failed to upload file: {e}")

    @retry(max_attempts=3)
    def download_file(self, bucket: str, key: str, file_path: str) -> None:
        """
        Download file from S3

        Args:
            bucket: S3 bucket name
            key: S3 object key
            file_path: Local file path to save

        Raises:
            MetadataManagementException: If download fails
        """
        try:
            self.client.download_file(bucket, key, file_path)
            logger.info(f"Downloaded s3://{bucket}/{key} to {file_path}")

        except ClientError as e:
            logger.error(f"Failed to download file: {e}")
            raise MetadataManagementException(f"Failed to download file: {e}")

    @retry(max_attempts=3)
    def list_objects(
        self,
        bucket: str,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List objects in S3 bucket

        Args:
            bucket: S3 bucket name
            prefix: Object key prefix filter
            max_keys: Maximum number of keys to return

        Returns:
            List of object metadata

        Raises:
            MetadataManagementException: If listing fails
        """
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            objects = []

            for page in paginator.paginate(
                Bucket=bucket,
                Prefix=prefix,
                PaginationConfig={'MaxItems': max_keys}
            ):
                if 'Contents' in page:
                    objects.extend(page['Contents'])

            logger.info(f"Listed {len(objects)} objects in s3://{bucket}/{prefix}")
            return objects

        except ClientError as e:
            logger.error(f"Failed to list objects: {e}")
            raise MetadataManagementException(f"Failed to list objects: {e}")

    @retry(max_attempts=3)
    def delete_objects(self, bucket: str, keys: List[str]) -> Dict[str, Any]:
        """
        Delete multiple objects from S3

        Args:
            bucket: S3 bucket name
            keys: List of object keys to delete

        Returns:
            Response from delete_objects API

        Raises:
            MetadataManagementException: If deletion fails
        """
        try:
            objects_to_delete = [{'Key': key} for key in keys]
            response = self.client.delete_objects(
                Bucket=bucket,
                Delete={'Objects': objects_to_delete}
            )
            logger.info(f"Deleted {len(keys)} objects from s3://{bucket}")
            return response

        except ClientError as e:
            logger.error(f"Failed to delete objects: {e}")
            raise MetadataManagementException(f"Failed to delete objects: {e}")

    @retry(max_attempts=3)
    def get_object_metadata(self, bucket: str, key: str) -> Dict[str, Any]:
        """
        Get object metadata

        Args:
            bucket: S3 bucket name
            key: S3 object key

        Returns:
            Object metadata

        Raises:
            MetadataManagementException: If operation fails
        """
        try:
            response = self.client.head_object(Bucket=bucket, Key=key)
            logger.info(f"Retrieved metadata for s3://{bucket}/{key}")
            return response

        except ClientError as e:
            logger.error(f"Failed to get object metadata: {e}")
            raise MetadataManagementException(f"Failed to get metadata: {e}")

    @retry(max_attempts=3)
    def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str
    ) -> Dict[str, Any]:
        """
        Copy object within or between buckets

        Args:
            source_bucket: Source bucket name
            source_key: Source object key
            dest_bucket: Destination bucket name
            dest_key: Destination object key

        Returns:
            Response from copy_object API

        Raises:
            MetadataManagementException: If copy fails
        """
        try:
            copy_source = {'Bucket': source_bucket, 'Key': source_key}
            response = self.client.copy_object(
                CopySource=copy_source,
                Bucket=dest_bucket,
                Key=dest_key
            )
            logger.info(f"Copied s3://{source_bucket}/{source_key} to s3://{dest_bucket}/{dest_key}")
            return response

        except ClientError as e:
            logger.error(f"Failed to copy object: {e}")
            raise MetadataManagementException(f"Failed to copy object: {e}")
