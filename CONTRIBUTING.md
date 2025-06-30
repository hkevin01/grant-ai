# Contributing to Grant AI

Thank you for your interest in contributing to Grant AI! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

### Our Pledge

We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone, regardless of age, body size, visible or invisible disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

Examples of behavior that contributes to a positive environment for our community include:

- Demonstrating empathy and kindness toward other people
- Being respectful of differing opinions, viewpoints, and experiences
- Giving and gracefully accepting constructive feedback
- Accepting responsibility and apologizing to those affected by our mistakes
- Focusing on what is best for the overall community

Examples of unacceptable behavior include:

- The use of sexualized language or imagery, and sexual attention or advances
- Trolling, insulting or derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account
- Basic knowledge of Python development

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/grant-ai.git
   cd grant-ai
   ```
3. **Set up the development environment** (see [Development Setup](#development-setup))
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Environment Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Run initial checks**:
   ```bash
   ./scripts/dev.sh check
   ```

### IDE Setup

We recommend using VS Code with the following extensions:
- Python
- Pylance
- Black Formatter
- Ruff
- GitLens

### Configuration Files

The project includes several configuration files:
- `pyproject.toml` - Project configuration and dependencies
- `.pre-commit-config.yaml` - Pre-commit hooks
- `pytest.ini` - Test configuration
- `.editorconfig` - Editor settings

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Report bugs and issues
- **Feature Requests**: Suggest new features
- **Code Contributions**: Submit code improvements
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve tests
- **Translation**: Help with internationalization

### Issue Guidelines

When creating issues, please:

1. **Use the issue templates** provided
2. **Provide clear descriptions** of the problem or feature
3. **Include reproduction steps** for bugs
4. **Add relevant labels** to help categorize the issue
5. **Check for duplicates** before creating new issues

### Feature Request Process

1. **Create a feature request issue**
2. **Discuss the feature** with maintainers
3. **Get approval** before starting implementation
4. **Create a design document** for complex features
5. **Implement the feature** with tests
6. **Submit a pull request**

## Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters
- **Import sorting**: Use isort
- **Formatting**: Use Black
- **Type hints**: Required for all functions

### Code Quality Tools

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting and import sorting
- **MyPy**: Type checking
- **Pre-commit**: Automated checks

### Running Quality Checks

```bash
# Run all checks
./scripts/dev.sh check

# Run individual checks
black src/ tests/
ruff check src/ tests/
mypy src/
```

### Commit Message Format

We use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add user authentication system
fix(gui): resolve crash in grant search
docs(readme): update installation instructions
```

## Testing

### Test Structure

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
├── e2e/           # End-to-end tests
└── conftest.py    # Test configuration
```

### Writing Tests

1. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test functions: `test_*`

2. **Use descriptive test names**:
   ```python
   def test_grant_matching_returns_relevant_results():
       # Test implementation
   ```

3. **Use fixtures** for common setup:
   ```python
   @pytest.fixture
   def sample_organization():
       return OrganizationProfile(name="Test Org")
   ```

4. **Test edge cases** and error conditions

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

# Run specific test
pytest tests/unit/test_grant_researcher.py::test_find_matches
```

### Test Coverage

We aim for at least 80% test coverage. To check coverage:

```bash
pytest --cov=src/grant_ai --cov-report=term-missing
```

## Documentation

### Documentation Standards

- **Use clear, concise language**
- **Include code examples**
- **Keep documentation up to date**
- **Use proper formatting**

### Documentation Structure

```
docs/
├── user_guide.md      # User documentation
├── technical_guide.md # Technical documentation
├── api_reference.md   # API documentation
└── tutorials/         # Tutorial guides
```

### Writing Documentation

1. **Start with an overview**
2. **Include installation instructions**
3. **Provide usage examples**
4. **Document all public APIs**
5. **Include troubleshooting sections**

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Run quality checks**
3. **Update documentation**
4. **Add tests for new features**
5. **Follow commit message format**

### Pull Request Guidelines

1. **Use descriptive titles**
2. **Provide clear descriptions**
3. **Reference related issues**
4. **Include screenshots for UI changes**
5. **Add appropriate labels**

### Review Process

1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Address feedback** and make changes
4. **Get approval** from maintainers
5. **Merge** when ready

### Review Checklist

- [ ] Code follows project standards
- [ ] Tests are comprehensive
- [ ] Documentation is updated
- [ ] No breaking changes (or documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Release Process

### Versioning

We use semantic versioning (SemVer):
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Steps

1. **Create release branch** from develop
2. **Update version numbers**
3. **Update CHANGELOG.md**
4. **Run full test suite**
5. **Create release notes**
6. **Merge to main**
7. **Create release tag**
8. **Deploy to production**

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version numbers updated
- [ ] Release notes prepared
- [ ] Security review completed

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the docs first
- **Code Examples**: Look at existing code

### Communication Channels

- **GitHub**: Primary communication platform
- **Email**: For sensitive issues
- **Community Calls**: Regular video calls (if applicable)

### Recognition

We recognize contributors through:
- **Contributor profiles** in documentation
- **Release notes** acknowledgments
- **Community highlights** in newsletters
- **Contributor badges** on GitHub

### Mentorship

We offer mentorship for new contributors:
- **Onboarding guides**
- **Pair programming sessions**
- **Code review feedback**
- **Regular check-ins**

## Getting Help

If you need help with contributing:

1. **Check the documentation** first
2. **Search existing issues** for similar problems
3. **Ask in GitHub Discussions**
4. **Create an issue** if needed

## License

By contributing to Grant AI, you agree that your contributions will be licensed under the MIT License.

## Contact

- **Project Maintainers**: [Maintainer Names]
- **Email**: [Contact Email]
- **GitHub**: [Repository URL]

Thank you for contributing to Grant AI! 🚀 