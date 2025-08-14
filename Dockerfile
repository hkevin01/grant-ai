# Grant AI Dockerfile
# Multi-stage build for optimized production image

# Use Python 3.11 slim image as base
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies (incl. X11/Qt runtime libs for PyQt5)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    libx11-xcb1 \
    libxrender1 \
    libxcb1 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libgl1 \
    libdbus-1-3 \
    libfontconfig1 \
    libglib2.0-0 \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata for installs in later stages
COPY pyproject.toml ./

# Development stage
FROM base AS development

# Copy source code first, then install in editable mode
COPY . .

# Install development dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Development command
CMD ["python", "-m", "grant_ai.core.cli", "gui"]

# Production stage
FROM base AS production

# Copy source code
COPY . .

# Install package with runtime dependencies
RUN pip install --no-cache-dir .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/reports

# Expose port
EXPOSE 8000

# Health check (uses curl available from base)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Production command
CMD ["python", "-m", "grant_ai.core.cli"]

# Testing stage
FROM development AS testing

# Install testing dependencies
RUN pip install --no-cache-dir pytest pytest-cov pytest-mock

# Run tests
CMD ["pytest", "tests/", "-v", "--cov=src/grant_ai", "--cov-report=html"]
