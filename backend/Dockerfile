# Multi-stage Docker build for AI Health Navigator
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "ai_health_navigator.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]


# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -e .[dev]

# Copy development files
COPY .env.example .env
COPY docker/entrypoint-dev.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Development command
CMD ["/entrypoint.sh"]


# Production stage
FROM base as production

# Install production dependencies only
RUN pip install --no-cache-dir -e .[monitoring]

# Copy production configuration
COPY docker/entrypoint-prod.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Production command
CMD ["/entrypoint.sh"]


# ML Models stage (for GPU support)
FROM nvidia/cuda:11.8-runtime-ubuntu20.04 as ml-gpu

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt pyproject.toml ./

# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# GPU-enabled command
CMD ["python3", "-m", "ai_health_navigator.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]
