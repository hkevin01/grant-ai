"""
Data validation utilities for Grant AI.
"""
from typing import Any, Dict, List

def validate_required_fields(data: Dict[str, Any], required: List[str]) -> List[str]:
    """Return list of missing required fields."""
    return [field for field in required if field not in data or not data[field]]

def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))
