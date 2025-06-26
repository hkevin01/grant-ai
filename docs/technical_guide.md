# Grant AI Technical Guide

## Overview
This technical guide provides comprehensive information for system administrators, developers, and advanced users of the Grant AI system.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Installation & Configuration](#installation--configuration)
3. [Database Management](#database-management)
4. [API Reference](#api-reference)
5. [Development Guide](#development-guide)
6. [Deployment](#deployment)
7. [Maintenance & Administration](#maintenance--administration)
8. [Security](#security)
9. [Performance Optimization](#performance-optimization)
10. [Troubleshooting](#troubleshooting)

## System Architecture

### Overview
Grant AI follows a modular Python architecture with the following components:

```
grant-ai/
├── src/grant_ai/           # Core application code
│   ├── models/             # Data models and ORM
│   ├── services/           # Business logic layer
│   ├── gui/               # PyQt user interface
│   ├── scrapers/          # Data collection modules
│   ├── analysis/          # Matching algorithms
│   └── cli.py             # Command-line interface
├── data/                   # Data storage
├── scripts/               # Utility scripts
├── tests/                 # Test suite
└── docs/                  # Documentation
```

### Core Technologies
- **Language**: Python 3.9+
- **GUI Framework**: PyQt5
- **Database**: SQLite (with SQLAlchemy ORM)
- **Web Scraping**: Requests, BeautifulSoup, Scrapy
- **Data Analysis**: Pandas, NumPy
- **Reporting**: ReportLab (PDF), Matplotlib, Seaborn
- **Testing**: pytest

### Design Patterns
- **MVC Architecture**: Models, Views (GUI), Controllers (Services)
- **Repository Pattern**: Data access abstraction
- **Strategy Pattern**: Pluggable matching algorithms
- **Observer Pattern**: Event-driven updates
- **Factory Pattern**: Template and questionnaire creation

## Installation & Configuration

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.9.0 or higher
- **RAM**: 4GB
- **Storage**: 1GB free space
- **Display**: 1024x768 resolution

#### Recommended Requirements
- **OS**: Latest stable versions
- **Python**: 3.11.0 or higher
- **RAM**: 8GB or more
- **Storage**: 5GB free space
- **Display**: 1920x1080 or higher

### Installation Steps

#### 1. Environment Setup
```bash
# Clone or extract the Grant AI package
cd grant-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Database Initialization
```bash
# Initialize the database
python scripts/setup.py

# Import sample data (optional)
python scripts/generate_sample_data.py

# Fetch current grants (optional)
python scripts/fetch_grants_gov.py --limit 100
```

#### 3. Configuration
```bash
# Copy default configuration
cp config/default.ini config/local.ini

# Edit configuration as needed
# Configuration options documented below
```

### Configuration Options

#### Database Configuration
```ini
[database]
url = sqlite:///data/grants.db
pool_size = 10
pool_recycle = 3600
echo = false  # Set to true for SQL debugging
```

#### API Configuration
```ini
[api]
grants_gov_base_url = https://www.grants.gov/web/grants/search-grants.html
rate_limit_delay = 1.0
timeout = 30
max_retries = 3
```

#### Application Configuration
```ini
[application]
default_data_dir = data
max_search_results = 1000
auto_save_interval = 300  # seconds
backup_retention_days = 30
```

#### Logging Configuration
```ini
[logging]
level = INFO
file = logs/grant_ai.log
max_file_size = 10MB
backup_count = 5
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Database Management

### Schema Overview
The Grant AI database uses SQLAlchemy ORM with the following main tables:

#### Organizations Table
```sql
CREATE TABLE organizations (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    mission TEXT,
    focus_areas JSON,
    annual_budget VARCHAR,
    geographic_scope VARCHAR,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### Grants Table
```sql
CREATE TABLE grants (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    funder_name VARCHAR,
    amount_min INTEGER,
    amount_max INTEGER,
    application_deadline DATE,
    focus_areas JSON,
    eligibility_types JSON,
    geographic_restrictions JSON,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### Applications Table
```sql
CREATE TABLE applications (
    id VARCHAR PRIMARY KEY,
    organization_id VARCHAR,
    grant_id VARCHAR,
    status VARCHAR,
    amount_requested INTEGER,
    submission_date DATE,
    decision_date DATE,
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (grant_id) REFERENCES grants(id)
);
```

### Database Operations

#### Backup
```bash
# Create database backup
python -c "
import shutil
from datetime import datetime
backup_name = f'data/grants_backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.db'
shutil.copy('data/grants.db', backup_name)
print(f'Backup created: {backup_name}')
"
```

#### Restore
```bash
# Restore from backup
cp data/grants_backup_YYYYMMDD_HHMMSS.db data/grants.db
```

#### Maintenance
```bash
# Vacuum database (reclaim space)
sqlite3 data/grants.db "VACUUM;"

# Analyze database (update statistics)
sqlite3 data/grants.db "ANALYZE;"

# Check integrity
sqlite3 data/grants.db "PRAGMA integrity_check;"
```

### Data Migration
```python
# Example migration script
from src.grant_ai.db import get_session
from sqlalchemy import text

def migrate_database():
    session = get_session()
    try:
        # Add new column example
        session.execute(text("ALTER TABLE grants ADD COLUMN new_field VARCHAR;"))
        session.commit()
        print("Migration completed successfully")
    except Exception as e:
        session.rollback()
        print(f"Migration failed: {e}")
    finally:
        session.close()
```

## API Reference

### Core Services

#### QuestionnaireManager
```python
from src.grant_ai.services.questionnaire_manager import QuestionnaireManager

qm = QuestionnaireManager()

# Get questionnaire structure
questionnaire = qm.get_questionnaire()

# Validate responses
is_valid = qm.validate_responses(responses)

# Create profile from responses
profile = qm.create_profile_from_responses(responses)
```

#### TemplateManager
```python
from src.grant_ai.services.template_manager import TemplateManager

tm = TemplateManager()

# Get available templates
templates = tm.get_available_templates()

# Create application from template
application = tm.create_application_from_template(template_id, data)

# Save custom template
tm.save_template(template_data)
```

#### ReportGenerator
```python
from src.grant_ai.services.report_generator import ReportGenerator

rg = ReportGenerator()

# Generate summary report
report = rg.generate_summary_report(organization_id, date_range)

# Export to Excel
rg.export_to_excel(report_data, filename)

# Generate charts
charts = rg.generate_charts(data)
```

### CLI Commands

#### Profile Management
```bash
# Create new profile
grant-ai profile create --name "Org Name" --focus-area education

# Show profile
grant-ai profile show profile.json

# Validate profile
grant-ai profile validate profile.json
```

#### Grant Research
```bash
# Search grants
grant-ai research grants --keywords "education arts" --amount-min 10000

# Match grants to profile
grant-ai match grants profile.json

# Research AI companies
grant-ai research companies --focus education
```

#### Data Management
```bash
# Import grants
grant-ai data import-grants grants_file.json

# Export data
grant-ai data export --format json --output export.json

# Update database
grant-ai data update-grants
```

## Development Guide

### Development Environment
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run development server
python scripts/dev.sh run
```

### Code Style
- **Style Guide**: PEP 8
- **Line Length**: 79 characters
- **Docstrings**: Google style
- **Type Hints**: Required for all functions
- **Import Order**: isort configuration in pyproject.toml

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/grant_ai

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

### Adding New Features

#### 1. Create Model
```python
# src/grant_ai/models/new_model.py
from sqlalchemy import Column, String, DateTime
from .base import Base

class NewModel(Base):
    __tablename__ = 'new_models'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime)
```

#### 2. Create Service
```python
# src/grant_ai/services/new_service.py
from typing import List, Optional
from ..models.new_model import NewModel

class NewService:
    def create(self, data: dict) -> NewModel:
        # Implementation
        pass
    
    def get_all(self) -> List[NewModel]:
        # Implementation
        pass
```

#### 3. Add Tests
```python
# tests/test_new_feature.py
import pytest
from src.grant_ai.services.new_service import NewService

def test_new_service_create():
    service = NewService()
    result = service.create({'name': 'Test'})
    assert result.name == 'Test'
```

#### 4. Add CLI Command
```python
# src/grant_ai/cli.py
@cli.group()
def new_command():
    """New feature commands."""
    pass

@new_command.command()
@click.option('--name', required=True)
def create(name):
    """Create new item."""
    # Implementation
    pass
```

## Deployment

### Production Deployment

#### 1. Environment Preparation
```bash
# Create production environment
python -m venv prod_env
source prod_env/bin/activate

# Install production dependencies only
pip install -r requirements.txt --no-dev
```

#### 2. Configuration
```ini
# config/production.ini
[database]
url = postgresql://user:pass@host:port/dbname
pool_size = 20

[logging]
level = WARNING
file = /var/log/grant_ai/app.log

[application]
debug = false
auto_save_interval = 600
```

#### 3. Database Setup
```bash
# Run migrations
python scripts/migrate_database.py

# Initialize production data
python scripts/setup_production.py
```

#### 4. Service Configuration
```ini
# /etc/systemd/system/grant-ai.service
[Unit]
Description=Grant AI Application
After=network.target

[Service]
Type=simple
User=grant-ai
WorkingDirectory=/opt/grant-ai
ExecStart=/opt/grant-ai/venv/bin/python scripts/launch_gui.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["python", "scripts/launch_gui.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  grant-ai:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - grant_data:/app/data
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/grant_ai
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: grant_ai
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  grant_data:
  postgres_data:
```

## Maintenance & Administration

### Regular Maintenance Tasks

#### Daily
- Monitor system logs
- Check database space
- Verify backup completion
- Review error reports

#### Weekly
- Update grants database
- Generate usage reports
- Check for software updates
- Clean temporary files

#### Monthly
- Full database backup
- Performance analysis
- Security audit
- User training review

### Monitoring
```python
# scripts/monitor.py
import logging
import psutil
from src.grant_ai.db import get_session

def check_system_health():
    """Check various system health metrics."""
    
    # Database connectivity
    try:
        session = get_session()
        session.execute("SELECT 1")
        db_status = "OK"
    except Exception as e:
        db_status = f"ERROR: {e}"
    
    # Disk space
    disk_usage = psutil.disk_usage('/').percent
    
    # Memory usage
    memory_usage = psutil.virtual_memory().percent
    
    # Log results
    logging.info(f"Database: {db_status}")
    logging.info(f"Disk usage: {disk_usage}%")
    logging.info(f"Memory usage: {memory_usage}%")
```

### Log Management
```bash
# Rotate logs
logrotate /etc/logrotate.d/grant-ai

# Archive old logs
tar -czf logs_archive_$(date +%Y%m%d).tar.gz logs/*.log.1

# Clean old archives (keep 90 days)
find logs/ -name "*.tar.gz" -mtime +90 -delete
```

## Security

### Security Best Practices

#### Data Protection
- Encrypt sensitive data at rest
- Use secure database connections
- Implement regular backups
- Control file permissions

#### Access Control
- Use strong authentication
- Implement role-based access
- Monitor user activities
- Regular access reviews

#### Network Security
- Use HTTPS for all connections
- Implement firewall rules
- Monitor network traffic
- Regular security scans

### Security Configuration
```ini
# config/security.ini
[authentication]
session_timeout = 3600
password_complexity = high
multi_factor_auth = enabled

[encryption]
data_encryption = AES256
key_rotation_days = 90
secure_key_storage = enabled

[audit]
log_all_access = true
log_data_changes = true
audit_retention_days = 365
```

## Performance Optimization

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_grants_focus_areas ON grants(focus_areas);
CREATE INDEX idx_grants_deadline ON grants(application_deadline);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_org ON applications(organization_id);
```

### Application Optimization
```python
# Enable query caching
from sqlalchemy import create_engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Use connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30
)
```

### Memory Management
```python
# Implement pagination for large datasets
def get_grants_paginated(page=1, per_page=50):
    session = get_session()
    query = session.query(Grant)
    return query.offset((page - 1) * per_page).limit(per_page).all()

# Use generators for large data processing
def process_grants_batch():
    session = get_session()
    for grant in session.query(Grant).yield_per(100):
        yield process_grant(grant)
```

## Troubleshooting

### Common Issues

#### High Memory Usage
**Symptoms**: Application becomes slow, system runs out of memory
**Solutions**:
1. Check for memory leaks in custom code
2. Implement pagination for large datasets
3. Close database sessions properly
4. Use connection pooling
5. Monitor SQLAlchemy query execution

#### Database Lock Issues
**Symptoms**: "Database is locked" errors
**Solutions**:
1. Check for long-running transactions
2. Implement proper exception handling
3. Use connection pooling
4. Consider using PostgreSQL for production
5. Monitor concurrent access patterns

#### GUI Performance Issues
**Symptoms**: Slow interface response, freezing
**Solutions**:
1. Implement background processing for long operations
2. Use threading for database operations
3. Optimize query performance
4. Implement caching for frequently accessed data
5. Profile code to identify bottlenecks

### Diagnostic Tools
```python
# Performance profiling
import cProfile
import pstats

def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
    
    return result

# Memory profiling
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function to profile
    pass
```

### Log Analysis
```bash
# Find errors in logs
grep ERROR logs/grant_ai.log | tail -20

# Analyze performance
grep "SLOW QUERY" logs/grant_ai.log

# Monitor database connections
grep "database" logs/grant_ai.log | grep -E "(connect|disconnect)"
```

---

## Additional Resources

### Development Tools
- **IDE**: VS Code with Python extension
- **Database Browser**: DB Browser for SQLite
- **Profiling**: PyCharm profiler or line_profiler
- **Testing**: pytest with coverage reports

### External Documentation
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [pytest Documentation](https://docs.pytest.org/)
- [Click CLI Documentation](https://click.palletsprojects.com/)

### Support Channels
- **Issue Tracking**: GitHub Issues
- **Documentation**: Wiki pages
- **Community**: Discussion forums
- **Direct Support**: Email support team

---

*This technical guide provides comprehensive information for system administration and development. For user-focused documentation, see the User Guide.*
