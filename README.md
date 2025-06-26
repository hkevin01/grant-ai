# Grant Research AI

An AI-powered system for researching and managing grant applications for non-profit organizations.

## Overview

This project helps non-profit organizations streamline their grant research and application process by:
- Researching AI companies and their grant programs
- Filtering opportunities based on organizational focus and needs
- Managing application processes and tracking progress
- Generating reports and insights

## Target Organizations

### CODA
- **Focus**: Education programs in music, art, and robotics
- **Programs**: After-school programs and summer camps

### Christian Pocket Community/NRG Development
- **Focus**: Affordable, efficient housing for retired people
- **Additional Support**: Housing for struggling single mothers and others in need

## Features

- 🔍 **AI Company Research**: Automated research and filtering of AI companies with grant programs
- 🤖 **AI-Powered Grant Discovery**: Intelligent agent that searches the web for new grant opportunities
- 🏔️ **West Virginia Grant Sources**: Specialized scrapers for WV state government and foundation grants
- 📊 **Grant Database**: Comprehensive database of grant opportunities
- 🎯 **Smart Matching**: Algorithms to match organizations with suitable grants
- 📝 **Application Management**: Streamlined application process and tracking
- 📈 **Analytics & Reporting**: Progress tracking and success metrics
- 🔄 **Auto-Fill Search**: Automatically populate search fields based on organization profile
- 📋 **Search Descriptions**: Natural language descriptions of what the search is looking for

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Install from source
```bash
git clone https://github.com/username/grant-ai.git
cd grant-ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

## Usage

### Command Line Interface
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

## GUI Usage

Two GUI options are available for interactive grant search and management:

### PyQt5 GUI (Recommended)
A native desktop application with full functionality:

```bash
# Launch via CLI command
python -m grant_ai.core.cli gui

# Or launch directly
python -m grant_ai.gui.qt_app

# Or use the launcher script
python launch_gui.py
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

**Quick Start with PyQt5 GUI:**
1. Launch the GUI: `python -m grant_ai.core.cli gui`
2. Go to "Organization Profile" tab
3. Select "Coda Mountain Academy" from the dropdown
4. The profile will load automatically and auto-fill search fields
5. Switch to "Grant Search" tab to see:
   - Search description explaining what you're looking for
   - Auto-filled search fields based on the profile
   - Location dropdowns (Country: USA, State: West Virginia)
   - Use "🔍 Comprehensive Grant Search" to find opportunities from all sources

### Streamlit GUI (Alternative)
A web-based interface for basic functionality:

```bash
source venv/bin/activate
streamlit run src/grant_ai/gui/app.py
```

This GUI allows you to:
- Load or create an organization profile
- Search for grants using state/federal scrapers
- View and interact with results

## Project Structure

```
grant-ai/
├── data/                          # Data storage
│   ├── profiles/                  # Organization profiles
│   │   └── coda_profile.json      # Example profile for CODA
│   ├── grants/                    # Grant opportunities
│   ├── companies/                 # AI company data
│   ├── applications/              # Application tracking
│   └── templates/                 # Application templates
├── src/grant_ai/                  # Source code
│   ├── core/                      # Core functionality
│   │   ├── cli.py                 # Command-line interface
│   │   └── db.py                  # Database operations
│   ├── config/                    # Configuration management
│   ├── utils/                     # Utility functions
│   ├── models/                    # Data models
│   ├── analysis/                  # Analysis and matching
│   ├── scrapers/                  # Data collection
│   └── gui/                       # User interfaces
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
├── scripts/                       # Development scripts
└── docs/                          # Documentation
```

## Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/username/grant-ai.git
cd grant-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .

# Run development tools
./scripts/dev.sh check     # Run all quality checks
./scripts/dev.sh test      # Run test suite
./scripts/dev.sh format    # Format code
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/grant_ai --cov-report=html

# Run specific test categories
pytest tests/unit/         # Unit tests only
pytest tests/integration/  # Integration tests only
pytest tests/e2e/          # End-to-end tests only
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

## Data Management

### Sample Data
The project includes sample data for testing and demonstration:
- **Organization Profiles**: CODA and NRG Development profiles
- **Grant Opportunities**: 4 sample grants with various focus areas
- **AI Companies**: 4 major AI companies with grant programs

### Data Sources
The system collects data from various sources:
- **AI-Powered Web Search**: Intelligent agents search the web for new grant opportunities
- **West Virginia State Sources**: WV Arts Commission, Department of Education, Commerce, and Health
- **Federal Sources**: Grants.gov API, USAspending.gov
- **Foundation Sources**: Benedum Foundation, Candid, Foundation Center
- **AI Company Sources**: Company websites and press releases
- **Government Databases**: State and federal grant databases
- **Industry Publications**: Grant announcements and funding news

## Configuration

The system uses centralized configuration in `src/grant_ai/config/`:
- Database settings
- API endpoints and keys
- File paths and directories
- Default values

Environment variables can be set for sensitive configuration:
```bash
export GRANT_AI_DB_URL="sqlite:///data/grants.db"
export GRANTS_GOV_API_KEY="your_api_key_here"
```

## Current Status

### ✅ Completed (Phases 1-4)
- Core infrastructure and data models
- CLI interface with profile management
- Grant research and matching algorithms
- Basic GUI (Streamlit and PyQt)
- Grants.gov API scraper
- Unit tests for core modules
- **AI-Powered Grant Discovery**: Intelligent agents for finding new grant opportunities
- **West Virginia Grant Sources**: Specialized scrapers for WV state and foundation grants
- **Auto-Fill Search**: Automatically populate search fields based on organization profiles
- **Search Descriptions**: Natural language descriptions of search criteria
- Application management system
- Questionnaire system for organization profiling
- Grant application templates
- Application tracking and reporting

### 🔄 In Progress (Phase 5)
- Enhanced AI agent capabilities
- Additional grant source integrations
- Advanced matching algorithms
- Performance optimizations

### 📋 Next Steps (Phase 6)
- Testing with real organization data
- User interface improvements
- Documentation and user guides
- Production deployment

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality checks pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the non-profit organizations providing requirements and feedback
- Built with Python and various open-source libraries
- Inspired by the need to democratize access to grant funding

## Support

For questions or support:
- Create an issue on GitHub
- Contact the development team
- Check the documentation in the `docs/` directory

## Roadmap

See [project_plan.md](docs/project_plan.md) for detailed development roadmap and [project_progress.md](docs/project_progress.md) for current status.
