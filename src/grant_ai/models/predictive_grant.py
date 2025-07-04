"""
Predictive grant model for tracking annually recurring grant opportunities.
Used to identify grants that typically open each year but haven't been posted yet.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class PredictiveStatus(Enum):
    """Status of predictive grant predictions."""
    EXPECTED = "Expected"
    OVERDUE = "Overdue" 
    EARLY = "Early"
    POSTED = "Posted"
    CANCELLED = "Cancelled"


class RecurrencePattern(Enum):
    """Pattern for grant recurrence."""
    ANNUAL = "Annual"
    BIANNUAL = "Biannual"
    QUARTERLY = "Quarterly"
    IRREGULAR = "Irregular"


@dataclass
class HistoricalData:
    """Historical data for a recurring grant."""
    year: int
    posted_date: date
    deadline_date: date
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None
    actual_awards: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    notes: str = ""


@dataclass
class PredictiveGrant:
    """
    Model for predictive grant opportunities.
    
    Tracks grants that typically recur annually and predicts when
    they might be posted based on historical patterns.
    """
    
    # Required fields (no defaults) must come first
    title: str
    agency: str
    predicted_post_date: date
    predicted_deadline: date
    
    # Optional fields (with defaults) come after
    program_code: Optional[str] = None
    confidence_score: float = 0.0  # 0.0 to 1.0
    status: PredictiveStatus = PredictiveStatus.EXPECTED
    
    # Grant Details
    description: str = ""
    focus_areas: List[str] = field(default_factory=list)
    eligibility_criteria: List[str] = field(default_factory=list)
    
    # Financial Information
    predicted_amount_min: Optional[int] = None
    predicted_amount_max: Optional[int] = None
    typical_award_count: Optional[int] = None
    
    # Historical Pattern
    recurrence_pattern: RecurrencePattern = RecurrencePattern.ANNUAL
    historical_data: List[HistoricalData] = field(default_factory=list)
    years_tracked: int = 0
    
    # Matching Information
    organization_match_score: float = 0.0
    relevance_keywords: List[str] = field(default_factory=list)
    past_application_attempts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Tracking
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    source_urls: List[str] = field(default_factory=list)
    
    def days_until_predicted_posting(self) -> int:
        """Calculate days until predicted posting date."""
        today = date.today()
        delta = self.predicted_post_date - today
        return delta.days
    
    def days_until_predicted_deadline(self) -> int:
        """Calculate days until predicted deadline."""
        today = date.today()
        delta = self.predicted_deadline - today
        return delta.days
    
    def update_status(self) -> None:
        """Update status based on current date and predictions."""
        today = date.today()
        days_until_post = self.days_until_predicted_posting()
        
        if days_until_post > 30:
            self.status = PredictiveStatus.EARLY
        elif days_until_post > -30:
            self.status = PredictiveStatus.EXPECTED
        else:
            self.status = PredictiveStatus.OVERDUE
    
    def get_historical_average_amount(self) -> Optional[Dict[str, int]]:
        """Calculate average grant amounts from historical data."""
        if not self.historical_data:
            return None
        
        min_amounts = [h.amount_min for h in self.historical_data if h.amount_min]
        max_amounts = [h.amount_max for h in self.historical_data if h.amount_max]
        
        result = {}
        if min_amounts:
            result['avg_min'] = sum(min_amounts) // len(min_amounts)
        if max_amounts:
            result['avg_max'] = sum(max_amounts) // len(max_amounts)
        
        return result if result else None
    
    def add_historical_data(self, historical_entry: HistoricalData) -> None:
        """Add historical data point and update predictions."""
        self.historical_data.append(historical_entry)
        self.years_tracked = len(self.historical_data)
        self._update_predictions()
    
    def _update_predictions(self) -> None:
        """Update predictions based on historical data."""
        if len(self.historical_data) < 2:
            return
        
        # Calculate average posting dates
        posting_days = []
        deadline_days = []
        
        for data in self.historical_data:
            posting_days.append(data.posted_date.timetuple().tm_yday)
            deadline_days.append(data.deadline_date.timetuple().tm_yday)
        
        if posting_days:
            avg_posting_day = sum(posting_days) // len(posting_days)
            current_year = date.today().year
            # Handle year transitions
            try:
                self.predicted_post_date = date(current_year, 1, 1) + \
                                         timedelta(days=avg_posting_day - 1)
            except ValueError:
                # If day calculation is invalid, use original prediction
                pass
        
        if deadline_days:
            avg_deadline_day = sum(deadline_days) // len(deadline_days)
            current_year = date.today().year
            try:
                self.predicted_deadline = date(current_year, 1, 1) + \
                                        timedelta(days=avg_deadline_day - 1)
            except ValueError:
                # If day calculation is invalid, use original prediction
                pass
        
        # Update confidence based on consistency
        self.confidence_score = min(0.9, self.years_tracked * 0.15)
        
        # Update amounts
        avg_amounts = self.get_historical_average_amount()
        if avg_amounts:
            self.predicted_amount_min = avg_amounts.get('avg_min')
            self.predicted_amount_max = avg_amounts.get('avg_max')


@dataclass 
@dataclass
class PredictiveGrantDatabase:
    """Database for managing predictive grants."""
    
    grants: List[PredictiveGrant] = field(default_factory=list)
    
    def add_grant(self, grant: PredictiveGrant) -> None:
        """Add a predictive grant to the database."""
        self.grants.append(grant)
    
    def get_all_grants(self) -> List[PredictiveGrant]:
        """Get all grants in the database."""
        return self.grants.copy()
    
    def get_grants_for_organization(self, 
                                  focus_areas: List[str],
                                  min_match_score: float = 0.3) -> List[PredictiveGrant]:
        """Get predictive grants matching organization focus areas."""
        matching_grants = []
        
        for grant in self.grants:
            # Calculate match score based on focus area overlap
            focus_overlap = set(focus_areas).intersection(set(grant.focus_areas))
            match_score = len(focus_overlap) / max(len(grant.focus_areas), 1)
            
            if match_score >= min_match_score:
                grant.organization_match_score = match_score
                matching_grants.append(grant)
        
        # Sort by match score and confidence
        return sorted(matching_grants, 
                     key=lambda g: (g.organization_match_score, g.confidence_score),
                     reverse=True)
    
    def get_grants_by_status(self, status: PredictiveStatus) -> List[PredictiveGrant]:
        """Get grants filtered by status."""
        return [g for g in self.grants if g.status == status]
    
    def update_all_statuses(self) -> None:
        """Update status for all grants."""
        for grant in self.grants:
            grant.update_status()


def create_sample_predictive_grants() -> List[PredictiveGrant]:
    """Create sample predictive grants for CODA and NRG Development."""
    
    grants = []
    
    # Education grants for CODA
    stem_grant = PredictiveGrant(
        title="STEM Education Innovation Grant (Annual)",
        agency="West Virginia Department of Education",
        program_code="WV-STEM-2025",
        predicted_post_date=date(2025, 8, 15),
        predicted_deadline=date(2025, 11, 30),
        confidence_score=0.85,
        description="Annual funding for innovative STEM education programs including robotics, technology integration, and hands-on learning experiences for K-12 students.",
        focus_areas=["education", "stem", "technology", "robotics", "youth"],
        eligibility_criteria=["Non-profit educational organizations", "After-school programs", "Youth development"],
        predicted_amount_min=15000,
        predicted_amount_max=75000,
        typical_award_count=12,
        years_tracked=4,
        relevance_keywords=["music technology", "robotics education", "after-school STEM"]
    )
    
    # Add historical data for STEM grant
    stem_grant.add_historical_data(HistoricalData(
        year=2024,
        posted_date=date(2024, 8, 12),
        deadline_date=date(2024, 11, 28),
        amount_min=15000,
        amount_max=75000,
        notes="Funded 12 programs statewide"
    ))
    
    stem_grant.add_historical_data(HistoricalData(
        year=2023,
        posted_date=date(2023, 8, 18),
        deadline_date=date(2023, 12, 1),
        amount_min=12000,
        amount_max=65000,
        notes="Funded 10 programs"
    ))
    
    grants.append(stem_grant)
    
    # Arts education grant for CODA
    arts_grant = PredictiveGrant(
        title="Community Arts Education Grant (Annual)",
        agency="West Virginia Arts Council",
        program_code="WV-ARTS-ED-2025",
        predicted_post_date=date(2025, 9, 1),
        predicted_deadline=date(2025, 12, 15),
        confidence_score=0.78,
        description="Annual funding for community-based arts education programs including music education, visual arts, and creative expression for youth.",
        focus_areas=["arts", "education", "music", "community", "youth"],
        eligibility_criteria=["Non-profit arts organizations", "Educational programs", "Community groups"],
        predicted_amount_min=8000,
        predicted_amount_max=45000,
        typical_award_count=8,
        years_tracked=3,
        relevance_keywords=["music education", "community arts", "youth arts"]
    )
    
    grants.append(arts_grant)
    
    # Housing grant for NRG Development
    housing_grant = PredictiveGrant(
        title="Rural Affordable Housing Development Fund (Annual)",
        agency="USDA Rural Development",
        program_code="USDA-RAHD-2025",
        predicted_post_date=date(2025, 10, 1),
        predicted_deadline=date(2026, 1, 31),
        confidence_score=0.92,
        description="Annual funding for affordable housing development in rural communities, with priority for senior housing and family-supportive communities.",
        focus_areas=["housing", "rural development", "seniors", "affordable housing"],
        eligibility_criteria=["Non-profit housing developers", "Rural communities", "Low-income focus"],
        predicted_amount_min=250000,
        predicted_amount_max=2000000,
        typical_award_count=6,
        years_tracked=5,
        relevance_keywords=["senior housing", "affordable development", "rural communities"]
    )
    
    # Add historical data for housing grant
    housing_grant.add_historical_data(HistoricalData(
        year=2024,
        posted_date=date(2024, 9, 28),
        deadline_date=date(2025, 1, 30),
        amount_min=300000,
        amount_max=1800000,
        notes="6 awards made, priority for senior housing"
    ))
    
    grants.append(housing_grant)
    
    # Senior services grant for NRG Development
    senior_grant = PredictiveGrant(
        title="Community Support for Seniors Grant (Annual)",
        agency="West Virginia Bureau of Senior Services",
        program_code="WV-CSS-2025",
        predicted_post_date=date(2025, 7, 15),
        predicted_deadline=date(2025, 10, 31),
        confidence_score=0.71,
        description="Annual funding for programs supporting seniors in community settings, including housing support services and community integration programs.",
        focus_areas=["seniors", "community support", "social services", "housing support"],
        eligibility_criteria=["Non-profit service providers", "Senior-focused programs", "Community organizations"],
        predicted_amount_min=5000,
        predicted_amount_max=35000,
        typical_award_count=15,
        years_tracked=3,
        relevance_keywords=["senior support", "community services", "housing assistance"]
    )
    
    grants.append(senior_grant)
    
    # Technology education grant for CODA
    tech_grant = PredictiveGrant(
        title="Digital Divide Education Initiative (Annual)",
        agency="Federal Communications Commission",
        program_code="FCC-DDEI-2025",
        predicted_post_date=date(2025, 6, 30),
        predicted_deadline=date(2025, 9, 30),
        confidence_score=0.88,
        description="Annual funding to bridge the digital divide through technology education programs, equipment provision, and digital literacy training.",
        focus_areas=["technology", "education", "digital literacy", "equipment"],
        eligibility_criteria=["Educational organizations", "Non-profits", "Community programs"],
        predicted_amount_min=25000,
        predicted_amount_max=150000,
        typical_award_count=20,
        years_tracked=4,
        relevance_keywords=["technology education", "digital access", "equipment grants"]
    )
    
    grants.append(tech_grant)
    
    return grants
