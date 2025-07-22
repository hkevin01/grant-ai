# Grant AI Test Plan

## Overview
This document outlines the testing strategy for the Grant AI project, including unit, integration, and end-to-end tests. All tests must be run using the project's venv.

## Test Strategy
- Unit tests for all core modules (models, analysis, CLI, scrapers)
- Integration tests for database, scrapers, and GUI
- End-to-end tests for user workflows (profile creation, grant search, application management)
- Manual exploratory testing for GUI and edge cases

## Test Categories
- Unit Tests: Validate individual modules and functions
- Integration Tests: Ensure components work together as expected
- End-to-End Tests: Simulate real user workflows
- Performance Tests: Measure speed and resource usage
- Security Tests: Identify vulnerabilities

## Test Coverage Goals
- ✅ Organization, Grant, and AICompany models
- ✅ GrantResearcher analysis and matching
- ✅ CLI commands for profile and grant management
- ✅ Scrapers for grants.gov API integration
- ✅ Application management system (questionnaire, templates, tracking, reporting)
- ✅ Database integration and persistence
- 🔄 GUI workflows (profile, search, results) - partially tested
- 🔄 End-to-end user workflows - in progress

## Test Execution
- All tests must be run with the venv activated
- Test output should be logged to logs/test_output_log.md for review

## Test Types
- ✅ Unit tests (pytest) - comprehensive coverage
- ✅ Integration tests - database and service layer
- 🔄 End-to-end tests - in progress
- 🔄 Manual/Exploratory tests - ongoing

## Test Tools
- ✅ pytest - primary testing framework
- ✅ pytest-cov - code coverage reporting
- ✅ PyQt testing - GUI component testing
- ✅ SQLAlchemy - database integration testing
- ✅ Mock/fixtures - isolated unit testing

## Phase 1: Project Modernization
- [x] Test refactored project structure
- [x] Validate config and dependency updates
- [x] Run lint and pre-commit checks
- [x] Test fallback/sample logic

## Phase 2: Grant Scraper and Analytics
- [x] Unit test grant scrapers for all sources
- [x] Test analytics and reporting modules
- [x] Validate logging and error handling
- [x] Coverage for analytics and scrapers

## Phase 3: Platform Integrations
- [x] Test API endpoints for organization/application management
- [x] Validate OpenGrants and multi-platform discovery
- [x] Test grant merging and deduplication
- [x] Platform statistics and reporting tests

## Phase 4: Advanced Grant Discovery
- [x] Test NASA NSPIRES and ESA OSIP integration
- [x] Validate Grants.gov API filtering
- [x] Test NSF and DOE AI program discovery
- [x] Enhanced grant discovery class tests
- [x] Domain/relevance scoring tests

## Phase 5: AI Proposal Classification
- [x] Unit test AI proposal classifier
- [x] Validate domain classification and relevance scoring
- [x] Test NASA Responsible AI alignment
- [x] ESA Discovery themes matching tests

## Phase 6: Community Signal Integration
- [x] Test arXiv paper monitoring
- [x] Validate NASA/ESA report tracking
- [x] Trending research direction analysis tests
- [x] Funding opportunity extraction tests

## Phase 7: Proposal Generator Enhancement
- [ ] Test NASA-specific proposal templates
- [ ] Validate ESA Discovery theme alignment
- [ ] IAC abstract formatting automation tests
- [ ] AI ethics/responsible AI integration tests
- [ ] Proposal generator logic tests

## Phase 8: Mobile App and Accessibility
- [ ] Test mobile wireframes and workflows
- [ ] Validate mobile grant search and tracking
- [ ] Accessibility feature tests
- [ ] UI improvement tests

## Phase 9: Data Analytics Dashboard
- [ ] Analytics dashboard unit/integration tests
- [ ] Integration tests for Google, Office 365, Salesforce
- [ ] Performance and caching tests

## Progress Tracking
- [x] Update test logs and documentation for each phase
- [x] Maintain coverage and expand tests as needed
- [x] Review and expand checklists regularly

## Test Documentation ✅ COMPLETE
- **Test Strategy**: Clear testing approach documented
- **Test Cases**: All test cases documented with purpose
- **Setup Instructions**: Clear test environment setup
- **Coverage Reports**: Regular coverage analysis and reporting
