#!/bin/bash

# Grant AI - Run Script
# This script provides easy access to the Grant AI application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}        GRANT AI RUNNER         ${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  help                    Show this help message"
    echo "  setup                   Setup the environment (install dependencies)"
    echo "  setup-ai                Setup AI features and models"
    echo "  load-data               Load sample data into the system"
    echo "  cli [command]           Run CLI commands"
    echo "  gui                     Launch the basic GUI application"
    echo "  gui-enhanced            Launch enhanced GUI with AI features"
    echo "  test                    Run all tests"
    echo "  test-unit               Run unit tests only"
    echo "  test-integration        Run integration tests only"
    echo "  test-comprehensive      Run comprehensive test suite"
    echo "  test-enhanced           Run enhanced test suite with detailed reporting"
    echo "  test-ai                 Test AI features"
    echo "  demo-search             Run enhanced search demo"
    echo "  analyze-performance     Analyze system performance and generate recommendations"
    echo "  validate-integration    Validate the integration of new features"
    echo "  lint                    Run linter checks"
    echo "  format                  Format code with black"
    echo "  clean                   Clean up temporary files"
    echo ""
    echo "CLI Examples:"
    echo "  $0 cli --help           Show CLI help"
    echo "  $0 cli research         Research grants"
    echo "  $0 cli questionnaire    Manage questionnaires"
    echo "  $0 cli template         Manage templates"
    echo "  $0 cli tracking         Manage tracking"
    echo "  $0 cli report           Generate reports"
    echo ""
    echo "Examples:"
    echo "  $0 setup                # First time setup"
    echo "  $0 load-data            # Load sample data"
    echo "  $0 cli research         # Research grants"
    echo "  $0 gui                  # Launch GUI"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run '$0 setup' first."
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        print_error "Virtual environment not found. Run '$0 setup' first."
        exit 1
    fi
}

# Function to setup environment
setup_environment() {
    print_header
    print_status "Setting up Grant AI environment..."
    
    # Check if Python 3.8+ is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed."
        exit 1
    fi
    
    # Create virtual environment
    print_status "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    activate_venv
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing dependencies..."
    pip install -e .
    
    # Install development dependencies
    print_status "Installing development dependencies..."
    pip install pytest pytest-cov ruff flake8 black
    
    print_status "Setup complete! You can now run:"
    echo "  $0 load-data    # Load sample data"
    echo "  $0 cli --help   # See available CLI commands"
    echo "  $0 gui          # Launch GUI"
}

# Function to load sample data
load_sample_data() {
    print_header
    print_status "Loading sample data..."
    
    check_venv
    activate_venv
    
    python -m grant_ai.core.cli load-sample-data
}

# Function to run CLI commands
run_cli() {
    print_header
    print_status "Running CLI command: $*"
    
    check_venv
    activate_venv
    
    python -m grant_ai.core.cli "$@"
}

# Function to run GUI
run_gui() {
    print_header
    print_status "Launching GUI..."
    
    check_venv
    activate_venv
    
    # Check if GUI dependencies are available
    if ! python -c "import PyQt5" 2>/dev/null; then
        print_warning "PyQt5 not found. Installing GUI dependencies..."
        pip install PyQt5
    fi
    
    python -m grant_ai.gui.qt_app
}

# Function to run tests
run_tests() {
    print_header
    print_status "Running tests..."
    
    check_venv
    activate_venv
    
    if [ "$1" = "unit" ]; then
        print_status "Running unit tests..."
        python -m pytest tests/unit/ -v --cov=src/grant_ai --cov-report=html
    elif [ "$1" = "integration" ]; then
        print_status "Running integration tests..."
        python -m pytest tests/integration/ -v
    else
        print_status "Running all tests..."
        python -m pytest tests/ -v --cov=src/grant_ai --cov-report=html
    fi
}

# Function to run comprehensive tests
run_comprehensive_tests() {
    print_header
    print_status "Running comprehensive test suite..."
    
    check_venv
    activate_venv
    
    python tests/test_comprehensive.py
}

# Function to run enhanced tests
run_enhanced_tests() {
    print_header
    print_status "Running enhanced test suite with detailed reporting..."
    
    check_venv
    activate_venv
    
    python tests/test_runner.py --test-type all --output-file test_results.txt
    
    if [ -f "test_results.txt" ]; then
        print_status "Test results saved to test_results.txt"
        cat test_results.txt
    fi
}

# Function to validate integration
validate_integration() {
    print_header
    print_status "Validating integration of new features..."
    
    check_venv
    activate_venv
    
    python validate_integration.py
}

# Function to run linter
run_lint() {
    print_header
    print_status "Running linter checks..."
    
    check_venv
    activate_venv
    
    print_status "Running ruff..."
    ruff check src/ tests/
    
    print_status "Running flake8..."
    flake8 src/ tests/
    
    print_status "Linting complete!"
}

# Function to format code
format_code() {
    print_header
    print_status "Formatting code..."
    
    check_venv
    activate_venv
    
    print_status "Running black..."
    black src/ tests/
    
    print_status "Code formatting complete!"
}

# Function to clean up
clean_up() {
    print_header
    print_status "Cleaning up temporary files..."
    
    # Remove Python cache files
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    
    # Remove test cache
    rm -rf .pytest_cache/
    rm -rf .coverage
    rm -rf htmlcov/
    
    # Remove temporary files
    rm -rf *.tmp
    rm -rf *.log
    
    print_status "Cleanup complete!"
}

# Function to setup AI features
setup_ai() {
    print_status "Setting up AI features..."
    
    if [[ ! -f "requirements-ai.txt" ]]; then
        print_error "requirements-ai.txt not found!"
        return 1
    fi
    
    python scripts/setup/setup_ai.py
    
    if [[ $? -eq 0 ]]; then
        print_status "AI features setup completed successfully!"
    else
        print_warning "AI setup completed with some issues. Basic functionality should still work."
    fi
}

# Function to launch enhanced GUI
launch_enhanced_gui() {
    print_status "Launching Enhanced Grant AI GUI with AI features..."
    
    if [[ ! -f "launch_enhanced_gui.py" ]]; then
        print_warning "Enhanced GUI not available, launching basic GUI..."
        launch_gui
        return
    fi
    
    python launch_enhanced_gui.py
}

# Function to test AI features
test_ai() {
    print_status "Testing AI features..."
    
    python -c "
from grant_ai.services.ai_assistant import AIAssistant
from grant_ai.services.robust_scraper import RobustWebScraper

# Test AI Assistant
ai = AIAssistant()
print(f'AI Assistant Available: {ai.is_available()}')
print(f'AI Status: {ai.get_status()}')

# Test Robust Scraper
scraper = RobustWebScraper()
health = scraper.health_check()
print(f'Scraper Health: {health}')

print('✅ AI feature tests completed')
"
}

# Function to run enhanced search demo
demo_enhanced_search() {
    print_status "Running enhanced search demo..."
    
    python -c "
import sys
sys.path.insert(0, 'src')

from grant_ai.models import OrganizationProfile
from grant_ai.services.ai_assistant import AIAssistant

# Create sample organization
org = OrganizationProfile(
    organization_name='Demo Organization',
    organization_type='nonprofit',
    mission_statement='Providing education and support for community development',
    target_beneficiaries='low-income families, students',
    funding_priorities='education, community development, youth programs'
)

# Test AI features
ai = AIAssistant()
print('AI Assistant Status:', ai.is_available())

if ai.is_available():
    terms = ai.suggest_search_terms(org)
    print('Suggested search terms:', terms[:5])
    
    suggestions = ai.auto_fill_suggestions('mission statement', org)
    print('Auto-fill suggestions:', suggestions)

print('✅ Enhanced search demo completed')
"
}

# Function to analyze system performance
analyze_performance() {
    print_status "Analyzing system performance..."
    check_venv
    activate_venv
    
    python scripts/analyze_performance.py
}

# Main script logic
main() {
    case "${1:-gui}" in
        "help"|"-h"|"--help")
            show_help
            ;;
        "setup")
            setup_environment
            ;;
        "setup-ai")
            setup_ai
            ;;
        "load-data")
            load_sample_data
            ;;
        "cli")
            shift
            run_cli "$@"
            ;;
        "gui")
            run_gui
            ;;
        "gui-enhanced")
            launch_enhanced_gui
            ;;
        "test")
            run_tests
            ;;
        "test-unit")
            run_tests unit
            ;;
        "test-integration")
            run_tests integration
            ;;
        "test-comprehensive")
            run_comprehensive_tests
            ;;
        "test-enhanced")
            run_enhanced_tests
            ;;
        "test-ai")
            test_ai
            ;;
        "demo-search")
            demo_enhanced_search
            ;;
        "analyze-performance")
            analyze_performance
            ;;
        "validate-integration")
            validate_integration
            ;;
        "lint")
            run_lint
            ;;
        "format")
            format_code
            ;;
        "clean")
            clean_up
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"