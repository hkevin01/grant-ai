# Grant Research AI Test Plan

## Test Strategy
- Unit tests for all core modules (models, analysis, CLI, scrapers)
- Integration tests for database, scrapers, and GUI
- End-to-end tests for user workflows (profile creation, grant search, application management)
- Manual exploratory testing for GUI and edge cases

## Test Coverage Goals
- [x] Organization, Grant, and AICompany models
- [x] GrantResearcher analysis and matching
- [x] CLI commands for profile and grant management
- [ ] Scrapers for state/federal/common sources
- [ ] GUI workflows (profile, search, results)
- [ ] Database integration and persistence
- [ ] Application management and reporting

## Test Types
- [x] Unit tests (pytest)
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Manual/Exploratory tests

## Test Tools
- [x] pytest
- [x] pytest-cov
- [x] Streamlit (GUI manual testing)
- [x] SQLAlchemy (DB integration)
