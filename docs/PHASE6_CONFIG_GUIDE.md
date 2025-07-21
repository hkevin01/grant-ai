# Phase 6 Configuration Guide

This guide describes configuration options for the next phase of Grant Research AI.

## Configuration Files

-   `src/grant_ai/config/settings.py`: Main application settings
-   `.env`: Environment variables for secrets and deployment

## How to Update Settings

1. Edit `settings.py` to change default values.
2. Use environment variables for sensitive data.
3. Restart the application after making changes.

## Example `.env` file

```
DATABASE_URL=sqlite:///data/grants.db
DEBUG=True
APP_NAME=Grant Research AI
```

## Best Practices

-   Do not commit secrets to version control.
-   Document all configuration changes in this guide.
