"""
EMR Job Submitter
Submits and manages EMR jobs
"""

import boto3
import time
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError

from metadata_mgmt.utils.logging_config import get_logger
from metadata_mgmt.utils.exceptions import EMRException
from metadata_mgmt.utils.retry import retry

logger = get_logger(__name__)


class JobSubmitter:
    """Manages EMR job submission and monitoring"""

    def __init__(self, cluster_id: str, region_name: Optional[str] = None, client: Optional[Any] = None):
        """
        Initialize Job Submitter

        Args:
            cluster_id: EMR cluster ID
            region_name: AWS region name
            client: Optional boto3 EMR client (for testing)
        """
        self.client = client or boto3.client('emr', region_name=region_name)
        self.cluster_id = cluster_id
        logger.info(f"JobSubmitter initialized for cluster: {cluster_id}")

    @retry(max_attempts=3)
    def submit_spark_job(
        self,
        script: str,
        args: Optional[List[str]] = None,
        name: str = "Spark Job",
        spark_submit_parameters: str = ""
    ) -> str:
        """
        Submit Spark job to EMR

        Args:
            script: S3 path to Spark script
            args: Script arguments
            name: Job name
            spark_submit_parameters: Additional spark-submit parameters

        Returns:
            Step ID

        Raises:
            EMRException: If job submission fails
        """
        try:
            step_args = ['spark-submit']

            if spark_submit_parameters:
                step_args.extend(spark_submit_parameters.split())

            step_args.append(script)

            if args:
                step_args.extend(args)

            step = {
                'Name': name,
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': step_args
                }
            }

            response = self.client.add_job_flow_steps(
                JobFlowId=self.cluster_id,
                Steps=[step]
            )

            step_id = response['StepIds'][0]
            logger.info(f"Submitted Spark job: {step_id}")
            return step_id

        except ClientError as e:
            logger.error(f"Failed to submit Spark job: {e}")
            raise EMRException(f"Job submission failed: {e}")

    @retry(max_attempts=3)
    def wait_for_step(
        self,
        step_id: str,
        max_wait_seconds: int = 3600,
        poll_interval: int = 10
    ) -> str:
        """
        Wait for step completion

        Args:
            step_id: Step ID
            max_wait_seconds: Maximum wait time
            poll_interval: Seconds between status checks

        Returns:
            Final step state

        Raises:
            EMRException: If step fails or times out
        """
        elapsed = 0
        while elapsed < max_wait_seconds:
            response = self.client.describe_step(
                ClusterId=self.cluster_id,
                StepId=step_id
            )
            state = response['Step']['Status']['State']

            if state == 'COMPLETED':
                logger.info(f"Step {step_id} completed successfully")
                return state
            elif state in ['FAILED', 'CANCELLED']:
                reason = response['Step']['Status'].get('FailureDetails', {}).get('Message', 'Unknown')
                logger.error(f"Step {step_id} failed: {reason}")
                raise EMRException(f"Step failed: {reason}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise EMRException(f"Step {step_id} timed out after {max_wait_seconds}s")

    @retry(max_attempts=3)
    def get_step_status(self, step_id: str) -> Dict[str, Any]:
        """
        Get step status

        Args:
            step_id: Step ID

        Returns:
            Step status information
        """
        try:
            response = self.client.describe_step(
                ClusterId=self.cluster_id,
                StepId=step_id
            )
            return response['Step']['Status']

        except ClientError as e:
            logger.error(f"Failed to get step status: {e}")
            raise EMRException(f"Failed to get status: {e}")
