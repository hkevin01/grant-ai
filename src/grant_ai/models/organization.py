"""Data models for organizations, grants, and AI companies."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FocusArea(str, Enum):
    """Enumeration of organization focus areas."""
    EDUCATION = "education"
    MUSIC_EDUCATION = "music_education"
    ART_EDUCATION = "art_education"
    ROBOTICS = "robotics"
    HOUSING = "housing"
    AFFORDABLE_HOUSING = "affordable_housing"
    COMMUNITY_DEVELOPMENT = "community_development"
    SOCIAL_SERVICES = "social_services"
    YOUTH_DEVELOPMENT = "youth_development"
    SENIOR_SERVICES = "senior_services"


class ProgramType(str, Enum):
    """Enumeration of program types."""
    AFTER_SCHOOL = "after_school"
    SUMMER_CAMPS = "summer_camps"
    HOUSING_DEVELOPMENT = "housing_development"
    SUPPORT_SERVICES = "support_services"
    EDUCATIONAL_WORKSHOPS = "educational_workshops"
    COMMUNITY_OUTREACH = "community_outreach"


class PastGrant(BaseModel):
    """Model representing a past grant awarded or applied for by the organization."""
    grant_id: str = Field(..., description="Unique identifier for the grant (e.g., federal award ID)")
    name: str = Field(..., description="Grant name or title")
    funder: str = Field(..., description="Funder or awarding agency")
    year: int = Field(..., description="Year the grant was awarded or applied for")
    amount: float = Field(..., description="Amount awarded or applied for")
    status: str = Field(..., description="Status: 'won', 'applied', 'pending', etc.")
    url: Optional[str] = Field(None, description="URL to grant details")
    next_estimated_open: Optional[str] = Field(None, description="Estimated next open date/cycle")


class OrganizationProfile(BaseModel):
    """Model representing a non-profit organization profile."""
    
    name: str = Field(..., description="Organization name")
    description: str = Field("", description="Organization description")
    focus_areas: List[FocusArea] = Field(
        default_factory=list, 
        description="Primary focus areas of the organization"
    )
    program_types: List[ProgramType] = Field(
        default_factory=list,
        description="Types of programs offered"
    )
    target_demographics: List[str] = Field(
        default_factory=list,
        description="Target demographics served"
    )
    annual_budget: Optional[int] = Field(
        None, 
        description="Annual operating budget in USD"
    )
    location: str = Field("", description="Primary location of operations")
    website: Optional[str] = Field(None, description="Organization website")
    ein: Optional[str] = Field(None, description="Employer Identification Number")
    founded_year: Optional[int] = Field(None, description="Year organization was founded")
    
    # Grant application preferences
    preferred_grant_size: tuple[int, int] = Field(
        (10000, 100000), 
        description="Preferred grant amount range (min, max)"
    )
    grant_history: List[str] = Field(
        default_factory=list,
        description="List of previously received grants"
    )
    
    # Contact information
    contact_name: str = Field("", description="Primary contact name")
    contact_email: str = Field("", description="Primary contact email")
    contact_phone: str = Field("", description="Primary contact phone")
    
    past_grants: List[PastGrant] = Field(
        default_factory=list,
        description="List of past grants awarded or applied for"
    )
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        
    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()
    
    def add_focus_area(self, focus_area: FocusArea) -> None:
        """Add a focus area if not already present."""
        if focus_area not in self.focus_areas:
            self.focus_areas.append(focus_area)
            self.update_timestamp()
    
    def add_program_type(self, program_type: ProgramType) -> None:
        """Add a program type if not already present."""
        if program_type not in self.program_types:
            self.program_types.append(program_type)
            self.update_timestamp()
    
    def is_eligible_for_amount(self, amount: int) -> bool:
        """Check if the organization would be eligible for a grant amount."""
        min_amount, max_amount = self.preferred_grant_size
        return min_amount <= amount <= max_amount
    
    def get_focus_keywords(self) -> List[str]:
        """Get keywords related to focus areas for matching."""
        keywords = []
        for area in self.focus_areas:
            if area == FocusArea.MUSIC_EDUCATION:
                keywords.extend(["music", "musical", "arts", "education"])
            elif area == FocusArea.ART_EDUCATION:
                keywords.extend(["art", "arts", "creative", "education"])
            elif area == FocusArea.ROBOTICS:
                keywords.extend(["robotics", "STEM", "technology", "engineering"])
            elif area == FocusArea.AFFORDABLE_HOUSING:
                keywords.extend(["housing", "affordable", "residential", "community"])
            elif area == FocusArea.EDUCATION:
                keywords.extend(["education", "learning", "academic", "school"])
            # Add more keyword mappings as needed
        return list(set(keywords))  # Remove duplicates
