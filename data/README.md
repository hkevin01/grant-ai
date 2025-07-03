# Data Directory

This directory contains data files for the Grant AI project.

## Structure

### profiles/
Contains organization profile files:
- `american_red_cross_|_help_those_affected_by_disasters_profile.json` - Sample Red Cross profile

### Other Data Files
- Grant databases and cached data will be stored in subdirectories
- Export files and reports may be generated here
- Configuration files for specific organizations

## Usage

Profile files can be loaded into the application via:
- GUI profile loading interface
- CLI profile management commands
- API endpoints for profile management

## File Formats

- **Profile files**: JSON format containing organization details, focus areas, and funding needs
- **Grant databases**: JSON or SQLite format for grant opportunity storage
- **Export files**: CSV, PDF, or Excel formats for reports and data exports
