"""OAuth2 authentication setup for Grant Research AI API."""

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# TODO: Implement token validation and user authentication
