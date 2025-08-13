# Grant AI Makefile
# Provides common development tasks and automation

.PHONY: help install format lint typecheck security test check build clean run gui docs setup venv

# Default target
help:
	@echo "Grant AI Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup      - Set up development environment"
	@echo "  install    - Install dependencies"
	@echo "  format     - Format code with Black and isort"
	@echo "  lint       - Run linting with Ruff"
	@echo "  typecheck  - Run type checking with MyPy"
	@echo "  security   - Run security checks"
	@echo "  test       - Run all tests"
	@echo "  test-unit  - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e   - Run end-to-end tests only"
	@echo "  check      - Run all quality checks"
	@echo "  build      - Build the package"
	@echo "  clean      - Clean build artifacts"
	@echo "  run        - Run the application"
	@echo "  gui        - Launch the GUI"
	@echo "  docs       - Generate documentation"
	@echo "  venv       - Create virtual environment"
	@echo "  release    - Create a new release"

# Set up development environment
setup: venv install
	@echo "Development environment setup complete!"

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate  # On Unix/macOS"
	@echo "  venv\\Scripts\\activate     # On Windows"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -e ".[dev]"
	@echo "Dependencies installed successfully"

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/ scripts/
	isort src/ tests/ scripts/
	@echo "Code formatting completed"

# Run linting
lint:
	@echo "Running linting..."
	ruff check src/ tests/ scripts/
	@echo "Linting completed"

# Run type checking
typecheck:
	@echo "Running type checking..."
	mypy src/
	@echo "Type checking completed"

# Run security checks
security:
	@echo "Running security checks..."
	bandit -r src/ -f json -o bandit-report.json || true
	safety check
	@echo "Security checks completed"

# Run all tests
test:
	@echo "Running all tests..."
	source venv/bin/activate && pytest tests/ -v --cov=src/grant_ai --cov-report=term-missing --cov-report=html
	@echo "Tests completed"

# Run unit tests only
test-unit:
	@echo "Running unit tests..."
	source venv/bin/activate && pytest tests/unit/ -v --cov=src/grant_ai --cov-report=term-missing
	@echo "Unit tests completed"

# Run integration tests only
test-integration:
	@echo "Running integration tests..."
	source venv/bin/activate && pytest tests/integration/ -v --cov=src/grant_ai --cov-report=term-missing
	@echo "Integration tests completed"

# Run end-to-end tests only
test-e2e:
	@echo "Running end-to-end tests..."
	source venv/bin/activate && pytest tests/e2e/ -v
	@echo "End-to-end tests completed"

# Run all quality checks
check: format lint typecheck security test-unit
	@echo "All quality checks completed"

# Build the package
build:
	@echo "Building package..."
	python -m build
	@echo "Package built successfully"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -f .coverage
	rm -f coverage.xml
	rm -f bandit-report.json
	@echo "Build artifacts cleaned"

# Run the application
run:
	@echo "Running Grant AI application..."
	python -m grant_ai.core.cli

# Launch the GUI
gui:
	@echo "Launching Grant AI GUI..."
	python -m grant_ai.gui.qt_app

# Generate documentation
docs:
	@echo "Generating documentation..."
	cd docs && make html
	@echo "Documentation generated"

# Create a new release
release:
	@echo "Creating a new release..."
	@read -p "Enter version number (e.g., 1.0.1): " version; \
	git tag -a v$$version -m "Release v$$version"; \
	git push origin v$$version; \
	echo "Release v$$version created and pushed"

# Database operations
db-init:
	@echo "Initializing database..."
	python scripts/init_db.py

db-migrate:
	@echo "Running database migrations..."
	python scripts/migrate_grants.py

# Data operations
data-import:
	@echo "Importing sample data..."
	python scripts/generate_sample_data.py

data-export:
	@echo "Exporting data..."
	python scripts/export_data.py

# Development utilities
dev-setup: setup
	@echo "Setting up development environment..."
	pre-commit install
	@echo "Development environment setup complete"

dev-reset: clean
	@echo "Resetting development environment..."
	rm -rf venv/
	@echo "Development environment reset. Run 'make setup' to recreate."

# Docker operations (if applicable)
docker-build:
	@echo "Building Docker image..."
	docker build -t grant-ai .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 grant-ai

# Performance testing
perf-test:
	@echo "Running performance tests..."
	source venv/bin/activate && pytest tests/performance/ -v

# Load testing
load-test:
	@echo "Running load tests..."
	python scripts/load_test.py

# Backup operations
backup:
	@echo "Creating backup..."
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/ reports/

# Restore operations
restore:
	@echo "Restoring from backup..."
	@read -p "Enter backup filename: " backup_file; \
	tar -xzf $$backup_file

# Monitoring and logging
logs:
	@echo "Showing application logs..."
	tail -f logs/app.log

# Health check
health:
	@echo "Running health check..."
	python scripts/health_check.py

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	pip install --upgrade pip
	pip install --upgrade -e ".[dev]"
	@echo "Dependencies updated"

# Generate requirements files
requirements:
	@echo "Generating requirements files..."
	pip freeze > requirements.txt
	pip freeze | grep -v "grant-ai" > requirements-prod.txt
	@echo "Requirements files generated"

# Code coverage report
coverage:
	@echo "Generating coverage report..."
	source venv/bin/activate && pytest tests/ --cov=src/grant_ai --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

# Security audit
audit:
	@echo "Running security audit..."
	safety check
	bandit -r src/ -f json -o bandit-report.json
	@echo "Security audit completed"

# Documentation
docs-serve:
	@echo "Serving documentation..."
	cd docs/_build/html && python -m http.server 8000

# Clean all
clean-all: clean
	@echo "Cleaning all artifacts..."
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	@echo "All artifacts cleaned"
