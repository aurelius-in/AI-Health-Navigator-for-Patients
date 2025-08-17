"""
Environment configuration management for AI Health Navigator.

This module manages environment-specific configurations and provides utilities
for environment detection and configuration loading.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class Environment(Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentConfig:
    """Environment configuration manager."""
    
    def __init__(self):
        self._environment = self._detect_environment()
        self._config_cache: Dict[str, Any] = {}
    
    def _detect_environment(self) -> Environment:
        """Detect the current environment."""
        env_var = os.getenv("ENVIRONMENT", "").lower()
        
        if env_var == "production":
            return Environment.PRODUCTION
        elif env_var == "staging":
            return Environment.STAGING
        elif env_var == "testing":
            return Environment.TESTING
        else:
            return Environment.DEVELOPMENT
    
    @property
    def environment(self) -> Environment:
        """Get current environment."""
        return self._environment
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self._environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self._environment == Environment.TESTING
    
    @property
    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self._environment == Environment.STAGING
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self._environment == Environment.PRODUCTION
    
    def get_config_file_path(self, filename: str) -> Optional[Path]:
        """Get the path to a configuration file for the current environment."""
        config_dir = Path(__file__).parent
        
        # Try environment-specific file first
        env_specific = config_dir / f"{filename}.{self._environment.value}"
        if env_specific.exists():
            return env_specific
        
        # Fall back to base file
        base_file = config_dir / filename
        if base_file.exists():
            return base_file
        
        return None
    
    def load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load configuration from a file."""
        if filename in self._config_cache:
            return self._config_cache[filename]
        
        config_path = self.get_config_file_path(filename)
        if not config_path:
            return {}
        
        # Load configuration based on file extension
        if config_path.suffix == ".json":
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
        elif config_path.suffix in [".yaml", ".yml"]:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        elif config_path.suffix == ".ini":
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            # Convert to dict
            config_dict = {}
            for section in config.sections():
                config_dict[section] = dict(config[section])
            config = config_dict
        else:
            # Try to load as Python module
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", config_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                config = {k: v for k, v in module.__dict__.items() 
                         if not k.startswith('_')}
            else:
                config = {}
        
        self._config_cache[filename] = config
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        # Try environment variable first
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
        
        # Try configuration files
        for filename in ["config.json", "config.yaml", "config.yml", "config.ini"]:
            config = self.load_config_file(filename)
            if key in config:
                return config[key]
        
        return default
    
    def get_nested(self, key_path: str, default: Any = None) -> Any:
        """Get a nested configuration value using dot notation."""
        keys = key_path.split('.')
        
        # Try environment variable first
        env_value = os.getenv(key_path.replace('.', '_').upper())
        if env_value is not None:
            return env_value
        
        # Try configuration files
        for filename in ["config.json", "config.yaml", "config.yml", "config.ini"]:
            config = self.load_config_file(filename)
            value = config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            if value is not None:
                return value
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value (in memory only)."""
        self._config_cache[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        all_config = {}
        
        # Load from all configuration files
        for filename in ["config.json", "config.yaml", "config.yml", "config.ini"]:
            config = self.load_config_file(filename)
            all_config.update(config)
        
        # Override with environment variables
        for key, value in os.environ.items():
            if key.startswith(('AI_HEALTH_', 'APP_')):
                all_config[key.lower()] = value
        
        return all_config
    
    def validate_required_configs(self, required_keys: list) -> list:
        """Validate that required configuration keys are present."""
        missing_keys = []
        
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        return missing_keys


# Global environment configuration instance
env_config = EnvironmentConfig()


def get_env_config() -> EnvironmentConfig:
    """Get the global environment configuration instance."""
    return env_config


def is_development() -> bool:
    """Check if running in development environment."""
    return env_config.is_development


def is_production() -> bool:
    """Check if running in production environment."""
    return env_config.is_production


def is_testing() -> bool:
    """Check if running in testing environment."""
    return env_config.is_testing


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    return env_config.get(key, default)


def get_nested_config(key_path: str, default: Any = None) -> Any:
    """Get a nested configuration value."""
    return env_config.get_nested(key_path, default)
