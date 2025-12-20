"""
Unit tests for QueryRunner
"""

import pytest
from unittest.mock import Mock

from metadata_mgmt.athena.query_runner import QueryRunner


@pytest.fixture
def mock_athena_client():
    """Mock Athena client for testing"""
    return Mock()


@pytest.fixture
def query_runner(mock_athena_client):
    """QueryRunner instance with mocked client"""
    return QueryRunner(workgroup='test', client=mock_athena_client)


def test_execute_query_no_wait(query_runner, mock_athena_client):
    """Test query execution without waiting"""
    mock_athena_client.start_query_execution.return_value = {
        'QueryExecutionId': 'test-query-id-123'
    }

    result = query_runner.execute_query(
        query='SELECT * FROM test_table',
        database='test_db',
        wait=False
    )

    assert result['QueryExecutionId'] == 'test-query-id-123'
    mock_athena_client.start_query_execution.assert_called_once()


def test_wait_for_query_success(query_runner, mock_athena_client):
    """Test waiting for query completion"""
    mock_athena_client.get_query_execution.return_value = {
        'QueryExecution': {
            'Status': {'State': 'SUCCEEDED'}
        }
    }

    state = query_runner.wait_for_query('test-query-id', max_wait_seconds=10)
    assert state == 'SUCCEEDED'
