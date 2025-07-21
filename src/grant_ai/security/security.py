"""
Security module for Grant AI.
"""
from typing import Any
from grant_ai.utils.logger import get_logger

logger = get_logger(__name__)


def check_permissions(user: Any, action: str) -> bool:
    """
    Check if a user has permission for an action.

    Args:
        user (Any): User object with role attribute.
        action (str): Action to check.

    Returns:
        bool: True if permitted, False otherwise.
    """
    try:
        if hasattr(user, 'role') and user.role == 'admin':
            logger.info(f"Admin access granted for action: {action}")
            return True
        if action == 'view':
            logger.info(f"View access granted for user: {getattr(user, 'role', None)}")
            return True
        logger.warning(f"Access denied for user: {getattr(user, 'role', None)} action: {action}")
        return False
    except Exception as e:
        logger.error(f"Error checking permissions: {e}")
        return False
