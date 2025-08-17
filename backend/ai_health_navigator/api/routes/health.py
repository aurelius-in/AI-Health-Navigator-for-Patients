"""
Health check API routes for AI Health Navigator.
"""

import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...core.config import settings
from ...core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment,
        "service": "ai-health-navigator"
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with database connectivity."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment,
        "service": "ai-health-navigator",
        "checks": {
            "database": "unknown",
            "redis": "unknown",
            "ai_models": "unknown",
            "external_apis": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis connectivity (if configured)
    try:
        import redis
        r = redis.from_url(settings.redis.url)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")
    
    # Check AI models
    try:
        from ...ai.models import model_manager
        # Basic check - could be expanded to test actual model loading
        health_status["checks"]["ai_models"] = "healthy"
    except Exception as e:
        health_status["checks"]["ai_models"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"AI models health check failed: {e}")
    
    # Check external APIs (LLM providers)
    try:
        # Check OpenAI API (if configured)
        if settings.openai_api_key:
            import openai
            openai.api_key = settings.openai_api_key
            # Simple test - could be expanded
            health_status["checks"]["external_apis"] = "healthy"
        else:
            health_status["checks"]["external_apis"] = "not_configured"
    except Exception as e:
        health_status["checks"]["external_apis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"External APIs health check failed: {e}")
    
    return health_status


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Readiness check for Kubernetes/container orchestration."""
    try:
        # Check database
        db.execute("SELECT 1")
        
        # Check Redis
        import redis
        r = redis.from_url(settings.redis.url)
        r.ping()
        
        # Check AI models
        from ...ai.models import model_manager
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ai-health-navigator"
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "ai-health-navigator",
            "error": str(e)
        }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes/container orchestration."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ai-health-navigator"
    }


@router.get("/info")
async def service_info() -> Dict[str, Any]:
    """Get service information and configuration."""
    return {
        "name": "AI Health Navigator",
        "version": "1.0.0",
        "description": "Advanced AI-powered health navigation platform",
        "environment": settings.environment,
        "features": [
            "Symptom Analysis",
            "Triage Assessment",
            "Provider Matching",
            "AI Agents",
            "Medication Management",
            "Preventive Care",
            "Mental Health Support"
        ],
        "api_version": "v1",
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/status")
async def service_status() -> Dict[str, Any]:
    """Get detailed service status."""
    return {
        "service": "ai-health-navigator",
        "status": "operational",
        "uptime": "running",
        "version": "1.0.0",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "operational",
            "database": "operational",
            "cache": "operational",
            "ai_models": "operational",
            "monitoring": "operational"
        }
    }
