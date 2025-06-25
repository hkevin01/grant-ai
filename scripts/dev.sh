#!/bin/bash
# Development utilities for Grant AI project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if command_exists pytest; then
        pytest tests/ -v --cov=src/grant_ai --cov-report=term-missing
    else
        print_error "pytest not found. Install with: pip install pytest pytest-cov"
        exit 1
    fi
}

# Function to format code
format_code() {
    print_status "Formatting code..."
    
    if command_exists black; then
        black src/ tests/ scripts/
        print_status "Code formatted with black"
    else
        print_warning "black not found. Install with: pip install black"
    fi
    
    if command_exists isort; then
        isort src/ tests/ scripts/
        print_status "Imports sorted with isort"
    else
        print_warning "isort not found. Install with: pip install isort"
    fi
}

# Function to run linting
run_lint() {
    print_status "Running linting..."
    
    if command_exists flake8; then
        flake8 src/ tests/
        print_status "Linting completed with flake8"
    else
        print_warning "flake8 not found. Install with: pip install flake8"
    fi
}

# Function to run type checking
run_typecheck() {
    print_status "Running type checking..."
    
    if command_exists mypy; then
        mypy src/
        print_status "Type checking completed with mypy"
    else
        print_warning "mypy not found. Install with: pip install mypy"
    fi
}

# Function to run all quality checks
run_quality_checks() {
    print_status "Running all quality checks..."
    format_code
    run_lint
    run_typecheck
    run_tests
    print_status "All quality checks completed!"
}

# Function to set up development environment
setup_dev() {
    print_status "Setting up development environment..."
    
    # Check Python version
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "Python version: $python_version"
    
    # Install package in development mode
    pip install -e .[dev]
    
    # Install pre-commit hooks if available
    if command_exists pre-commit; then
        pre-commit install
        print_status "Pre-commit hooks installed"
    fi
    
    # Generate sample data
    python3 scripts/generate_sample_data.py
    
    print_status "Development environment setup complete!"
}

# Function to build documentation
build_docs() {
    print_status "Building documentation..."
    
    if command_exists sphinx-build; then
        sphinx-build -b html docs/ docs/_build/html
        print_status "Documentation built successfully"
        print_status "Open docs/_build/html/index.html to view"
    else
        print_warning "sphinx not found. Install with: pip install sphinx sphinx-rtd-theme"
    fi
}

# Function to clean up temporary files
clean() {
    print_status "Cleaning up temporary files..."
    
    # Remove Python cache files
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    
    # Remove test artifacts
    rm -rf .pytest_cache/
    rm -rf htmlcov/
    rm -f .coverage
    
    # Remove build artifacts
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    
    print_status "Cleanup completed!"
}

# Function to create release
create_release() {
    local version=$1
    if [ -z "$version" ]; then
        print_error "Please provide a version number: ./dev.sh release v1.0.0"
        exit 1
    fi
    
    print_status "Creating release $version..."
    
    # Run quality checks first
    run_quality_checks
    
    # Build package
    python3 -m build
    
    print_status "Release $version created successfully!"
    print_status "Distribution files are in dist/"
}

# Function to update dependencies
update_deps() {
    print_status "Updating dependencies..."
    
    # Update pip
    pip install --upgrade pip
    
    # Update package dependencies
    pip install --upgrade -e .[dev]
    
    print_status "Dependencies updated!"
}

# Main script logic
case "$1" in
    "test")
        run_tests
        ;;
    "format")
        format_code
        ;;
    "lint")
        run_lint
        ;;
    "typecheck")
        run_typecheck
        ;;
    "check")
        run_quality_checks
        ;;
    "setup")
        setup_dev
        ;;
    "docs")
        build_docs
        ;;
    "clean")
        clean
        ;;
    "release")
        create_release "$2"
        ;;
    "update")
        update_deps
        ;;
    *)
        echo "Grant AI Development Utilities"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  test       Run tests with coverage"
        echo "  format     Format code with black and isort"
        echo "  lint       Run flake8 linting"
        echo "  typecheck  Run mypy type checking"
        echo "  check      Run all quality checks"
        echo "  setup      Set up development environment"
        echo "  docs       Build documentation"
        echo "  clean      Clean up temporary files"
        echo "  release    Create a release (requires version)"
        echo "  update     Update dependencies"
        echo ""
        echo "Examples:"
        echo "  $0 check"
        echo "  $0 release v1.0.0"
        echo "  $0 setup"
        exit 1
        ;;
esac
