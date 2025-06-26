"""
Utility script to scrape Coda Mountain Academy website information.
"""
import json
from pathlib import Path
from typing import Dict, Optional

from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType


def scrape_coda_info() -> Dict:
    """
    Scrape information about Coda Mountain Academy from their website.
    Returns a dictionary with organization information.
    """
    # Based on the website content provided
    coda_info = {
        "name": "Coda Mountain Academy",
        "description": (
            "Coda Mountain Academy is a non-profit organization dedicated to "
            "equipping and developing young students and their families through "
            "unique and outstanding educational opportunities. We use Arts "
            "Integration to develop exposure and opportunities that promote "
            "healthy goal setting, positive identity, strong character, "
            "resiliency, and life skills. Coda hopes to change the world, "
            "one child at a time."
        ),
        "focus_areas": [
            FocusArea.EDUCATION,
            FocusArea.ART_EDUCATION,
            FocusArea.ROBOTICS,
            FocusArea.YOUTH_DEVELOPMENT
        ],
        "program_types": [
            ProgramType.AFTER_SCHOOL,
            ProgramType.SUMMER_CAMPS,
            ProgramType.EDUCATIONAL_WORKSHOPS,
            ProgramType.COMMUNITY_OUTREACH
        ],
        "target_demographics": [
            "Youth",
            "Families",
            "Students",
            "Young people in crisis",
            "Families affected by addiction"
        ],
        "location": "Fayetteville, West Virginia",
        "website": "https://www.codamountain.com/",
        "contact_email": "info@codamountain.com",
        "contact_phone": "304-900-0096",
        "address": "P.O. Box 615 Fayetteville, WV",
        "mission": (
            "INSPIRE. EDUCATE. EMPOWER. Transforming Fayette County, WV "
            "through youth & family engagement"
        ),
        "programs": [
            "Afterschool Programs",
            "Revive",
            "Grandfamily Support Group", 
            "Competitive Robotics Team",
            "Coda Fine Arts",
            "Coda Explore",
            "Music camps",
            "Lego robotics",
            "Art programs",
            "Cooking classes",
            "Outdoor recreation"
        ],
        "impact": (
            "In 2018 Coda provided over 500 youth and their families with "
            "summer camps and after-school programs"
        ),
        "founded_year": 2015,  # Based on copyright year
        "annual_budget": None,  # Not publicly available
        "preferred_grant_size": (25000, 100000),  # Estimated based on program scope
        "contact_name": "Coda Mountain Academy Staff"
    }
    
    return coda_info


def create_coda_profile() -> OrganizationProfile:
    """
    Create an OrganizationProfile instance for Coda Mountain Academy.
    """
    coda_info = scrape_coda_info()
    
    return OrganizationProfile(
        name=coda_info["name"],
        description=coda_info["description"],
        focus_areas=coda_info["focus_areas"],
        program_types=coda_info["program_types"],
        target_demographics=coda_info["target_demographics"],
        location=coda_info["location"],
        website=coda_info["website"],
        contact_name=coda_info["contact_name"],
        contact_email=coda_info["contact_email"],
        contact_phone=coda_info["contact_phone"],
        annual_budget=coda_info["annual_budget"],
        ein=None,  # Not publicly available
        founded_year=coda_info["founded_year"],
        preferred_grant_size=coda_info["preferred_grant_size"]
    )


def save_coda_profile_to_file(output_path: Optional[Path] = None) -> Path:
    """
    Save Coda Mountain Academy profile to a JSON file.
    """
    if output_path is None:
        output_path = (
            Path(__file__).parent.parent.parent / "data" / "profiles" / 
            "coda_profile.json"
        )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    coda_profile = create_coda_profile()
    
    with open(output_path, 'w') as f:
        json.dump(coda_profile.model_dump(), f, indent=2, default=str)
    
    print(f"Coda Mountain Academy profile saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    # Save the profile
    save_coda_profile_to_file()
    
    # Print the profile information
    coda_info = scrape_coda_info()
    print("\nCoda Mountain Academy Profile:")
    print(f"Name: {coda_info['name']}")
    print(f"Mission: {coda_info['mission']}")
    print(f"Location: {coda_info['location']}")
    print(f"Contact: {coda_info['contact_email']} | {coda_info['contact_phone']}")
    print(f"Programs: {', '.join(coda_info['programs'])}")
    print(f"Impact: {coda_info['impact']}") 