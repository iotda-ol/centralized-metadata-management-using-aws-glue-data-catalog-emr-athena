"""
Configuration management for metadata management
"""

import os
from typing import Any, Dict, Optional
from metadata_mgmt.utils.exceptions import ConfigurationException


class Config:
    """Configuration manager for metadata management"""

    def __init__(self, environment: Optional[str] = None):
        """
        Initialize configuration

        Args:
            environment: Environment name (dev, staging, prod)
        """
        self.environment = environment or os.getenv('ENVIRONMENT', 'dev')
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration based on environment"""
        base_config = {
            'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
            'project_name': os.getenv('PROJECT_NAME', 'metadata-mgmt'),
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        }

        env_configs = {
            'dev': {
                'emr_instance_type': 'm5.xlarge',
                'emr_instance_count': 2,
                'athena_workgroup': 'primary',
            },
            'staging': {
                'emr_instance_type': 'm5.xlarge',
                'emr_instance_count': 3,
                'athena_workgroup': 'staging',
            },
            'prod': {
                'emr_instance_type': 'm5.2xlarge',
                'emr_instance_count': 5,
                'athena_workgroup': 'production',
            }
        }

        config = {**base_config, **env_configs.get(self.environment, env_configs['dev'])}
        return config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary syntax"""
        if key not in self._config:
            raise ConfigurationException(f"Configuration key not found: {key}")
        return self._config[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set configuration value using dictionary syntax"""
        self._config[key] = value

    def update(self, config: Dict[str, Any]) -> None:
        """
        Update configuration

        Args:
            config: Dictionary of configuration updates
        """
        self._config.update(config)
