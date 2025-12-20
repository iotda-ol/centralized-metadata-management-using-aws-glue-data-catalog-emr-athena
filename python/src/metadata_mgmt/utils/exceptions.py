"""
Custom exceptions for metadata management operations
"""


class MetadataManagementException(Exception):
    """Base exception for all metadata management errors"""
    pass


class CatalogException(MetadataManagementException):
    """Exception raised for Glue Catalog errors"""
    pass


class EMRException(MetadataManagementException):
    """Exception raised for EMR errors"""
    pass


class AthenaException(MetadataManagementException):
    """Exception raised for Athena errors"""
    pass


class ValidationException(MetadataManagementException):
    """Exception raised for validation errors"""
    pass


class ConfigurationException(MetadataManagementException):
    """Exception raised for configuration errors"""
    pass
