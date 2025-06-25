#!/usr/bin/env python3
"""
Setup script for Grant AI project.
Run this after cloning the repository to set up the development environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def main():
    """Set up the development environment."""
    print("Setting up Grant AI development environment...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Create necessary directories
    directories = [
        "data/raw",
        "data/processed", 
        "logs",
        "config",
        "tests/unit",
        "tests/integration"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Install the package in development mode
    try:
        run_command("pip install -e .[dev]")
        print("✅ Package installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install package")
        sys.exit(1)
    
    # Install pre-commit hooks
    try:
        run_command("pre-commit install")
        print("✅ Pre-commit hooks installed")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install pre-commit hooks (optional)")
    
    # Create sample configuration
    config_file = Path("config/config.yaml")
    if not config_file.exists():
        config_content = """# Grant AI Configuration
database:
  url: "sqlite:///data/grants.db"
  
scraping:
  user_agent: "grant-ai-bot/1.0"
  request_delay: 1.0
  max_retries: 3
  
logging:
  level: "INFO"
  file: "logs/grant_ai.log"
  
api_keys:
  # Add API keys here if needed
  # foundation_api_key: "your_key_here"
"""
        config_file.write_text(config_content)
        print(f"✅ Created sample configuration: {config_file}")
    
    # Create sample environment file
    env_file = Path(".env.example")
    if not env_file.exists():
        env_content = """# Grant AI Environment Variables
# Copy this file to .env and fill in your values

# Database URL
DATABASE_URL=sqlite:///data/grants.db

# API Keys (if needed)
# FOUNDATION_API_KEY=your_api_key_here
# CANDID_API_KEY=your_api_key_here

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/grant_ai.log

# Web Scraping
USER_AGENT=grant-ai-bot/1.0
REQUEST_DELAY=1.0
"""
        env_file.write_text(env_content)
        print(f"✅ Created environment template: {env_file}")
    
    # Run initial tests
    try:
        result = run_command("python -m pytest tests/ -v", check=False)
        if result.returncode == 0:
            print("✅ All tests passed")
        else:
            print("⚠️  Some tests failed (this might be expected for new setup)")
    except FileNotFoundError:
        print("⚠️  Tests not found (will be created as development progresses)")
    
    # Create sample data
    print("\nCreating sample organization profiles...")
    try:
        run_command("grant-ai examples")
        print("✅ Sample profiles created")
    except subprocess.CalledProcessError:
        print("⚠️  Could not create sample profiles")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and fill in your configuration")
    print("2. Review config/config.yaml and adjust as needed")
    print("3. Run 'grant-ai --help' to see available commands")
    print("4. Start developing with 'grant-ai examples' to see sample usage")
    
    print("\nUseful commands:")
    print("- grant-ai profile show coda_profile.json")
    print("- grant-ai match companies coda_profile.json")
    print("- pytest tests/ -v  # Run tests")
    print("- black src/ tests/  # Format code")
    print("- mypy src/  # Type checking")


if __name__ == "__main__":
    main()
