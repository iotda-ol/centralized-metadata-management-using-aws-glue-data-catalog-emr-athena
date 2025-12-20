"""
Metadata Management Package
Centralized metadata management using AWS Glue Data Catalog, EMR, and Athena
"""

__version__ = "1.0.0"
__author__ = "Data Engineering Team"

from metadata_mgmt.glue.catalog_manager import CatalogManager
from metadata_mgmt.glue.crawler_manager import CrawlerManager
from metadata_mgmt.emr.job_submitter import JobSubmitter
from metadata_mgmt.athena.query_runner import QueryRunner
from metadata_mgmt.monitoring.metrics import MetricsCollector, AlarmManager
from metadata_mgmt.utils.config import Config
from metadata_mgmt.utils.s3_utils import S3Utils

__all__ = [
    "CatalogManager",
    "CrawlerManager",
    "JobSubmitter",
    "QueryRunner",
    "MetricsCollector",
    "AlarmManager",
    "Config",
    "S3Utils",
]
