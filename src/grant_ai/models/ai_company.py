"""Data models for AI companies and their grant programs."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class CompanySize(str, Enum):
    """Enumeration of company sizes."""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class AIFocusArea(str, Enum):
    """Enumeration of AI focus areas."""
    MACHINE_LEARNING = "machine_learning"
    NATURAL_LANGUAGE = "natural_language"
    COMPUTER_VISION = "computer_vision"
    ROBOTICS = "robotics"
    EDUCATION_TECH = "education_tech"
    HEALTHCARE = "healthcare"
    AUTONOMOUS_SYSTEMS = "autonomous_systems"
    DATA_ANALYTICS = "data_analytics"
    SOCIAL_IMPACT = "social_impact"


class ReputationRating(str, Enum):
    """Enumeration of reputation ratings."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"


class AICompany(BaseModel):
    """Model representing an AI company and their grant programs."""
    
    id: str = Field(..., description="Unique company identifier")
    name: str = Field(..., description="Company name")
    description: str = Field("", description="Company description")
    website: Optional[HttpUrl] = Field(None, description="Company website")
    
    # Company details
    size: Optional[CompanySize] = Field(None, description="Company size")
    founded_year: Optional[int] = Field(None, description="Year company was founded")
    headquarters: str = Field("", description="Company headquarters location")
    employee_count: Optional[int] = Field(None, description="Number of employees")
    
    # AI focus and capabilities
    ai_focus_areas: List[AIFocusArea] = Field(
        default_factory=list,
        description="Primary AI focus areas"
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Key technologies and platforms"
    )
    
    # Grant program information
    has_grant_program: bool = Field(False, description="Whether company has grant programs")
    grant_program_name: Optional[str] = Field(None, description="Name of grant program")
    grant_program_url: Optional[HttpUrl] = Field(None, description="Grant program URL")
    grant_focus_areas: List[str] = Field(
        default_factory=list,
        description="Focus areas for grants"
    )
    typical_grant_amount: Optional[int] = Field(None, description="Typical grant amount")
    annual_grant_budget: Optional[int] = Field(None, description="Annual grant budget")
    
    # Target demographics for grants
    target_demographics: List[str] = Field(
        default_factory=list,
        description="Target demographics for grant programs"
    )
    supported_organization_types: List[str] = Field(
        default_factory=list,
        description="Types of organizations they support"
    )
    
    # Reputation and assessment
    reputation_rating: ReputationRating = Field(
        ReputationRating.UNKNOWN,
        description="Overall reputation rating"
    )
    reputation_factors: Dict[str, Any] = Field(
        default_factory=dict,
        description="Factors contributing to reputation score"
    )
    
    # Social impact and CSR
    social_impact_focus: List[str] = Field(
        default_factory=list,
        description="Social impact focus areas"
    )
    csr_initiatives: List[str] = Field(
        default_factory=list,
        description="Corporate social responsibility initiatives"
    )
    diversity_initiatives: bool = Field(False, description="Has diversity/inclusion initiatives")
    
    # Financial and business metrics
    revenue_range: Optional[str] = Field(None, description="Revenue range")
    funding_received: Optional[int] = Field(None, description="Total funding received")
    valuation: Optional[int] = Field(None, description="Company valuation")
    
    # Contact and application information
    grant_contact_email: Optional[str] = Field(None, description="Grant program contact email")
    application_process: Optional[str] = Field(None, description="Application process description")
    application_requirements: List[str] = Field(
        default_factory=list,
        description="Grant application requirements"
    )
    
    # Metadata
    data_sources: List[str] = Field(
        default_factory=list,
        description="Sources of information"
    )
    last_updated: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Scoring for organization matching
    match_score: Optional[float] = Field(None, description="Match score for specific organization")
    match_reasons: List[str] = Field(
        default_factory=list,
        description="Reasons for organization match"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
    
    def calculate_reputation_score(self) -> float:
        """Calculate numerical reputation score based on various factors."""
        score = 0.0
        factors = self.reputation_factors
        
        # Base score from rating
        rating_scores = {
            ReputationRating.EXCELLENT: 1.0,
            ReputationRating.GOOD: 0.8,
            ReputationRating.FAIR: 0.6,
            ReputationRating.POOR: 0.2,
            ReputationRating.UNKNOWN: 0.5
        }
        score += rating_scores.get(self.reputation_rating, 0.5) * 0.4
        
        # Company age and stability (20%)
        if self.founded_year:
            age = datetime.now().year - self.founded_year
            if age >= 10:
                score += 0.2
            elif age >= 5:
                score += 0.15
            elif age >= 2:
                score += 0.1
        
        # Grant program existence and quality (30%)
        if self.has_grant_program:
            score += 0.15
            if self.grant_program_url:
                score += 0.05
            if self.typical_grant_amount and self.typical_grant_amount >= 10000:
                score += 0.1
        
        # Social impact focus (10%)
        if self.social_impact_focus or self.diversity_initiatives:
            score += 0.1
        
        return min(score, 1.0)
    
    def matches_organization_focus(self, org_focus_keywords: List[str]) -> bool:
        """Check if company's grant focus matches organization needs."""
        if not self.grant_focus_areas:
            return False
            
        company_keywords = [area.lower() for area in self.grant_focus_areas]
        org_keywords = [keyword.lower() for keyword in org_focus_keywords]
        
        return any(
            any(company_keyword in org_keyword or org_keyword in company_keyword
                for company_keyword in company_keywords)
            for org_keyword in org_keywords
        )
    
    def calculate_match_score(self, organization_keywords: List[str],
                            organization_budget: Optional[int] = None,
                            organization_type: str = "nonprofit") -> float:
        """Calculate match score for a specific organization."""
        score = 0.0
        
        # Must have grant program to be relevant
        if not self.has_grant_program:
            self.match_score = 0.0
            return 0.0
        
        # Focus area alignment (40%)
        if self.matches_organization_focus(organization_keywords):
            score += 0.4
            self.match_reasons.append("Focus areas align with organization needs")
        
        # Grant amount suitability (25%)
        if self.typical_grant_amount and organization_budget:
            budget_ratio = self.typical_grant_amount / organization_budget
            if 0.1 <= budget_ratio <= 0.5:
                score += 0.25
                self.match_reasons.append("Grant amount suitable for organization size")
            elif 0.05 <= budget_ratio <= 0.8:
                score += 0.15
        elif self.typical_grant_amount and self.typical_grant_amount >= 10000:
            score += 0.1
        
        # Organization type support (15%)
        if organization_type.lower() in [ot.lower() for ot in self.supported_organization_types]:
            score += 0.15
            self.match_reasons.append("Supports this type of organization")
        elif "nonprofit" in [ot.lower() for ot in self.supported_organization_types]:
            score += 0.1
        
        # Company reputation (20%)
        reputation_score = self.calculate_reputation_score()
        score += reputation_score * 0.2
        if reputation_score >= 0.8:
            self.match_reasons.append("Excellent company reputation")
        elif reputation_score >= 0.6:
            self.match_reasons.append("Good company reputation")
        
        self.match_score = score
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert company to dictionary for export."""
        return {
            "id": self.id,
            "name": self.name,
            "website": str(self.website) if self.website else None,
            "has_grant_program": self.has_grant_program,
            "grant_program_name": self.grant_program_name,
            "grant_program_url": str(self.grant_program_url) if self.grant_program_url else None,
            "typical_grant_amount": self.typical_grant_amount,
            "grant_focus_areas": ", ".join(self.grant_focus_areas),
            "target_demographics": ", ".join(self.target_demographics),
            "reputation_rating": self.reputation_rating,
            "social_impact_focus": ", ".join(self.social_impact_focus),
            "match_score": self.match_score,
            "match_reasons": ", ".join(self.match_reasons)
        }
