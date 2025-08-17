"""
Advanced middleware for AI Health Navigator API.
"""

import time
import uuid
from typing import Dict, Any, Optional

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis.asyncio as redis

from ..core.config import settings
from ..core.logging import get_logger, HealthNavigatorLogger

logger = get_logger(__name__)
health_logger = HealthNavigatorLogger("Middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request logging."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request start
        start_time = time.time()
        
        # Extract request details
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        
        logger.info(
            "Request started",
            request_id=request_id,
            method=method,
            path=path,
            client_ip=client_ip,
            user_agent=user_agent
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log successful request
            logger.info(
                "Request completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                processing_time=processing_time
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Processing-Time"] = str(processing_time)
            
            return response
            
        except Exception as e:
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Log failed request
            logger.error(
                "Request failed",
                request_id=request_id,
                method=method,
                path=path,
                error=str(e),
                processing_time=processing_time
            )
            
            # Re-raise the exception
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit = settings.rate_limit_per_minute
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/api/v1/health", "/metrics", "/"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if await self._is_rate_limited(client_id):
            health_logger.log_security_event(
                "rate_limit_exceeded",
                context={
                    "client_id": client_id,
                    "path": request.url.path,
                    "method": request.method
                }
            )
            
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Increment request count
        await self._increment_request_count(client_id)
        
        return await call_next(request)
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier."""
        # Use API key if available
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Use user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        if not self.redis_client:
            return False  # Skip rate limiting if Redis not available
        
        try:
            key = f"rate_limit:{client_id}"
            current_count = await self.redis_client.get(key)
            
            if current_count:
                return int(current_count) >= self.rate_limit
            
            return False
            
        except Exception as e:
            logger.warning(f"Rate limit check failed: {e}")
            return False  # Allow request if rate limiting fails
    
    async def _increment_request_count(self, client_id: str) -> None:
        """Increment request count for client."""
        if not self.redis_client:
            return
        
        try:
            key = f"rate_limit:{client_id}"
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)  # Expire after 1 minute
            await pipe.execute()
            
        except Exception as e:
            logger.warning(f"Failed to increment request count: {e}")


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security checks and headers."""
    
    async def dispatch(self, request: Request, call_next):
        # Security checks
        await self._perform_security_checks(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response = self._add_security_headers(response)
        
        return response
    
    async def _perform_security_checks(self, request: Request) -> None:
        """Perform security checks on the request."""
        # Check for suspicious patterns
        suspicious_patterns = [
            "script", "javascript", "eval(", "document.cookie",
            "union select", "drop table", "exec(", "system("
        ]
        
        # Check URL path
        path = request.url.path.lower()
        for pattern in suspicious_patterns:
            if pattern in path:
                health_logger.log_security_event(
                    "suspicious_request_pattern",
                    context={
                        "pattern": pattern,
                        "path": path,
                        "client_ip": request.client.host if request.client else "unknown"
                    }
                )
                raise HTTPException(status_code=400, detail="Invalid request")
        
        # Check request body for suspicious content
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                body_str = body.decode("utf-8").lower()
                
                for pattern in suspicious_patterns:
                    if pattern in body_str:
                        health_logger.log_security_event(
                            "suspicious_request_body",
                            context={
                                "pattern": pattern,
                                "method": request.method,
                                "path": path
                            }
                        )
                        raise HTTPException(status_code=400, detail="Invalid request content")
                        
            except Exception:
                # If we can't read the body, continue
                pass
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log performance metrics
        self._log_performance_metrics(request, response, processing_time)
        
        # Add performance headers
        response.headers["X-Processing-Time"] = f"{processing_time:.4f}"
        
        return response
    
    def _log_performance_metrics(
        self, 
        request: Request, 
        response: Response, 
        processing_time: float
    ) -> None:
        """Log performance metrics."""
        # Log slow requests
        if processing_time > 1.0:  # More than 1 second
            health_logger.log_performance(
                operation=f"{request.method} {request.url.path}",
                duration_ms=processing_time * 1000,
                status_code=response.status_code,
                request_id=getattr(request.state, "request_id", "unknown")
            )
        
        # Log all requests for monitoring
        logger.info(
            "Request performance",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            processing_time=processing_time,
            request_id=getattr(request.state, "request_id", "unknown")
        )


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for authentication and authorization."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extract and validate authentication
        user = await self._authenticate_request(request)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        
        # Add user to request state
        request.state.user = user
        request.state.user_id = user.get("id")
        
        # Check authorization
        if not await self._authorize_request(request, user):
            health_logger.log_security_event(
                "unauthorized_access",
                context={
                    "user_id": user.get("id"),
                    "path": request.url.path,
                    "method": request.method
                }
            )
            
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        return await call_next(request)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public."""
        public_paths = [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health",
            "/metrics",
            "/api/v1/auth/login",
            "/api/v1/auth/register"
        ]
        
        return any(path.startswith(public_path) for public_path in public_paths)
    
    async def _authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate the request."""
        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return await self._validate_api_key(api_key)
        
        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            return await self._validate_jwt_token(token)
        
        return None
    
    async def _validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key."""
        # This would validate against a database
        # For now, return a mock user
        if api_key == "test_api_key":
            return {
                "id": "api_user_123",
                "email": "api@example.com",
                "role": "api_user",
                "permissions": ["read", "write"]
            }
        return None
    
    async def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token."""
        # This would validate the JWT token
        # For now, return a mock user
        if token == "test_jwt_token":
            return {
                "id": "jwt_user_123",
                "email": "jwt@example.com",
                "role": "patient",
                "permissions": ["read"]
            }
        return None
    
    async def _authorize_request(self, request: Request, user: Dict[str, Any]) -> bool:
        """Authorize the request."""
        # Check user permissions
        required_permissions = self._get_required_permissions(request.url.path, request.method)
        user_permissions = user.get("permissions", [])
        
        return all(perm in user_permissions for perm in required_permissions)
    
    def _get_required_permissions(self, path: str, method: str) -> list:
        """Get required permissions for the endpoint."""
        # Define permission requirements for different endpoints
        permission_map = {
            ("/api/v1/symptoms/analyze", "POST"): ["read"],
            ("/api/v1/triage/assess", "POST"): ["read"],
            ("/api/v1/providers/search", "GET"): ["read"],
            ("/api/v1/insurance/check", "POST"): ["read"],
        }
        
        return permission_map.get((path, method), [])


class CachingMiddleware(BaseHTTPMiddleware):
    """Middleware for response caching."""
    
    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.cache_ttl = settings.cache_ttl_seconds
    
    async def dispatch(self, request: Request, call_next):
        # Skip caching for non-GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Skip caching for authenticated requests
        if hasattr(request.state, "user"):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Try to get cached response
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200:
            await self._cache_response(cache_key, response)
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for the request."""
        # Include path and query parameters
        key_parts = [request.url.path]
        
        # Add query parameters
        for key, value in request.query_params.items():
            key_parts.append(f"{key}={value}")
        
        return f"cache:{':'.join(key_parts)}"
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Response]:
        """Get cached response."""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                # Parse cached response
                import json
                data = json.loads(cached_data)
                
                response = Response(
                    content=data["content"],
                    status_code=data["status_code"],
                    headers=data["headers"]
                )
                
                response.headers["X-Cache"] = "HIT"
                return response
                
        except Exception as e:
            logger.warning(f"Failed to get cached response: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: Response) -> None:
        """Cache the response."""
        if not self.redis_client:
            return
        
        try:
            # Prepare response data for caching
            response_data = {
                "content": response.body.decode(),
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }
            
            # Cache the response
            await self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                response_data
            )
            
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
