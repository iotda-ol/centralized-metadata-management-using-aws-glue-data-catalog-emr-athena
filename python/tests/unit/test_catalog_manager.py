"""
Unit tests for CatalogManager
"""

import pytest
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from metadata_mgmt.glue.catalog_manager import CatalogManager
from metadata_mgmt.utils.exceptions import CatalogException


@pytest.fixture
def mock_glue_client():
    """Mock Glue client for testing"""
    return Mock()


@pytest.fixture
def catalog_manager(mock_glue_client):
    """CatalogManager instance with mocked client"""
    return CatalogManager(client=mock_glue_client)


def test_create_database_success(catalog_manager, mock_glue_client):
    """Test successful database creation"""
    mock_glue_client.create_database.return_value = {
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }

    result = catalog_manager.create_database(
        name='test_db',
        description='Test database'
    )

    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
    mock_glue_client.create_database.assert_called_once()


def test_create_database_already_exists(catalog_manager, mock_glue_client):
    """Test database creation when database already exists"""
    error_response = {
        'Error': {'Code': 'AlreadyExistsException', 'Message': 'Database exists'}
    }
    mock_glue_client.create_database.side_effect = ClientError(error_response, 'CreateDatabase')

    result = catalog_manager.create_database('test_db')
    assert result['ResponseMetadata']['HTTPStatusCode'] == 200


def test_create_table_success(catalog_manager, mock_glue_client):
    """Test successful table creation"""
    mock_glue_client.create_table.return_value = {
        'ResponseMetadata': {'HTTPStatusCode': 200}
    }

    schema = [
        {'Name': 'id', 'Type': 'bigint'},
        {'Name': 'name', 'Type': 'string'}
    ]

    result = catalog_manager.create_table(
        database='test_db',
        table='test_table',
        schema=schema,
        location='s3://bucket/path/',
        format='parquet'
    )

    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
    mock_glue_client.create_table.assert_called_once()


def test_get_table_success(catalog_manager, mock_glue_client):
    """Test successful table retrieval"""
    expected_table = {
        'Name': 'test_table',
        'DatabaseName': 'test_db',
        'StorageDescriptor': {}
    }
    mock_glue_client.get_table.return_value = {'Table': expected_table}

    result = catalog_manager.get_table('test_db', 'test_table')

    assert result == expected_table
    mock_glue_client.get_table.assert_called_once_with(
        DatabaseName='test_db',
        Name='test_table'
    )


def test_get_table_not_found(catalog_manager, mock_glue_client):
    """Test table retrieval when table doesn't exist"""
    error_response = {
        'Error': {'Code': 'EntityNotFoundException', 'Message': 'Table not found'}
    }
    mock_glue_client.get_table.side_effect = ClientError(error_response, 'GetTable')

    with pytest.raises(CatalogException):
        catalog_manager.get_table('test_db', 'test_table')
