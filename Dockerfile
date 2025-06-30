# Grant AI Dockerfile
# Multi-stage build for optimized production image

# Use Python 3.11 slim image as base
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt ./
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Development command
CMD ["python", "-m", "grant_ai.core.cli", "gui"]

# Production stage
FROM base as production

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/reports

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Production command
CMD ["python", "-m", "grant_ai.core.cli"]

# Testing stage
FROM development as testing

# Install testing dependencies
RUN pip install --no-cache-dir pytest pytest-cov pytest-mock

# Run tests
CMD ["pytest", "tests/", "-v", "--cov=src/grant_ai", "--cov-report=html"] 