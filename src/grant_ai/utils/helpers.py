"""
General-purpose helper functions for Grant AI.
"""
from typing import Any, List, Dict


def chunk_list(lst: List[Any], n: int) -> List[List[Any]]:
    """Split a list into chunks of size n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]


def safe_get(d: Dict, key: Any, default: Any = None) -> Any:
    """Safely get a value from a dict."""
    return d.get(key, default)
