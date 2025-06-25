#!/usr/bin/env python3
"""
Sample data generator for testing Grant AI functionality.
Creates realistic test data for grants, AI companies, and organizations.
"""

import json
from datetime import date, timedelta
from pathlib import Path

from grant_ai.models.ai_company import (
    AICompany,
    AIFocusArea,
    CompanySize,
    ReputationRating,
)
from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus
from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType


def create_sample_grants() -> list[Grant]:
    """Create sample grant data."""
    grants = []

    # Education-focused grants
    grants.append(
        Grant(
            id="ed-tech-001",
            title="AI in Education Innovation Grant",
            description="Supporting innovative uses of AI technology in educational settings",
            funder_name="Tech Education Foundation",
            funder_type="private_foundation",
            funding_type=FundingType.GRANT,
            amount_min=25000,
            amount_max=75000,
            amount_typical=50000,
            status=GrantStatus.OPEN,
            application_deadline=date.today() + timedelta(days=60),
            eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
            focus_areas=["education", "technology", "AI", "youth"],
            application_url="https://techedfoundation.org/grants/ai-education",
            source="foundation_website",
        )
    )

    grants.append(
        Grant(
            id="arts-music-002",
            title="Community Arts & Music Program Grant",
            description="Funding for community-based arts and music education programs",
            funder_name="National Arts Council",
            funder_type="government",
            funding_type=FundingType.GRANT,
            amount_min=15000,
            amount_max=100000,
            amount_typical=40000,
            status=GrantStatus.OPEN,
            application_deadline=date.today() + timedelta(days=45),
            eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.COMMUNITY],
            focus_areas=["arts", "music", "education", "community", "youth"],
            application_url="https://artscouncil.gov/grants/community",
            source="government_database",
        )
    )

    # Housing-focused grants
    grants.append(
        Grant(
            id="housing-dev-003",
            title="Affordable Housing Development Grant",
            description="Supporting innovative affordable housing projects for seniors and families",
            funder_name="Housing Innovation Fund",
            funder_type="private_foundation",
            funding_type=FundingType.GRANT,
            amount_min=100000,
            amount_max=500000,
            amount_typical=250000,
            status=GrantStatus.OPEN,
            application_deadline=date.today() + timedelta(days=90),
            eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.COMMUNITY],
            focus_areas=[
                "housing",
                "affordable housing",
                "seniors",
                "families",
                "community development",
            ],
            application_url="https://housinginnovation.org/grants",
            source="foundation_website",
        )
    )

    grants.append(
        Grant(
            id="social-impact-004",
            title="Social Impact Technology Grant",
            description="Funding technology solutions that address social challenges",
            funder_name="Social Tech Foundation",
            funder_type="private_foundation",
            funding_type=FundingType.GRANT,
            amount_min=20000,
            amount_max=80000,
            amount_typical=50000,
            status=GrantStatus.ROLLING,
            eligibility_types=[EligibilityType.NONPROFIT],
            focus_areas=["technology", "social impact", "community", "innovation"],
            application_url="https://socialtech.org/apply",
            source="foundation_website",
        )
    )

    return grants


def create_sample_ai_companies() -> list[AICompany]:
    """Create sample AI company data."""
    companies = []

    companies.append(
        AICompany(
            id="openai-001",
            name="OpenAI",
            description="AI research and deployment company focused on ensuring AI benefits humanity",
            website="https://openai.com",
            size=CompanySize.LARGE,
            founded_year=2015,
            headquarters="San Francisco, CA",
            ai_focus_areas=[AIFocusArea.NATURAL_LANGUAGE, AIFocusArea.MACHINE_LEARNING],
            has_grant_program=True,
            grant_program_name="OpenAI Community Grant",
            grant_program_url="https://openai.com/grants",
            grant_focus_areas=["education", "research", "social impact", "AI safety"],
            typical_grant_amount=75000,
            target_demographics=["researchers", "educators", "nonprofits"],
            supported_organization_types=["nonprofit", "education", "research"],
            reputation_rating=ReputationRating.EXCELLENT,
            social_impact_focus=["AI safety", "education", "research"],
            diversity_initiatives=True,
        )
    )

    companies.append(
        AICompany(
            id="google-ai-002",
            name="Google AI",
            description="Google's artificial intelligence research division",
            website="https://ai.google",
            size=CompanySize.ENTERPRISE,
            founded_year=2017,
            headquarters="Mountain View, CA",
            ai_focus_areas=[
                AIFocusArea.MACHINE_LEARNING,
                AIFocusArea.COMPUTER_VISION,
                AIFocusArea.NATURAL_LANGUAGE,
            ],
            has_grant_program=True,
            grant_program_name="Google.org AI for Social Good",
            grant_program_url="https://google.org/our-work/ai-for-social-good",
            grant_focus_areas=["social good", "education", "healthcare", "environment"],
            typical_grant_amount=100000,
            target_demographics=["nonprofits", "social organizations", "researchers"],
            supported_organization_types=["nonprofit", "research", "social enterprise"],
            reputation_rating=ReputationRating.EXCELLENT,
            social_impact_focus=["education", "healthcare", "climate", "economic opportunity"],
            diversity_initiatives=True,
        )
    )

    companies.append(
        AICompany(
            id="microsoft-ai-003",
            name="Microsoft AI",
            description="Microsoft's artificial intelligence platform and research",
            website="https://microsoft.com/ai",
            size=CompanySize.ENTERPRISE,
            founded_year=2016,
            headquarters="Redmond, WA",
            ai_focus_areas=[
                AIFocusArea.MACHINE_LEARNING,
                AIFocusArea.NATURAL_LANGUAGE,
                AIFocusArea.COMPUTER_VISION,
            ],
            has_grant_program=True,
            grant_program_name="AI for Good",
            grant_program_url="https://microsoft.com/ai-for-good",
            grant_focus_areas=[
                "accessibility",
                "humanitarian action",
                "cultural heritage",
                "earth",
            ],
            typical_grant_amount=150000,
            target_demographics=["nonprofits", "humanitarian organizations", "researchers"],
            supported_organization_types=["nonprofit", "humanitarian", "research", "education"],
            reputation_rating=ReputationRating.EXCELLENT,
            social_impact_focus=["accessibility", "humanitarian", "sustainability", "education"],
            diversity_initiatives=True,
        )
    )

    companies.append(
        AICompany(
            id="anthropic-004",
            name="Anthropic",
            description="AI safety company focused on building reliable, interpretable, and steerable AI",
            website="https://anthropic.com",
            size=CompanySize.MEDIUM,
            founded_year=2021,
            headquarters="San Francisco, CA",
            ai_focus_areas=[AIFocusArea.NATURAL_LANGUAGE, AIFocusArea.MACHINE_LEARNING],
            has_grant_program=True,
            grant_program_name="Anthropic Research Grants",
            grant_program_url="https://anthropic.com/grants",
            grant_focus_areas=["AI safety", "research", "education", "ethics"],
            typical_grant_amount=50000,
            target_demographics=["researchers", "academics", "safety organizations"],
            supported_organization_types=["research", "education", "nonprofit"],
            reputation_rating=ReputationRating.GOOD,
            social_impact_focus=["AI safety", "research", "education"],
            diversity_initiatives=True,
        )
    )

    return companies


def create_sample_organizations() -> list[OrganizationProfile]:
    """Create sample organization profiles."""
    organizations = []

    # CODA profile
    coda = OrganizationProfile(
        name="CODA",
        description="Community organization focused on education programs in music, art, and robotics for youth",
        focus_areas=[FocusArea.MUSIC_EDUCATION, FocusArea.ART_EDUCATION, FocusArea.ROBOTICS],
        program_types=[ProgramType.AFTER_SCHOOL, ProgramType.SUMMER_CAMPS],
        target_demographics=["youth", "students", "families", "underserved communities"],
        annual_budget=250000,
        location="Local Community",
        website="https://coda.org",
        founded_year=2015,
        preferred_grant_size=(25000, 100000),
        contact_name="Sarah Johnson",
        contact_email="sarah@coda.org",
        contact_phone="(555) 123-4567",
    )
    organizations.append(coda)

    # NRG Development profile
    nrg = OrganizationProfile(
        name="Christian Pocket Community/NRG Development",
        description="Developing affordable, efficient housing for retired people with support for struggling single mothers and others in need",
        focus_areas=[
            FocusArea.AFFORDABLE_HOUSING,
            FocusArea.COMMUNITY_DEVELOPMENT,
            FocusArea.SENIOR_SERVICES,
        ],
        program_types=[ProgramType.HOUSING_DEVELOPMENT, ProgramType.SUPPORT_SERVICES],
        target_demographics=["retired people", "single mothers", "low-income families", "seniors"],
        annual_budget=500000,
        location="Regional",
        founded_year=2018,
        preferred_grant_size=(100000, 500000),
        contact_name="Michael Chen",
        contact_email="michael@nrgdev.org",
        contact_phone="(555) 987-6543",
    )
    organizations.append(nrg)

    return organizations


def save_sample_data():
    """Save all sample data to files."""
    # Create data directory
    data_dir = Path("data/sample")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Create grants
    grants = create_sample_grants()
    grants_data = [grant.dict() for grant in grants]
    with open(data_dir / "sample_grants.json", "w") as f:
        json.dump(grants_data, f, indent=2, default=str)
    print(f"Created {len(grants)} sample grants")

    # Create AI companies
    companies = create_sample_ai_companies()
    companies_data = [company.dict() for company in companies]
    with open(data_dir / "sample_ai_companies.json", "w") as f:
        json.dump(companies_data, f, indent=2, default=str)
    print(f"Created {len(companies)} sample AI companies")

    # Create organizations
    organizations = create_sample_organizations()
    for org in organizations:
        filename = f"{org.name.lower().replace(' ', '_').replace('/', '_')}_profile.json"
        with open(data_dir / filename, "w") as f:
            json.dump(org.dict(), f, indent=2, default=str)
    print(f"Created {len(organizations)} sample organization profiles")

    print(f"\nSample data saved to {data_dir}/")
    print("Files created:")
    print("- sample_grants.json")
    print("- sample_ai_companies.json")
    print("- coda_profile.json")
    print("- christian_pocket_community_nrg_development_profile.json")


if __name__ == "__main__":
    save_sample_data()
