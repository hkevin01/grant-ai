"""Core exception classes for Grant AI application."""


class GrantAIError(Exception):
    """Base exception class for Grant AI."""
    pass


class ScraperError(GrantAIError):
    """Base exception for scraping errors."""
    pass


class NetworkError(ScraperError):
    """Network-related errors during scraping."""
    pass


class ParsingError(ScraperError):
    """Error parsing scraped content."""
    pass


class RateLimitError(ScraperError):
    """Rate limiting or throttling error."""
    pass


class TemporaryError(ScraperError):
    """Temporary error that may resolve with retry."""
    pass


class PermanentError(ScraperError):
    """Permanent error that won't resolve with retry."""
    pass


class DatabaseError(GrantAIError):
    """Database operation errors."""
    pass


class AIError(GrantAIError):
    """AI-related operation errors."""
    pass


class ValidationError(GrantAIError):
    """Data validation errors."""
    pass
