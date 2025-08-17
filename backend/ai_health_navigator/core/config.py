"""
Configuration management for AI Health Navigator.
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    url: str = Field(default="postgresql://user:pass@localhost/health_nav", env="DATABASE_URL")
    pool_size: int = Field(default=20, env="DB_POOL_SIZE")
    max_overflow: int = Field(default=30, env="DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, env="DB_ECHO")
    
    class Config:
        env_prefix = "DB_"


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    
    url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    class Config:
        env_prefix = "REDIS_"


class LLMSettings(BaseSettings):
    """Large Language Model configuration settings."""
    
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    default_model: str = Field(default="gpt-4", env="DEFAULT_LLM_MODEL")
    max_tokens: int = Field(default=4000, env="LLM_MAX_TOKENS")
    temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    
    class Config:
        env_prefix = "LLM_"


class VectorDBSettings(BaseSettings):
    """Vector database configuration settings."""
    
    type: str = Field(default="chroma", env="VECTOR_DB_TYPE")  # chroma, pinecone, qdrant
    chroma_path: str = Field(default="./chroma_db", env="CHROMA_PATH")
    pinecone_api_key: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    
    class Config:
        env_prefix = "VECTOR_DB_"


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    class Config:
        env_prefix = "SECURITY_"


class MonitoringSettings(BaseSettings):
    """Monitoring and observability settings."""
    
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    
    class Config:
        env_prefix = "MONITORING_"


class MLModelSettings(BaseSettings):
    """Machine learning model configuration."""
    
    symptom_classifier_path: str = Field(default="./models/symptom_classifier.pkl", env="SYMPTOM_CLASSIFIER_PATH")
    urgency_predictor_path: str = Field(default="./models/urgency_predictor.pkl", env="URGENCY_PREDICTOR_PATH")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    batch_size: int = Field(default=32, env="ML_BATCH_SIZE")
    
    class Config:
        env_prefix = "ML_"


class APISettings(BaseSettings):
    """API configuration settings."""
    
    title: str = Field(default="AI Health Navigator API", env="API_TITLE")
    version: str = Field(default="1.0.0", env="API_VERSION")
    description: str = Field(default="Advanced AI-powered health navigation platform", env="API_DESCRIPTION")
    debug: bool = Field(default=False, env="API_DEBUG")
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_prefix = "API_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Sub-settings
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    llm: LLMSettings = LLMSettings()
    vector_db: VectorDBSettings = VectorDBSettings()
    security: SecuritySettings = SecuritySettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    ml_models: MLModelSettings = MLModelSettings()
    api: APISettings = APISettings()
    
    # Feature flags
    enable_symptom_checker: bool = Field(default=True, env="ENABLE_SYMPTOM_CHECKER")
    enable_provider_matching: bool = Field(default=True, env="ENABLE_PROVIDER_MATCHING")
    enable_insurance_guidance: bool = Field(default=True, env="ENABLE_INSURANCE_GUIDANCE")
    enable_multilingual: bool = Field(default=True, env="ENABLE_MULTILINGUAL")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # Cache settings
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
