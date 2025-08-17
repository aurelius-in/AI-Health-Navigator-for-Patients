"""
Environment-specific configuration settings for AI Health Navigator.

This module provides configuration classes for different environments.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class DevelopmentSettings(BaseSettings):
    """Development environment settings."""
    
    # Database
    database_url: str = Field(
        default="postgresql://dev_user:dev_password@localhost:5432/ai_health_navigator_dev",
        env="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # LLM Settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Logging
    log_level: str = Field(default="DEBUG", env="LOG_LEVEL")
    
    # CORS
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    class Config:
        env_file = ".env.development"


class ProductionSettings(BaseSettings):
    """Production environment settings."""
    
    # Database
    database_url: str = Field(env="DATABASE_URL")
    
    # Redis
    redis_url: str = Field(env="REDIS_URL")
    
    # Security
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # LLM Settings
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(env="ANTHROPIC_API_KEY")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # CORS
    cors_origins: list = Field(env="CORS_ORIGINS")
    
    class Config:
        env_file = ".env.production"


class TestingSettings(BaseSettings):
    """Testing environment settings."""
    
    # Database
    database_url: str = Field(
        default="sqlite:///./test.db",
        env="TEST_DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/1",
        env="TEST_REDIS_URL"
    )
    
    # Security
    secret_key: str = Field(
        default="test-secret-key",
        env="TEST_SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="TEST_ALGORITHM")
    access_token_expire_minutes: int = Field(default=5, env="TEST_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # LLM Settings
    openai_api_key: Optional[str] = Field(default=None, env="TEST_OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="TEST_ANTHROPIC_API_KEY")
    
    # Logging
    log_level: str = Field(default="WARNING", env="TEST_LOG_LEVEL")
    
    # CORS
    cors_origins: list = Field(
        default=["http://localhost:3000"],
        env="TEST_CORS_ORIGINS"
    )
    
    class Config:
        env_file = ".env.testing"


def get_settings():
    """Get settings based on environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export settings instance
settings = get_settings()
