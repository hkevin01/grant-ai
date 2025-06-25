"""Test configuration and fixtures for the Grant AI test suite."""

from datetime import date, timedelta

import pytest

from grant_ai.models.ai_company import (
    AICompany,
    AIFocusArea,
    CompanySize,
    ReputationRating,
)
from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus
from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType


@pytest.fixture
def sample_organization():
    """Create a sample organization for testing."""
    return OrganizationProfile(
        name="Test Organization",
        description="A test organization for unit tests",
        focus_areas=[FocusArea.EDUCATION, FocusArea.ROBOTICS],
        program_types=[ProgramType.AFTER_SCHOOL],
        annual_budget=100000,
        location="Test City",
        preferred_grant_size=(10000, 50000)
    )


@pytest.fixture
def sample_grant():
    """Create a sample grant for testing."""
    return Grant(
        id="test-grant-001",
        title="Test Education Grant",
        description="A grant for testing purposes",
        funder_name="Test Foundation",
        funding_type=FundingType.GRANT,
        amount_typical=25000,
        status=GrantStatus.OPEN,
        application_deadline=date.today() + timedelta(days=30),
        eligibility_types=[EligibilityType.NONPROFIT],
        focus_areas=["education", "technology"]
    )


@pytest.fixture  
def sample_ai_company():
    """Create a sample AI company for testing."""
    return AICompany(
        id="test-company-001",
        name="Test AI Company",
        description="An AI company for testing",
        size=CompanySize.MEDIUM,
        ai_focus_areas=[AIFocusArea.EDUCATION_TECH],
        has_grant_program=True,
        grant_focus_areas=["education", "technology"],
        typical_grant_amount=50000,
        reputation_rating=ReputationRating.GOOD,
        supported_organization_types=["nonprofit"]
    )
