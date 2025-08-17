"""
Main FastAPI application for AI Health Navigator.
"""

import time
from contextlib import asynccontextmanager
from typing import Dict, Any

import sentry_sdk
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..core.config import settings
from ..core.logging import get_logger, HealthNavigatorLogger
from ..ai.models import model_manager
from ..ai.llm_service import llm_service
from .routes import symptoms, triage, providers, insurance, auth, health, agents, enhanced_agents
from .middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    PerformanceMiddleware
)

logger = get_logger(__name__)
health_logger = HealthNavigatorLogger("API")


# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

AI_PREDICTION_COUNT = Counter(
    "ai_predictions_total",
    "Total AI predictions",
    ["model", "type"]
)

AI_PREDICTION_DURATION = Histogram(
    "ai_prediction_duration_seconds",
    "AI prediction duration in seconds",
    ["model", "type"]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting AI Health Navigator API...")
    
    try:
        # Initialize AI models
        logger.info("Initializing AI models...")
        await model_manager.initialize_models()
        
        # Initialize LLM service
        logger.info("Initializing LLM service...")
        await llm_service.initialize()
        
        # Initialize Sentry if configured
        if settings.monitoring.sentry_dsn:
            sentry_sdk.init(
                dsn=settings.monitoring.sentry_dsn,
                environment=settings.environment,
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
            )
            logger.info("Sentry monitoring initialized")
        
        logger.info("AI Health Navigator API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Health Navigator API...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        description=settings.api.description,
        debug=settings.api.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.api.debug else None,
        redoc_url="/redoc" if settings.api.debug else None,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"] if settings.api.debug else ["localhost", "127.0.0.1"]
    )
    
    # Add custom middleware
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(symptoms.router, prefix="/api/v1/symptoms", tags=["Symptoms"])
    app.include_router(triage.router, prefix="/api/v1/triage", tags=["Triage"])
    app.include_router(providers.router, prefix="/api/v1/providers", tags=["Providers"])
    app.include_router(insurance.router, prefix="/api/v1/insurance", tags=["Insurance"])
    app.include_router(agents.router, prefix="/api/v1/agents", tags=["AI Agents"])
    app.include_router(enhanced_agents.router, prefix="/api/v1/enhanced-agents", tags=["Enhanced AI Agents"])
    
    # Add metrics endpoint
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Prometheus metrics endpoint."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    # Add root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.api.title,
            "version": settings.api.version,
            "description": settings.api.description,
            "status": "healthy",
            "environment": settings.environment,
            "docs": "/docs" if settings.api.debug else None,
            "health": "/api/v1/health",
            "metrics": "/metrics"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler."""
        health_logger.log_error(exc, {
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host if request.client else None
        })
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        )
    
    # HTTP exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """HTTP exception handler."""
        health_logger.log_security_event(
            "http_exception",
            context={
                "status_code": exc.status_code,
                "request_path": request.url.path,
                "request_method": request.method
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        )
    
    return app


# Create application instance
app = create_app()


# Dependency for getting current user (placeholder for auth)
async def get_current_user(request: Request):
    """Get current authenticated user."""
    # This would implement actual authentication logic
    # For now, return a mock user
    return {
        "id": "user_123",
        "email": "user@example.com",
        "role": "patient"
    }


# Health check dependency
async def check_health():
    """Check system health."""
    try:
        # Check AI models
        models_healthy = len(model_manager.models) > 0
        
        # Check LLM providers
        llm_health = await llm_service.health_check()
        llm_healthy = any(llm_health.values())
        
        return {
            "models": models_healthy,
            "llm_providers": llm_health,
            "overall": models_healthy and llm_healthy
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "models": False,
            "llm_providers": {},
            "overall": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "ai_health_navigator.api.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level=settings.monitoring.log_level.lower()
    )
