"""API endpoints for grant, organization, and application management."""


from fastapi import APIRouter, HTTPException

from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile
from grant_ai.models.application import Application

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


@router.get("/organizations/{org_id}")
def get_organization(org_id: str):
    # Fetch organization profile from database or file
    try:
        # ...fetch logic...
        return OrganizationProfile(
            name=org_id, description="Sample org", focus_areas=[], program_types=[]
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/organizations/")
def create_organization(profile: OrganizationProfile):
    # Save organization profile
    try:
        # ...save logic...
        return {"status": "success", "org": profile}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/applications/{app_id}")
def get_application(app_id: str):
    # Fetch application from database or file
    try:
        # ...fetch logic...
        return Application(id=app_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/applications/")
def create_application(app: Application):
    # Save application
    try:
        # ...save logic...
        return {"status": "success", "application": app}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
