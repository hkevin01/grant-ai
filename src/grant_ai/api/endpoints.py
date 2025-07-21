"""API endpoints for grant, organization, and application management."""

from typing import List

from fastapi import APIRouter

from grant_ai.models.grant import Grant

router = APIRouter()


# Example endpoint: Health check
def get_health():
    return {"status": "ok"}


router.add_api_route("/health", get_health, methods=["GET"])


# Example: List grants endpoint
def list_grants() -> list[Grant]:
    # TODO: Replace with real database query
    return []


router.add_api_route("/grants", list_grants, methods=["GET"])

# TODO: Add endpoints for organization and application management
