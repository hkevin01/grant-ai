"""API endpoints for grant, organization, and application management."""


from fastapi import APIRouter

from grant_ai.models.grant import Grant

router = APIRouter()


# Example endpoint: Health check
def get_health():
    return {"status": "ok"}


router.add_api_route("/health", get_health, methods=["GET"])

# Example: List grants endpoint
fake_grants = [
    Grant(id="g1", title="Music Education Grant", funder_name="Arts Foundation"),
    Grant(id="g2", title="Robotics Youth Grant", funder_name="Tech Foundation"),
]


def list_grants() -> list[Grant]:
    return [grant.to_dict() for grant in fake_grants]


router.add_api_route("/grants", list_grants, methods=["GET"])

# TODO: Add endpoints for organization and application management
