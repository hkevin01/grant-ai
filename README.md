# Grant Research AI

[![CI/CD Pipeline](https://github.com/username/grant-ai/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/username/grant-ai/actions)
[![Code Coverage](https://codecov.io/gh/username/grant-ai/branch/main/graph/badge.svg)](https://codecov.io/gh/username/grant-ai)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Status](https://img.shields.io/badge/status-production--ready-green.svg)]()

An AI-powered system for researching and managing grant applications for non-profit organizations. **Production-ready** with enhanced stability, threading-based GUI operations, and comprehensive grant discovery capabilities.

## ✅ Current Status (July 2025)

**🎉 Production Ready!** All major issues resolved:
- ✅ **Crash-Free Operation**: GUI threading prevents VS Code force quits
- ✅ **Enhanced Scrapers**: Robust WV Department of Education and foundation grant discovery  
- ✅ **Organized Codebase**: Professional project structure with comprehensive testing
- ✅ **Performance Analysis**: Built-in system monitoring and improvement recommendations

## 🚀 Features

- 🔍 **AI Company Research**: Automated research and filtering of AI companies with grant programs
- 🤖 **AI-Powered Grant Discovery**: Intelligent agent that searches the web for new grant opportunities
- 🏔️ **West Virginia Grant Sources**: Specialized scrapers for WV state government and foundation grants
- 📊 **Grant Database**: Comprehensive database of grant opportunities
- 🎯 **Smart Matching**: Algorithms to match organizations with suitable grants
- 📝 **Application Management**: Streamlined application process and tracking
- 📈 **Analytics & Reporting**: Progress tracking and success metrics
- 🔄 **Auto-Fill Search**: Automatically populate search fields based on organization profile
- 📋 **Search Descriptions**: Natural language descriptions of what the search is looking for

## 🎯 Target Organizations

### CODA
- **Focus**: Education programs in music, art, and robotics
- **Programs**: After-school programs and summer camps

### Christian Pocket Community/NRG Development
- **Focus**: Affordable, efficient housing for retired people
- **Additional Support**: Housing for struggling single mothers and others in need

## 📋 Requirements

- Python 3.9 or higher
- pip package manager
- Git

## 🛠️ Installation

### Quick Start (Recommended)

```bash
# Clone the repository
git clone https://github.com/username/grant-ai.git
cd grant-ai

# Set up development environment (includes virtual environment and dependencies)
make setup

# Run quality checks
make check

# Launch the application
make run
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/username/grant-ai.git
cd grant-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build and run individual container
docker build -t grant-ai .
docker run -p 8000:8000 grant-ai
```

## 🚀 Usage

### Command Line Interface

```bash
# System Analysis & Health Check
./run.sh analyze-performance    # Analyze system and get improvement recommendations

# Setup and Launch
./run.sh setup                  # First-time setup
./run.sh load-data             # Load sample data
./run.sh gui                   # Launch GUI application

# Grant Research
./run.sh cli research          # Command-line grant research
./run.sh demo-search           # Enhanced search demonstration

# Testing and Validation
./run.sh test                  # Run all tests
./run.sh test-integration      # Integration tests
./run.sh lint                  # Code quality checks

# Advanced Commands
./run.sh setup-ai              # Setup AI features
./run.sh gui-enhanced          # Launch enhanced GUI with AI
./run.sh test-ai               # Test AI functionality
```

### Original CLI Interface (Advanced)

```bash
# Create organization profile
grant-ai profile create --name "Your Org" --focus-area education

# View existing profiles
grant-ai profile show data/profiles/coda_profile.json

# Comprehensive Grant Search (AI + Location-specific)
grant-ai discover comprehensive data/profiles/coda_profile.json --state "West Virginia" --limit 10
grant-ai discover comprehensive data/profiles/coda_profile.json --state "All States" --limit 20

# Research AI companies
grant-ai research research-companies --focus education

# Match grants to organization
grant-ai match grants data/profiles/coda_profile.json

# Match companies to organization
grant-ai match companies data/profiles/coda_profile.json

# Launch GUI with comprehensive search
grant-ai gui
```

### Python API

```python
from grant_ai import OrganizationProfile, GrantResearcher

# Create organization profile
coda = OrganizationProfile(
    name="CODA",
    focus_areas=["music_education", "art_education", "robotics"],
    program_types=["after_school", "summer_camps"]
)

# Research grants
researcher = GrantResearcher()
matches = researcher.find_matches(coda, min_amount=10000, max_amount=100000)

# Generate report
researcher.generate_report(matches, output_file="coda_grants.xlsx")
```

## 🖥️ GUI Usage

Two GUI options are available for interactive grant search and management:

### PyQt5 GUI (Recommended)
A native desktop application with full functionality:

```bash
# Launch via CLI command
python -m grant_ai.core.cli gui

# Or launch directly
python -m grant_ai.gui.qt_app

# Or use the launcher script
python scripts/launchers/launch_gui.py

# Or use make command
make gui
```

The PyQt5 GUI provides:
- **Organization Profile Management**: Load, edit, and save organization profiles
- **Comprehensive Grant Search**: Single button that combines AI agent and location-specific scrapers
- **Location Selection**: Country and state dropdowns (USA/West Virginia defaults)
- **Auto-Fill Search Fields**: Automatically populate search criteria based on organization profile
- **Search Descriptions**: Natural language descriptions of what the search is looking for
- **Grant Search**: Search grants by keywords, focus areas, amounts, and eligibility
- **Smart Suggestions**: Auto-suggest grants based on organization profile
- **Application Tracking**: Track application status and progress
- **Crash-Free Operation**: Robust error handling prevents system crashes

### Streamlit GUI (Alternative)
A web-based interface for basic functionality:

```bash
source venv/bin/activate
streamlit run src/grant_ai/gui/app.py
```

## 🏗️ Project Structure

```
grant-ai/
├── src/grant_ai/           # Main application code
│   ├── core/              # Core functionality (CLI, DB)
│   ├── config/            # Configuration management
│   ├── utils/             # Utility functions
│   ├── models/            # Data models
│   ├── analysis/          # Analysis and matching
│   ├── scrapers/          # Data collection
│   ├── services/          # Business logic services
│   └── gui/               # User interfaces
├── scripts/               # Utility scripts (organized)
│   ├── setup/            # Setup and installation scripts
│   ├── launchers/        # GUI and application launchers
│   └── fixes/            # Emergency fix scripts
├── tests/                 # Test suite (organized)
│   ├── integration/       # Integration and E2E tests
│   ├── scrapers/         # Scraper-specific tests
│   └── unit/             # Unit tests
├── data/                  # Data storage (organized)
│   ├── profiles/          # Organization profile files
│   ├── grants/            # Grant opportunities
│   ├── companies/         # AI company data
│   ├── applications/      # Application tracking
│   └── templates/         # Application templates
├── docs/                  # Documentation
├── reports/               # Generated reports
├── .github/               # GitHub workflows and templates
├── .copilot/              # Copilot configuration
└── docker-compose.yml     # Docker deployment
```

## 🧪 Development

### Development Setup

```bash
# Set up complete development environment
make setup

# Or use the development script
./scripts/dev.sh install
```

### Quality Assurance

```bash
# Run all quality checks
make check

# Run individual checks
make format      # Code formatting
make lint        # Linting
make typecheck   # Type checking
make security    # Security checks
```

### Testing

```bash
# Run all tests
make test

# Run specific test types
make test-unit           # Unit tests only
make test-integration    # Integration tests only
make test-e2e           # End-to-end tests only

# Run with coverage
make coverage
```

### Building and Deployment

```bash
# Build package
make build

# Clean build artifacts
make clean

# Generate documentation
make docs
```

### Docker Development

```bash
# Build development image
docker build --target development -t grant-ai:dev .

# Run with Docker Compose
docker-compose up -d

# Run tests in container
docker-compose exec grant-ai make test
```

## 📚 Documentation

- **[User Guide](docs/user_guide.md)** - Complete user documentation
- **[Technical Guide](docs/technical_guide.md)** - Technical implementation details
- **[API Reference](docs/api_reference.md)** - API documentation
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute
- **[Security Policy](SECURITY.md)** - Security and vulnerability reporting
- **[Project Goals](PROJECT_GOALS.md)** - Project purpose and objectives
- **[Development Workflow](WORKFLOW.md)** - Development processes and CI/CD
- **[Project Status](PROJECT_STATUS.md)** - Current status and roadmap

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes** and add tests
4. **Run quality checks**: `make check`
5. **Commit your changes**: Use conventional commits
6. **Push to your fork** and create a pull request

### Development Commands

```bash
# Set up development environment
make setup

# Run quality checks
make check

# Run tests
make test

# Format code
make format

# Build package
make build
```

## 🔒 Security

We take security seriously. Please report any security vulnerabilities to `security@grant-ai.org`.

- **Security Policy**: [SECURITY.md](SECURITY.md)
- **Vulnerability Reporting**: Email security@grant-ai.org
- **Security Scanning**: Automated with Bandit and Safety
- **Dependency Monitoring**: Regular security updates

## 📊 Quality Metrics

- **Test Coverage**: ≥80%
- **Type Coverage**: 100% for public APIs
- **Code Quality**: Zero linting errors
- **Security**: No critical vulnerabilities
- **Performance**: <2 second response times

## 🚀 Deployment

### Local Deployment

```bash
# Install and run
make setup
make run
```

### Docker Deployment

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Development deployment
docker-compose -f docker-compose.dev.yml up -d
```

### Cloud Deployment

Instructions for deploying to various cloud platforms are available in the [Deployment Guide](docs/deployment_guide.md).

## 📈 Roadmap

### Phase 3: Enhanced User Experience (Current)
- [ ] Modern GUI with improved UX
- [ ] Mobile-responsive web application
- [ ] Real-time notifications
- [ ] Advanced search and filtering

### Phase 4: Data Enhancement (Next)
- [ ] Real-time grant database updates
- [ ] Integration with major grant platforms
- [ ] Historical success rate data
- [ ] Predictive analytics

### Phase 5: Advanced AI Features (Future)
- [ ] Natural language processing
- [ ] Automated application generation
- [ ] Success probability scoring
- [ ] Intelligent deadline management

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Contributors**: All contributors who have helped build this project
- **Open Source**: Built on the shoulders of many open source projects
- **Community**: The non-profit community for feedback and guidance

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/username/grant-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/grant-ai/discussions)
- **Email**: contact@grant-ai.org

## 🏆 Status

**Current Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: January 2024  

This project has undergone comprehensive modernization and is now following industry best practices for development, testing, security, and deployment.

---

**Made with ❤️ for the non-profit community**
