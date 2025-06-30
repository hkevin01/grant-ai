#!/bin/bash
# Development utilities for Grant AI project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
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

# Function to check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not activated. Please activate it first:"
        echo "source venv/bin/activate  # On Unix/macOS"
        echo "venv\\Scripts\\activate     # On Windows"
        exit 1
    fi
}

# Function to install dependencies
install_deps() {
    print_status "Installing dependencies..."
    pip install -e ".[dev]"
    print_success "Dependencies installed successfully"
}

# Function to run code formatting
format() {
    print_status "Running code formatting..."
    black src/ tests/ scripts/
    isort src/ tests/ scripts/
    print_success "Code formatting completed"
}

# Function to run linting
lint() {
    print_status "Running linting checks..."
    ruff check src/ tests/ scripts/
    print_success "Linting completed"
}

# Function to run type checking
typecheck() {
    print_status "Running type checking..."
    mypy src/
    print_success "Type checking completed"
}

# Function to run security checks
security() {
    print_status "Running security checks..."
    bandit -r src/ -f json -o bandit-report.json || true
    safety check
    print_success "Security checks completed"
}

# Function to run tests
test() {
    local test_type=${1:-all}
    
    case $test_type in
        "unit")
            print_status "Running unit tests..."
            pytest tests/unit/ -v --cov=src/grant_ai --cov-report=term-missing
            ;;
        "integration")
            print_status "Running integration tests..."
            pytest tests/integration/ -v --cov=src/grant_ai --cov-report=term-missing
            ;;
        "e2e")
            print_status "Running end-to-end tests..."
            pytest tests/e2e/ -v
            ;;
        "all")
            print_status "Running all tests..."
            pytest tests/ -v --cov=src/grant_ai --cov-report=term-missing --cov-report=html
            ;;
        *)
            print_error "Unknown test type: $test_type"
            echo "Available test types: unit, integration, e2e, all"
            exit 1
            ;;
    esac
    print_success "Tests completed"
}

# Function to run all quality checks
check() {
    print_status "Running all quality checks..."
    format
    lint
    typecheck
    security
    test unit
    print_success "All quality checks completed"
}

# Function to build the package
build() {
    print_status "Building package..."
    python -m build
    print_success "Package built successfully"
}

# Function to clean build artifacts
clean() {
    print_status "Cleaning build artifacts..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf htmlcov/
    rm -f .coverage
    rm -f coverage.xml
    rm -f bandit-report.json
    print_success "Build artifacts cleaned"
}

# Function to run the application
run() {
    print_status "Running Grant AI application..."
    python -m grant_ai.core.cli
}

# Function to run the GUI
gui() {
    print_status "Launching Grant AI GUI..."
    python launch_gui.py
}

# Function to generate documentation
docs() {
    print_status "Generating documentation..."
    cd docs
    make html
    cd ..
    print_success "Documentation generated"
}

# Function to show help
help() {
    echo "Grant AI Development Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  install     Install dependencies"
    echo "  format      Format code with Black and isort"
    echo "  lint        Run linting with Ruff"
    echo "  typecheck   Run type checking with MyPy"
    echo "  security    Run security checks with Bandit and Safety"
    echo "  test [type] Run tests (unit, integration, e2e, all)"
    echo "  check       Run all quality checks"
    echo "  build       Build the package"
    echo "  clean       Clean build artifacts"
    echo "  run         Run the application"
    echo "  gui         Launch the GUI"
    echo "  docs        Generate documentation"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install"
    echo "  $0 check"
    echo "  $0 test unit"
    echo "  $0 test all"
    echo "  $0 run"
}

# Main script logic
case ${1:-help} in
    "install")
        check_venv
        install_deps
        ;;
    "format")
        check_venv
        format
        ;;
    "lint")
        check_venv
        lint
        ;;
    "typecheck")
        check_venv
        typecheck
        ;;
    "security")
        check_venv
        security
        ;;
    "test")
        check_venv
        test $2
        ;;
    "check")
        check_venv
        check
        ;;
    "build")
        check_venv
        build
        ;;
    "clean")
        clean
        ;;
    "run")
        check_venv
        run
        ;;
    "gui")
        check_venv
        gui
        ;;
    "docs")
        check_venv
        docs
        ;;
    "help"|"--help"|"-h")
        help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac
