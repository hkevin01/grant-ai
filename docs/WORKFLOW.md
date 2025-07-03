# Development Workflow

This document outlines the development workflow, branching strategies, and CI/CD processes for the Grant AI project.

## Branching Strategy

We follow a modified Git Flow approach:

### Main Branches
- `main` - Production-ready code
- `develop` - Integration branch for features

### Supporting Branches
- `feature/*` - New features (branch from `develop`)
- `bugfix/*` - Bug fixes (branch from `develop`)
- `hotfix/*` - Critical production fixes (branch from `main`)
- `release/*` - Release preparation (branch from `develop`)

### Branch Naming Convention
```
feature/user-authentication
bugfix/grant-search-crash
hotfix/security-vulnerability
release/v1.2.0
```

## Development Process

### 1. Feature Development
1. Create feature branch from `develop`
2. Implement feature with tests
3. Run quality checks locally
4. Create pull request to `develop`
5. Code review and approval
6. Merge to `develop`

### 2. Bug Fixes
1. Create bugfix branch from `develop`
2. Fix the issue with tests
3. Run quality checks
4. Create pull request
5. Code review and approval
6. Merge to `develop`

### 3. Release Process
1. Create release branch from `develop`
2. Update version numbers
3. Update CHANGELOG.md
4. Final testing
5. Merge to `main` and `develop`
6. Create release tag

## CI/CD Pipeline

### Automated Checks
Our GitHub Actions workflow runs on every push and pull request:

1. **Code Quality**
   - Linting with Ruff
   - Type checking with MyPy
   - Code formatting with Black
   - Import sorting with isort

2. **Testing**
   - Unit tests with pytest
   - Coverage reporting
   - Integration tests
   - End-to-end tests

3. **Security**
   - Dependency vulnerability scanning
   - Code security analysis

### Quality Gates
All checks must pass before merging:
- ✅ All tests passing
- ✅ Code coverage ≥ 80%
- ✅ No linting errors
- ✅ No type checking errors
- ✅ Security scan clean

## Code Review Process

### Pull Request Requirements
- [ ] Descriptive title and description
- [ ] All CI checks passing
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

### Review Checklist
- [ ] Code follows project standards
- [ ] Tests are comprehensive
- [ ] Documentation is clear
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Development Environment Setup

### Prerequisites
- Python 3.9+
- Git
- Docker (optional)

### Local Setup
```bash
# Clone repository
git clone https://github.com/username/grant-ai.git
cd grant-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run quality checks
./scripts/dev.sh check
```

### Pre-commit Hooks
We use pre-commit hooks to ensure code quality:
- Black formatting
- Ruff linting
- isort import sorting
- MyPy type checking

## Testing Strategy

### Test Types
1. **Unit Tests** - Test individual functions and classes
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete user workflows

### Test Organization
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
└── conftest.py    # Test configuration
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=src/grant_ai --cov-report=html
```

## Deployment

### Environments
- **Development** - For feature testing
- **Staging** - For integration testing
- **Production** - Live application

### Deployment Process
1. Code merged to `main`
2. Automated tests pass
3. Security scan completed
4. Manual approval (if required)
5. Deployment to staging
6. Smoke tests
7. Deployment to production

## Monitoring and Maintenance

### Health Checks
- Application health endpoints
- Database connectivity
- External API status

### Logging
- Structured logging with correlation IDs
- Error tracking and alerting
- Performance monitoring

### Maintenance Tasks
- Dependency updates
- Security patches
- Performance optimization
- Documentation updates

## Communication

### Team Communication
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Pull requests for code reviews
- Release notes for changes

### Stakeholder Communication
- Regular status updates
- Feature demos
- Performance reports
- Security advisories

## Tools and Services

### Development Tools
- **IDE**: VS Code with Python extension
- **Version Control**: Git with GitHub
- **CI/CD**: GitHub Actions
- **Testing**: pytest, coverage
- **Code Quality**: Ruff, Black, MyPy
- **Documentation**: Sphinx, ReadTheDocs

### External Services
- **Package Registry**: PyPI
- **Documentation**: ReadTheDocs
- **Security**: GitHub Security Advisories
- **Monitoring**: Application monitoring tools

## Best Practices

### Code Standards
- Follow PEP 8 style guide
- Use type hints
- Write docstrings
- Keep functions small and focused
- Use meaningful variable names

### Git Practices
- Write clear commit messages
- Use conventional commits
- Keep commits atomic
- Rebase before merging

### Security
- Never commit secrets
- Use environment variables
- Regular dependency updates
- Security code reviews

### Performance
- Profile code regularly
- Optimize database queries
- Use caching where appropriate
- Monitor resource usage 