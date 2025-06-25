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
- 📊 **Grant Database**: Comprehensive database of grant opportunities
- 🎯 **Smart Matching**: Algorithms to match organizations with suitable grants
- 📝 **Application Management**: Streamlined application process and tracking
- 📈 **Analytics & Reporting**: Progress tracking and success metrics

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Install from source
```bash
git clone https://github.com/username/grant-ai.git
cd grant-ai
pip install -e .[dev]
```

## Usage

### Command Line Interface
```bash
# Research AI companies
grant-ai research companies --focus education

# Search for grants
grant-ai search grants --category education --amount 50000

# Generate organization profile
grant-ai profile create --org CODA

# Match grants to organization
grant-ai match --org CODA --output report.xlsx
```

### Python API
```python
from grant_ai import OrganizationProfile, GrantResearcher

# Create organization profile
coda = OrganizationProfile(
    name="CODA",
    focus_areas=["music education", "art education", "robotics"],
    program_types=["after-school", "summer camps"]
)

# Research grants
researcher = GrantResearcher()
matches = researcher.find_matches(coda, min_amount=10000, max_amount=100000)

# Generate report
researcher.generate_report(matches, output_file="coda_grants.xlsx")
```

## Project Structure

```
grant-ai/
├── src/grant_ai/           # Main package source code
│   ├── models/            # Data models (organizations, grants, companies)
│   ├── scrapers/          # Web scraping modules
│   ├── analysis/          # AI company analysis algorithms
│   ├── matching/          # Grant-organization matching logic
│   ├── reports/           # Report generation
│   └── cli/               # Command line interface
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docs/                  # Documentation
├── data/                  # Data files (gitignored)
└── config/                # Configuration files
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
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/grant_ai --cov-report=html

# Run specific test categories
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only
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

## Data Sources

The system collects data from various sources:
- Foundation databases (Candid, etc.)
- AI company websites and press releases
- Government grant databases
- Industry publications
- Social media monitoring

## Configuration

Create a `.env` file in the project root:
```env
# Database configuration
DATABASE_URL=sqlite:///data/grants.db

# API keys (if needed)
FOUNDATION_API_KEY=your_api_key_here

# Scraping settings
USER_AGENT=grant-ai-bot/1.0
REQUEST_DELAY=1.0
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality checks pass
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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
