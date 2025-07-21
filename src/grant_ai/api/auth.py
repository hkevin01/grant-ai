"""
Authentication module for Grant Research AI API.
Handles OAuth2 authentication and user retrieval.
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user based on OAuth2 token.
    Raises HTTPException if authentication fails.
    """
    if not token:
        logger.error("Authentication failed: No token provided.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    # TODO: Implement token validation and user retrieval
    logger.info(f"Authenticated user with token: {token}")
    return {"username": "demo_user"}
