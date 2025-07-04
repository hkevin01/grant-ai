"""
Enhanced past grant model with detailed information and document links.
"""

import os
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DocumentType(Enum):
    """Types of grant documents."""
    APPLICATION = "Application"
    PROPOSAL = "Proposal"
    BUDGET = "Budget"
    NARRATIVE = "Narrative"
    SUPPORTING_DOCS = "Supporting Documents"
    AWARD_LETTER = "Award Letter"
    PROGRESS_REPORT = "Progress Report"
    FINAL_REPORT = "Final Report"
    CORRESPONDENCE = "Correspondence"


@dataclass
class GrantDocument:
    """Model for grant-related documents."""
    name: str
    document_type: DocumentType
    file_path: Optional[str] = None
    url: Optional[str] = None
    upload_date: datetime = field(default_factory=datetime.now)
    file_size: Optional[int] = None
    description: str = ""
    is_confidential: bool = False
    
    def exists(self) -> bool:
        """Check if the document file exists."""
        if self.file_path and os.path.isfile(self.file_path):
            return True
        return False
    
    def get_size_formatted(self) -> str:
        """Get formatted file size."""
        if not self.file_size:
            return "Unknown"
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size // 1024} KB"
        else:
            return f"{self.file_size // (1024 * 1024)} MB"


@dataclass
class GrantMilestone:
    """Model for grant milestones and deliverables."""
    title: str
    description: str
    due_date: date
    completion_date: Optional[date] = None
    status: str = "Pending"  # Pending, In Progress, Completed, Overdue
    notes: str = ""
    
    def is_overdue(self) -> bool:
        """Check if milestone is overdue."""
        if self.status == "Completed":
            return False
        return date.today() > self.due_date
    
    def days_until_due(self) -> int:
        """Calculate days until due date."""
        delta = self.due_date - date.today()
        return delta.days


@dataclass
class BudgetItem:
    """Model for budget line items."""
    category: str
    description: str
    budgeted_amount: float
    actual_amount: Optional[float] = None
    variance: Optional[float] = None
    notes: str = ""
    
    def calculate_variance(self) -> float:
        """Calculate variance between budgeted and actual amounts."""
        if self.actual_amount is not None:
            self.variance = self.actual_amount - self.budgeted_amount
            return self.variance
        return 0.0
    
    def get_variance_percentage(self) -> float:
        """Get variance as percentage of budgeted amount."""
        if self.budgeted_amount == 0:
            return 0.0
        variance = self.calculate_variance()
        return (variance / self.budgeted_amount) * 100


@dataclass
class EnhancedPastGrant:
    """Enhanced model for past grants with detailed information."""
    
    # Required fields (no defaults) must come first
    funder: str
    title: str
    amount: float
    year: int
    type: str  # Federal, State, Foundation, Corporate, etc.
    purpose: str
    status: str  # Received, In Progress, Completed, Denied
    
    # Optional fields (with defaults) come after
    organization: str = ""  # The organization that received the grant
    program_name: Optional[str] = None
    grant_number: Optional[str] = None
    project_period_start: Optional[date] = None
    project_period_end: Optional[date] = None
    application_date: Optional[date] = None
    notification_date: Optional[date] = None
    project_director: Optional[str] = None
    collaborating_organizations: List[str] = field(default_factory=list)
    
    # Financial Details
    total_project_cost: Optional[float] = None
    match_required: Optional[float] = None
    match_provided: Optional[float] = None
    budget_items: List[BudgetItem] = field(default_factory=list)
    
    # Project Management
    milestones: List[GrantMilestone] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    
    # Documents
    documents: List[GrantDocument] = field(default_factory=list)
    
    # Outcomes and Impact
    beneficiaries_served: Optional[int] = None
    impact_metrics: Dict[str, Any] = field(default_factory=dict)
    success_stories: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    
    # Administrative
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def add_document(self, document: GrantDocument) -> None:
        """Add a document to this grant."""
        self.documents.append(document)
        self.last_updated = datetime.now()
    
    def get_documents_by_type(self, 
                             doc_type: DocumentType) -> List[GrantDocument]:
        """Get all documents of a specific type."""
        return [doc for doc in self.documents 
                if doc.document_type == doc_type]
    
    def add_milestone(self, milestone: GrantMilestone) -> None:
        """Add a milestone to this grant."""
        self.milestones.append(milestone)
        self.last_updated = datetime.now()
    
    def get_completion_percentage(self) -> float:
        """Calculate project completion percentage based on milestones."""
        if not self.milestones:
            return 0.0
        
        completed = len([m for m in self.milestones 
                        if m.status == "Completed"])
        return (completed / len(self.milestones)) * 100
    
    def get_budget_summary(self) -> Dict[str, float]:
        """Get budget summary information."""
        if not self.budget_items:
            return {
                "total_budgeted": self.amount, 
                "total_actual": 0.0, 
                "variance": 0.0
            }
        
        total_budgeted = sum(item.budgeted_amount for item in self.budget_items)
        total_actual = sum(item.actual_amount or 0 for item in self.budget_items)
        variance = total_actual - total_budgeted
        
        return {
            "total_budgeted": total_budgeted,
            "total_actual": total_actual,
            "variance": variance,
            "variance_percentage": (variance / total_budgeted * 100) 
                                 if total_budgeted else 0
        }
    
    def get_overdue_milestones(self) -> List[GrantMilestone]:
        """Get all overdue milestones."""
        return [m for m in self.milestones if m.is_overdue()]
    
    def get_upcoming_milestones(self, days: int = 30) -> List[GrantMilestone]:
        """Get milestones due within specified days."""
        return [m for m in self.milestones 
                if 0 <= m.days_until_due() <= days 
                and m.status != "Completed"]


def create_enhanced_sample_past_grants() -> List[EnhancedPastGrant]:
    """Create sample enhanced past grants for CODA."""
    grants = []
    
    # CODA STEM Education Grant
    stem_grant = EnhancedPastGrant(
        funder="West Virginia Department of Education",
        title="STEM Innovation Grant - Robotics Program",
        amount=45000,
        year=2023,
        type="State",
        purpose="Implementing robotics education and maker space",
        status="Completed",
        organization="Coda Mountain Academy",
        program_name="WV STEM Innovation Initiative",
        grant_number="WV-STEM-2023-015",
        project_period_start=date(2023, 7, 1),
        project_period_end=date(2024, 6, 30),
        application_date=date(2023, 3, 15),
        notification_date=date(2023, 5, 20),
        project_director="Sarah Johnson",
        collaborating_organizations=[
            "WV University Engineering Dept", 
            "Local High School"
        ],
        total_project_cost=55000,
        match_required=10000,
        match_provided=12000,
        beneficiaries_served=85,
        impact_metrics={
            "students_served": 85,
            "teachers_trained": 12,
            "robotics_kits_purchased": 15,
            "maker_space_items": 25
        },
        success_stories=[
            "3 students won state robotics competition",
            "Teacher received state innovation award",
            "Program featured in local news"
        ],
        lessons_learned=[
            "Start teacher training earlier in the project",
            "Plan for more storage space for equipment",
            "Involve parents in showcase events"
        ],
        tags=["robotics", "STEM", "education", "youth"]
    )
    
    # Add budget items
    stem_grant.budget_items = [
        BudgetItem("Equipment", "Robotics kits and sensors", 
                  25000, 24500, -500),
        BudgetItem("Training", "Teacher professional development", 
                  8000, 8200, 200),
        BudgetItem("Materials", "Maker space supplies", 
                  7000, 6800, -200),
        BudgetItem("Personnel", "Part-time coordinator", 
                  5000, 5000, 0)
    ]
    
    # Add milestones
    stem_grant.milestones = [
        GrantMilestone(
            "Equipment Purchase", 
            "Purchase robotics kits", 
            date(2023, 8, 15), 
            date(2023, 8, 10), 
            "Completed"
        ),
        GrantMilestone(
            "Teacher Training", 
            "Complete teacher workshops", 
            date(2023, 9, 30), 
            date(2023, 9, 25), 
            "Completed"
        ),
        GrantMilestone(
            "Student Program Launch", 
            "Begin student activities", 
            date(2023, 10, 15), 
            date(2023, 10, 12), 
            "Completed"
        ),
        GrantMilestone(
            "Mid-Year Assessment", 
            "Evaluate progress", 
            date(2024, 1, 31), 
            date(2024, 1, 28), 
            "Completed"
        ),
        GrantMilestone(
            "Final Showcase", 
            "Student demonstration event", 
            date(2024, 5, 15), 
            date(2024, 5, 18), 
            "Completed"
        )
    ]
    
    # Add documents (using sample paths for demonstration)
    stem_grant.documents = [
        GrantDocument(
            "Original Application", 
            DocumentType.APPLICATION, 
            "/documents/stem_grant_application_2023.pdf",
            description="Complete grant application with narrative and budget"
        ),
        GrantDocument(
            "Project Budget", 
            DocumentType.BUDGET, 
            "/documents/stem_grant_budget_2023.xlsx",
            description="Detailed budget breakdown by category"
        ),
        GrantDocument(
            "Award Letter", 
            DocumentType.AWARD_LETTER, 
            "/documents/stem_grant_award_2023.pdf",
            description="Official award notification"
        ),
        GrantDocument(
            "Mid-Year Report", 
            DocumentType.PROGRESS_REPORT, 
            "/documents/stem_grant_midyear_2024.pdf",
            description="Progress report submitted at project midpoint"
        ),
        GrantDocument(
            "Final Report", 
            DocumentType.FINAL_REPORT, 
            "/documents/stem_grant_final_2024.pdf",
            description="Comprehensive final project report"
        ),
        GrantDocument(
            "Student Showcase Photos", 
            DocumentType.SUPPORTING_DOCS, 
            "/documents/stem_showcase_photos_2024/",
            description="Photos and videos from student demonstration event"
        )
    ]
    
    grants.append(stem_grant)
    
    # CODA Arts Education Grant
    arts_grant = EnhancedPastGrant(
        funder="West Virginia Arts Council",
        title="Community Music Education Program",
        amount=18000,
        year=2024,
        type="State",
        purpose="Expanding music education and community performances",
        status="In Progress",
        organization="Coda Mountain Academy",
        program_name="Arts in Education Grant Program",
        grant_number="WV-ARTS-2024-008",
        project_period_start=date(2024, 1, 1),
        project_period_end=date(2024, 12, 31),
        application_date=date(2023, 10, 15),
        notification_date=date(2023, 12, 8),
        project_director="Michael Rodriguez",
        collaborating_organizations=[
            "Community Music Society", 
            "Local Theater Group"
        ],
        total_project_cost=22000,
        match_required=4000,
        match_provided=4000,
        beneficiaries_served=45,
        impact_metrics={
            "students_in_program": 45,
            "community_performances": 4,
            "instruments_purchased": 12,
            "volunteer_hours": 150
        },
        tags=["music", "arts", "community", "performance"]
    )
    
    # Add budget items for arts grant
    arts_grant.budget_items = [
        BudgetItem("Instruments", "Student instruments and equipment", 
                  12000, 11800, -200),
        BudgetItem("Instruction", "Music teacher stipends", 
                  4000, 2000, -2000, "Partially completed"),
        BudgetItem("Events", "Performance and recital costs", 
                  2000, 1500, -500),
    ]
    
    # Add milestones for arts grant
    arts_grant.milestones = [
        GrantMilestone(
            "Instrument Purchase", 
            "Buy student instruments", 
            date(2024, 2, 28), 
            date(2024, 2, 25), 
            "Completed"
        ),
        GrantMilestone(
            "Spring Concert", 
            "First community performance", 
            date(2024, 4, 15), 
            date(2024, 4, 20), 
            "Completed"
        ),
        GrantMilestone(
            "Summer Workshop", 
            "Intensive music camp", 
            date(2024, 7, 15), 
            None, 
            "In Progress"
        ),
        GrantMilestone(
            "Fall Recital", 
            "Student showcase event", 
            date(2024, 11, 15), 
            None, 
            "Pending"
        ),
        GrantMilestone(
            "Final Performance", 
            "Year-end community concert", 
            date(2024, 12, 10), 
            None, 
            "Pending"
        )
    ]
    
    # Add documents for arts grant
    arts_grant.documents = [
        GrantDocument(
            "Grant Application", 
            DocumentType.APPLICATION, 
            "/documents/arts_grant_application_2024.pdf"
        ),
        GrantDocument(
            "Budget Worksheet", 
            DocumentType.BUDGET, 
            "/documents/arts_grant_budget_2024.xlsx"
        ),
        GrantDocument(
            "Award Notification", 
            DocumentType.AWARD_LETTER, 
            "/documents/arts_grant_award_2024.pdf"
        ),
        GrantDocument(
            "Q1 Progress Report", 
            DocumentType.PROGRESS_REPORT, 
            "/documents/arts_grant_q1_2024.pdf"
        ),
        GrantDocument(
            "Spring Concert Program", 
            DocumentType.SUPPORTING_DOCS, 
            "/documents/spring_concert_program_2024.pdf"
        )
    ]
    
    grants.append(arts_grant)
    
    # Federal Technology Grant
    tech_grant = EnhancedPastGrant(
        funder="National Science Foundation",
        title="Digital Equity in Rural Education",
        amount=75000,
        year=2022,
        type="Federal",
        purpose="Bridging digital divide for rural students",
        status="Completed",
        organization="NRG Development",
        program_name="NSF Educational Innovation",
        grant_number="NSF-EI-2022-1245",
        project_period_start=date(2022, 9, 1),
        project_period_end=date(2024, 8, 31),
        application_date=date(2022, 4, 1),
        notification_date=date(2022, 7, 15),
        project_director="Dr. Lisa Chen",
        collaborating_organizations=[
            "WV University", 
            "Regional School District"
        ],
        total_project_cost=95000,
        match_required=20000,
        match_provided=25000,
        beneficiaries_served=120,
        impact_metrics={
            "students_with_devices": 120,
            "teachers_trained": 18,
            "digital_literacy_improved": 95,
            "test_scores_increased": 15
        },
        success_stories=[
            "100% of students gained access to learning devices",
            "Student test scores improved by 15% on average",
            "Program model adopted by 3 other districts"
        ],
        lessons_learned=[
            "Internet connectivity is as important as devices",
            "Parent training is crucial for success",
            "Tech support needs to be ongoing"
        ],
        tags=["technology", "digital equity", "rural education", "NSF"]
    )
    
    grants.append(tech_grant)
    
    return grants
