# Tests Directory

This directory contains all test files for the Grant AI project.

## Structure

### Unit Tests (root level)
- `test_grant_details.py` - Tests for grant detail functionality
- `test_preset_organizations.py` - Tests for preset organization features

### integration/
Contains integration and end-to-end tests:
- `test_all_enhancements.py` - Comprehensive validation of all improvements
- `test_enhanced_scraping.py` - Enhanced scraping functionality tests
- `test_improvements.py` - General improvement validation tests
- `demo_enhanced_scraping.py` - Demonstration of enhanced scraping capabilities

### scrapers/
Contains scraper-specific tests:
- `test_enhanced_education_scraping.py` - Enhanced education scraper tests
- `test_education_only.py` - Education URL and assistance detection tests
- `test_wv_education_direct.py` - Direct WV education scraping tests
- `test_attribute_fix.py` - AttributeError fix validation

## Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/integration/
python -m pytest tests/scrapers/

# Run individual test files
python tests/integration/test_all_enhancements.py
python tests/scrapers/test_education_only.py
```
