"""
Advanced logging configuration for AI Health Navigator.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory

from .config import settings


def configure_logging() -> None:
    """Configure structured logging with observability features."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.environment == "production" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.monitoring.log_level.upper()),
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class HealthNavigatorLogger:
    """Enhanced logger with healthcare-specific context."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def log_symptom_check(self, user_id: str, symptoms: str, confidence: float, **kwargs) -> None:
        """Log symptom check with healthcare context."""
        self.logger.info(
            "Symptom check completed",
            user_id=user_id,
            symptoms=symptoms,
            confidence=confidence,
            event_type="symptom_check",
            **kwargs
        )
    
    def log_triage_assessment(self, user_id: str, urgency_level: str, recommended_care: str, **kwargs) -> None:
        """Log triage assessment with healthcare context."""
        self.logger.info(
            "Triage assessment completed",
            user_id=user_id,
            urgency_level=urgency_level,
            recommended_care=recommended_care,
            event_type="triage_assessment",
            **kwargs
        )
    
    def log_provider_match(self, user_id: str, provider_id: str, match_score: float, **kwargs) -> None:
        """Log provider matching with healthcare context."""
        self.logger.info(
            "Provider match completed",
            user_id=user_id,
            provider_id=provider_id,
            match_score=match_score,
            event_type="provider_match",
            **kwargs
        )
    
    def log_insurance_query(self, user_id: str, query_type: str, coverage_status: str, **kwargs) -> None:
        """Log insurance queries with healthcare context."""
        self.logger.info(
            "Insurance query processed",
            user_id=user_id,
            query_type=query_type,
            coverage_status=coverage_status,
            event_type="insurance_query",
            **kwargs
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """Log errors with healthcare context."""
        self.logger.error(
            "Application error occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            event_type="error",
            **(context or {})
        )
    
    def log_performance(self, operation: str, duration_ms: float, **kwargs) -> None:
        """Log performance metrics."""
        self.logger.info(
            "Performance metric",
            operation=operation,
            duration_ms=duration_ms,
            event_type="performance",
            **kwargs
        )
    
    def log_security_event(self, event_type: str, user_id: Optional[str] = None, **kwargs) -> None:
        """Log security-related events."""
        self.logger.warning(
            "Security event detected",
            security_event_type=event_type,
            user_id=user_id,
            event_type="security",
            **kwargs
        )


# Configure logging on module import
configure_logging()

# Create default logger instance
logger = get_logger(__name__)
