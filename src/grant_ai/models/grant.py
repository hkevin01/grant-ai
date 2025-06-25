"""Data models for grants and funding opportunities."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class GrantStatus(str, Enum):
    """Enumeration of grant application statuses."""
    OPEN = "open"
    CLOSED = "closed"
    UPCOMING = "upcoming"
    ROLLING = "rolling"
    EXPIRED = "expired"


class FundingType(str, Enum):
    """Enumeration of funding types."""
    GRANT = "grant"
    FELLOWSHIP = "fellowship"
    SCHOLARSHIP = "scholarship"
    AWARD = "award"
    SPONSORSHIP = "sponsorship"
    DONATION = "donation"


class EligibilityType(str, Enum):
    """Enumeration of eligibility types."""
    NONPROFIT = "nonprofit"
    EDUCATION = "education"
    INDIVIDUAL = "individual"
    STARTUP = "startup"
    RESEARCH = "research"
    COMMUNITY = "community"


class Grant(BaseModel):
    """Model representing a grant opportunity."""
    
    id: str = Field(..., description="Unique grant identifier")
    title: str = Field(..., description="Grant title")
    description: str = Field("", description="Grant description")
    funder_name: str = Field(..., description="Name of funding organization")
    funder_type: str = Field("", description="Type of funder (foundation, government, etc.)")
    
    # Funding details
    funding_type: FundingType = Field(FundingType.GRANT, description="Type of funding")
    amount_min: Optional[int] = Field(None, description="Minimum grant amount")
    amount_max: Optional[int] = Field(None, description="Maximum grant amount")
    amount_typical: Optional[int] = Field(None, description="Typical grant amount")
    total_funding_available: Optional[int] = Field(None, description="Total funding pool")
    
    # Timing
    status: GrantStatus = Field(GrantStatus.OPEN, description="Current grant status")
    application_deadline: Optional[date] = Field(None, description="Application deadline")
    decision_date: Optional[date] = Field(None, description="Expected decision date")
    funding_start_date: Optional[date] = Field(None, description="Funding period start")
    funding_duration_months: Optional[int] = Field(None, description="Funding duration in months")
    
    # Eligibility and focus
    eligibility_types: List[EligibilityType] = Field(
        default_factory=list, 
        description="Types of eligible applicants"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Grant focus areas and keywords"
    )
    geographic_restrictions: List[str] = Field(
        default_factory=list,
        description="Geographic limitations"
    )
    
    # Requirements
    application_requirements: List[str] = Field(
        default_factory=list,
        description="Required application materials"
    )
    reporting_requirements: List[str] = Field(
        default_factory=list,
        description="Post-award reporting requirements"
    )
    matching_funds_required: bool = Field(False, description="Whether matching funds are required")
    matching_percentage: Optional[float] = Field(None, description="Required matching percentage")
    
    # Links and contacts
    application_url: Optional[HttpUrl] = Field(None, description="Application URL")
    information_url: Optional[HttpUrl] = Field(None, description="Information URL")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    
    # Metadata
    source: str = Field("", description="Data source")
    source_url: Optional[HttpUrl] = Field(None, description="Source URL")
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Scoring and matching
    relevance_score: Optional[float] = Field(None, description="Relevance score for matching")
    match_reasons: List[str] = Field(
        default_factory=list,
        description="Reasons for organization match"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
    
    def is_currently_open(self) -> bool:
        """Check if the grant is currently accepting applications."""
        if self.status == GrantStatus.ROLLING:
            return True
        if self.status == GrantStatus.OPEN and self.application_deadline:
            return date.today() <= self.application_deadline
        return self.status == GrantStatus.OPEN
    
    def is_amount_suitable(self, min_amount: int, max_amount: int) -> bool:
        """Check if grant amount range is suitable for organization needs."""
        if self.amount_min and self.amount_max:
            # Check if there's any overlap between ranges
            return not (max_amount < self.amount_min or min_amount > self.amount_max)
        elif self.amount_typical:
            return min_amount <= self.amount_typical <= max_amount
        return True  # If no amount info, assume it could be suitable
    
    def matches_focus_areas(self, keywords: List[str]) -> bool:
        """Check if grant focus areas match organization keywords."""
        if not self.focus_areas or not keywords:
            return False
        
        grant_keywords = [area.lower() for area in self.focus_areas]
        org_keywords = [keyword.lower() for keyword in keywords]
        
        return any(
            any(grant_keyword in org_keyword or org_keyword in grant_keyword 
                for grant_keyword in grant_keywords)
            for org_keyword in org_keywords
        )
    
    def calculate_relevance_score(self, organization_keywords: List[str], 
                                 org_budget: Optional[int] = None) -> float:
        """Calculate relevance score for an organization."""
        score = 0.0
        
        # Focus area matching (40% of score)
        if self.matches_focus_areas(organization_keywords):
            score += 0.4
        
        # Amount suitability (30% of score)
        if org_budget and self.amount_typical:
            budget_ratio = self.amount_typical / org_budget
            if 0.1 <= budget_ratio <= 0.5:  # 10-50% of budget is ideal
                score += 0.3
            elif 0.05 <= budget_ratio <= 0.8:  # 5-80% is acceptable
                score += 0.2
        elif not self.amount_typical:  # No amount specified
            score += 0.15
        
        # Status and timing (20% of score)
        if self.is_currently_open():
            score += 0.2
        elif self.status == GrantStatus.UPCOMING:
            score += 0.1
        
        # Eligibility (10% of score)
        if EligibilityType.NONPROFIT in self.eligibility_types:
            score += 0.1
        
        self.relevance_score = score
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert grant to dictionary for export."""
        return {
            "id": self.id,
            "title": self.title,
            "funder_name": self.funder_name,
            "amount_min": self.amount_min,
            "amount_max": self.amount_max,
            "amount_typical": self.amount_typical,
            "deadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "status": self.status,
            "focus_areas": ", ".join(self.focus_areas),
            "application_url": str(self.application_url) if self.application_url else None,
            "relevance_score": self.relevance_score,
            "match_reasons": ", ".join(self.match_reasons)
        }
