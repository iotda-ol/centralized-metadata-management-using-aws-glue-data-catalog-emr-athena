"""
Monitoring Module
CloudWatch metrics and alarms
"""

import boto3
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

from metadata_mgmt.utils.logging_config import get_logger
from metadata_mgmt.utils.exceptions import MetadataManagementException

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and publishes custom metrics to CloudWatch"""

    def __init__(self, namespace: str = "MetadataManagement", region_name: Optional[str] = None):
        """
        Initialize Metrics Collector

        Args:
            namespace: CloudWatch namespace
            region_name: AWS region name
        """
        self.client = boto3.client('cloudwatch', region_name=region_name)
        self.namespace = namespace
        logger.info(f"MetricsCollector initialized with namespace: {namespace}")

    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "None",
        dimensions: Optional[List[Dict[str, str]]] = None
    ) -> None:
        """
        Record a single metric

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            dimensions: Metric dimensions
        """
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit
            }

            if dimensions:
                metric_data['Dimensions'] = dimensions

            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )

            logger.debug(f"Recorded metric: {metric_name}={value} {unit}")

        except ClientError as e:
            logger.error(f"Failed to record metric: {e}")

    def record_job_duration(self, job_name: str, duration_seconds: float) -> None:
        """Record job execution duration"""
        self.record_metric(
            metric_name='JobDuration',
            value=duration_seconds,
            unit='Seconds',
            dimensions=[{'Name': 'JobName', 'Value': job_name}]
        )

    def record_error(self, component: str, error_type: str) -> None:
        """Record error occurrence"""
        self.record_metric(
            metric_name='Errors',
            value=1,
            unit='Count',
            dimensions=[
                {'Name': 'Component', 'Value': component},
                {'Name': 'ErrorType', 'Value': error_type}
            ]
        )

    def record_data_volume(self, table: str, bytes_processed: int) -> None:
        """Record data volume processed"""
        self.record_metric(
            metric_name='DataVolumeProcessed',
            value=bytes_processed,
            unit='Bytes',
            dimensions=[{'Name': 'Table', 'Value': table}]
        )


class AlarmManager:
    """Manages CloudWatch alarms"""

    def __init__(self, region_name: Optional[str] = None):
        """
        Initialize Alarm Manager

        Args:
            region_name: AWS region name
        """
        self.client = boto3.client('cloudwatch', region_name=region_name)
        logger.info("AlarmManager initialized")

    def create_alarm(
        self,
        name: str,
        metric_name: str,
        namespace: str,
        threshold: float,
        comparison_operator: str = "GreaterThanThreshold",
        evaluation_periods: int = 2,
        period: int = 300,
        statistic: str = "Average",
        alarm_actions: Optional[List[str]] = None,
        dimensions: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create CloudWatch alarm

        Args:
            name: Alarm name
            metric_name: Metric to monitor
            namespace: Metric namespace
            threshold: Alarm threshold
            comparison_operator: Comparison operator
            evaluation_periods: Number of periods to evaluate
            period: Period in seconds
            statistic: Statistic to apply
            alarm_actions: SNS topic ARNs for notifications
            dimensions: Metric dimensions

        Returns:
            Response from put_metric_alarm API
        """
        try:
            alarm_config = {
                'AlarmName': name,
                'MetricName': metric_name,
                'Namespace': namespace,
                'Threshold': threshold,
                'ComparisonOperator': comparison_operator,
                'EvaluationPeriods': evaluation_periods,
                'Period': period,
                'Statistic': statistic
            }

            if alarm_actions:
                alarm_config['AlarmActions'] = alarm_actions

            if dimensions:
                alarm_config['Dimensions'] = dimensions

            response = self.client.put_metric_alarm(**alarm_config)
            logger.info(f"Created alarm: {name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to create alarm: {e}")
            raise MetadataManagementException(f"Failed to create alarm: {e}")

    def delete_alarm(self, name: str) -> Dict[str, Any]:
        """
        Delete CloudWatch alarm

        Args:
            name: Alarm name

        Returns:
            Response from delete_alarms API
        """
        try:
            response = self.client.delete_alarms(AlarmNames=[name])
            logger.info(f"Deleted alarm: {name}")
            return response

        except ClientError as e:
            logger.error(f"Failed to delete alarm: {e}")
            raise MetadataManagementException(f"Failed to delete alarm: {e}")
