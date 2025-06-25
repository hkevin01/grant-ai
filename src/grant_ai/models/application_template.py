"""
Application template models for grant applications.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FieldType(str, Enum):
    """Types of fields in application templates."""
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    URL = "url"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    FILE_UPLOAD = "file_upload"


class TemplateField(BaseModel):
    """Model representing a field in an application template."""
    
    id: str = Field(..., description="Unique field identifier")
    label: str = Field(..., description="Field label")
    field_type: FieldType = Field(..., description="Type of field")
    required: bool = Field(True, description="Whether the field is required")
    help_text: Optional[str] = Field(None, description="Help text for the field")
    
    # For multiple choice fields
    options: Optional[List[str]] = Field(None, description="Available options")
    
    # For validation
    min_length: Optional[int] = Field(None, description="Minimum length for text")
    max_length: Optional[int] = Field(None, description="Maximum length for text")
    min_value: Optional[float] = Field(None, description="Minimum value for numbers")
    max_value: Optional[float] = Field(None, description="Maximum value for numbers")
    
    # For file uploads
    allowed_extensions: Optional[List[str]] = Field(None, description="Allowed file extensions")
    max_file_size: Optional[int] = Field(None, description="Maximum file size in bytes")
    
    # For organization profile mapping
    profile_field: Optional[str] = Field(None, description="Corresponding field in OrganizationProfile")
    
    # Display order
    order: int = Field(0, description="Display order of the field")


class ApplicationTemplate(BaseModel):
    """Model representing a grant application template."""
    
    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field("", description="Template description")
    grant_type: str = Field("", description="Type of grant this template is for")
    organization: str = Field("", description="Granting organization name")
    
    fields: List[TemplateField] = Field(default_factory=list, description="Template fields")
    
    # Metadata
    version: str = Field("1.0", description="Template version")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field("", description="Who created the template")
    
    # Template settings
    allow_save_draft: bool = Field(True, description="Allow saving as draft")
    allow_edit: bool = Field(True, description="Allow editing after submission")
    auto_fill_profile: bool = Field(True, description="Auto-fill from organization profile")
    
    def get_field_by_id(self, field_id: str) -> Optional[TemplateField]:
        """Get a field by its ID."""
        for field in self.fields:
            if field.id == field_id:
                return field
        return None
    
    def get_required_fields(self) -> List[TemplateField]:
        """Get all required fields."""
        return [f for f in self.fields if f.required]
    
    def get_fields_in_order(self) -> List[TemplateField]:
        """Get fields sorted by order."""
        return sorted(self.fields, key=lambda f: f.order)
    
    def add_field(self, field: TemplateField) -> None:
        """Add a field to the template."""
        if not field.order:
            field.order = len(self.fields) + 1
        self.fields.append(field)
        self.updated_at = datetime.now()
    
    def remove_field(self, field_id: str) -> bool:
        """Remove a field from the template."""
        for i, field in enumerate(self.fields):
            if field.id == field_id:
                self.fields.pop(i)
                self.updated_at = datetime.now()
                return True
        return False


class ApplicationResponse(BaseModel):
    """Model representing a response to an application template."""
    
    id: str = Field(..., description="Unique response identifier")
    template_id: str = Field(..., description="ID of the template")
    organization_id: str = Field(..., description="ID of the organization")
    grant_id: str = Field("", description="ID of the grant being applied for")
    
    responses: Dict[str, Any] = Field(default_factory=dict, description="Field ID to response mapping")
    
    # Status tracking
    status: str = Field("draft", description="Application status")
    submitted_at: Optional[datetime] = Field(None, description="When submitted")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Metadata
    created_by: str = Field("", description="Who created the response")
    notes: str = Field("", description="Additional notes")
    
    def get_response(self, field_id: str) -> Any:
        """Get response for a specific field."""
        return self.responses.get(field_id)
    
    def set_response(self, field_id: str, response: Any) -> None:
        """Set response for a specific field."""
        self.responses[field_id] = response
        self.updated_at = datetime.now()
    
    def is_complete(self, template: ApplicationTemplate) -> bool:
        """Check if all required fields are answered."""
        required_fields = template.get_required_fields()
        for field in required_fields:
            if field.id not in self.responses or not self.responses[field.id]:
                return False
        return True
    
    def submit(self) -> None:
        """Mark the application as submitted."""
        self.status = "submitted"
        self.submitted_at = datetime.now()
        self.updated_at = datetime.now()


def create_default_template() -> ApplicationTemplate:
    """Create a default grant application template."""
    return ApplicationTemplate(
        id="general_grant_v1",
        name="General Grant Application",
        description="A general template for grant applications",
        grant_type="General",
        organization="Various",
        created_by="System",
        fields=[
            TemplateField(
                id="org_name",
                label="Organization Name",
                field_type=FieldType.TEXT,
                required=True,
                profile_field="name",
                order=1
            ),
            TemplateField(
                id="org_description",
                label="Organization Description",
                field_type=FieldType.TEXTAREA,
                required=True,
                profile_field="description",
                order=2
            ),
            TemplateField(
                id="project_title",
                label="Project Title",
                field_type=FieldType.TEXT,
                required=True,
                max_length=200,
                order=3
            ),
            TemplateField(
                id="project_description",
                label="Project Description",
                field_type=FieldType.TEXTAREA,
                required=True,
                help_text="Describe your project in detail",
                order=4
            ),
            TemplateField(
                id="requested_amount",
                label="Requested Amount (USD)",
                field_type=FieldType.NUMBER,
                required=True,
                min_value=0,
                order=5
            ),
            TemplateField(
                id="project_duration",
                label="Project Duration (months)",
                field_type=FieldType.NUMBER,
                required=True,
                min_value=1,
                max_value=60,
                order=6
            ),
            TemplateField(
                id="start_date",
                label="Project Start Date",
                field_type=FieldType.DATE,
                required=True,
                order=7
            ),
            TemplateField(
                id="contact_name",
                label="Primary Contact Name",
                field_type=FieldType.TEXT,
                required=True,
                profile_field="contact_name",
                order=8
            ),
            TemplateField(
                id="contact_email",
                label="Primary Contact Email",
                field_type=FieldType.EMAIL,
                required=True,
                profile_field="contact_email",
                order=9
            ),
            TemplateField(
                id="budget_breakdown",
                label="Budget Breakdown",
                field_type=FieldType.TEXTAREA,
                required=False,
                help_text="Provide a detailed breakdown of how funds will be used",
                order=10
            ),
            TemplateField(
                id="expected_outcomes",
                label="Expected Outcomes",
                field_type=FieldType.TEXTAREA,
                required=True,
                help_text="What outcomes do you expect from this project?",
                order=11
            ),
            TemplateField(
                id="supporting_documents",
                label="Supporting Documents",
                field_type=FieldType.FILE_UPLOAD,
                required=False,
                allowed_extensions=["pdf", "doc", "docx"],
                max_file_size=10485760,  # 10MB
                order=12
            )
        ]
    ) 