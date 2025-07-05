# Directory Structure

This document describes the organization of the Grant AI project directory.

## Root Directory
- `run.sh` - Main script to run the application
- `README.md` - Main project documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security information
- `pyproject.toml` - Python project configuration
- `requirements-*.txt` - Python dependencies
- `Dockerfile` - Docker configuration
- `docker-compose.yml` - Docker compose configuration
- `Makefile` - Build and maintenance commands

## Source Code
- `src/` - Main source code directory
  - `grant_ai/` - Core application package
    - `core/` - Core functionality
    - `gui/` - GUI components
    - `models/` - Data models
    - `analysis/` - Grant analysis tools
    - `services/` - Service layer

## Tests
- `tests/` - Automated test suite
  - `unit/` - Unit tests
  - `integration/` - Integration tests

## Documentation
- `docs/` - Documentation files
  - `project/` - Project status and integration documentation
    - `AGENT_INTEGRATION_SUMMARY.md`
    - `ALL_ISSUES_RESOLVED.md`
    - `INTEGRATION_COMPLETE.md`
    - `ISSUE_RESOLVED.md`
  - `fixes/` - Bug fix documentation
    - `ATTRIBUTEERROR_FIX.md`
    - `COMPLETE_FIXES_SUMMARY.md`
    - `ENHANCEMENTS_SUMMARY.md`
    - `ENHANCEMENT_SUMMARY.md`
  - `CHANGELOG.md` - Change history

## Scripts
- `scripts/` - Utility scripts and tools
  - `setup/` - Setup and configuration scripts
  - `testing/` - Test scripts and validation tools
    - `test_*.py` - Various test scripts
    - `validate_integration.py` - Integration validation
  - `utils/` - Utility scripts
    - `demo_enhanced_scraping.py` - Scraping demonstration
    - `launch_enhanced_gui.py` - Enhanced GUI launcher
    - `setup_ai.py` - AI features setup
    - `emergency_fix_vscode.py` - Emergency fixes
    - `urgent_vscode_fix.py` - Urgent fixes

## Data and Output
- `data/` - Application data files
- `reports/` - Generated reports
- `htmlcov/` - Test coverage reports

## Build and Cache
- `.pytest_cache/` - Pytest cache
- `.ruff_cache/` - Ruff linter cache
- `venv/` - Python virtual environment
- `.coverage` - Coverage data
- `coverage.xml` - Coverage XML report

## Configuration
- `.github/` - GitHub workflows and configurations
- `.vscode/` - VS Code configuration
- `.copilot/` - GitHub Copilot configuration
- `.gitignore` - Git ignore rules
- `.editorconfig` - Editor configuration
- `.pre-commit-config.yaml` - Pre-commit hooks
