"""
Template manager for grant application templates.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional

from grant_ai.models.application_template import (
    ApplicationResponse,
    ApplicationTemplate,
    FieldType,
    TemplateField,
    create_default_template,
)


class TemplateManager:
    """Manages grant application templates."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize template manager.
        
        Args:
            data_dir: Directory to store template data
        """
        self.data_dir = data_dir or Path.home() / ".grant_ai" / "templates"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize with default templates
        self._templates: Dict[str, ApplicationTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default templates."""
        # General template
        self._templates["general_grant_v1"] = create_default_template()
        
        # Federal education template
        self._templates["federal_education_v1"] = self._create_federal_education_template()
        
        # Private foundation template
        self._templates["private_foundation_v1"] = self._create_private_foundation_template()
        
        # Housing development template
        self._templates["housing_development_v1"] = self._create_housing_development_template()
    
    def _create_federal_education_template(self) -> ApplicationTemplate:
        """Create federal education grant template."""
        return ApplicationTemplate(
            id="federal_education_v1",
            name="Federal Education Grant Application",
            description="Template for federal education grants (Title I, 21st Century, etc.)",
            grant_type="Education",
            organization="U.S. Department of Education",
            created_by="System",
            fields=[
                TemplateField(
                    id="applicant_org",
                    label="Applicant Organization Name",
                    field_type=FieldType.TEXT,
                    required=True,
                    max_length=200,
                    profile_field="name",
                    order=1
                ),
                TemplateField(
                    id="ein",
                    label="Employer Identification Number (EIN)",
                    field_type=FieldType.TEXT,
                    required=True,
                    help_text="Format: XX-XXXXXXX",
                    profile_field="ein",
                    order=2
                ),
                TemplateField(
                    id="project_title",
                    label="Project Title",
                    field_type=FieldType.TEXT,
                    required=True,
                    max_length=150,
                    order=3
                ),
                TemplateField(
                    id="project_summary",
                    label="Project Summary/Abstract",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    max_length=2000,
                    help_text="One-page summary of your project, goals, and expected outcomes",
                    order=4
                ),
                TemplateField(
                    id="target_population",
                    label="Target Population",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Describe the students/community you will serve",
                    order=5
                ),
                TemplateField(
                    id="needs_assessment",
                    label="Statement of Need",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Include data and evidence supporting the need",
                    order=6
                ),
                TemplateField(
                    id="project_description",
                    label="Project Description",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Detailed description of proposed activities and methodology",
                    order=7
                ),
                TemplateField(
                    id="goals_objectives",
                    label="Goals and Objectives",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Use SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)",
                    order=8
                ),
                TemplateField(
                    id="evaluation_plan",
                    label="Evaluation Plan",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Include both formative and summative evaluation methods",
                    order=9
                ),
                TemplateField(
                    id="budget_narrative",
                    label="Budget Narrative",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Justify each budget category and expense",
                    order=10
                ),
                TemplateField(
                    id="sustainability_plan",
                    label="Sustainability Plan",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="How will the project continue after grant funding ends?",
                    order=11
                ),
                TemplateField(
                    id="requested_amount",
                    label="Total Amount Requested",
                    field_type=FieldType.NUMBER,
                    required=True,
                    min_value=1000,
                    order=12
                ),
                TemplateField(
                    id="project_period",
                    label="Project Period (months)",
                    field_type=FieldType.NUMBER,
                    required=True,
                    min_value=12,
                    max_value=60,
                    help_text="Most federal grants are for 1-3 years",
                    order=13
                )
            ]
        )
    
    def _create_private_foundation_template(self) -> ApplicationTemplate:
        """Create private foundation grant template."""
        return ApplicationTemplate(
            id="private_foundation_v1",
            name="Private Foundation Grant Application",
            description="Template for private foundation grants",
            grant_type="General",
            organization="Private Foundation",
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
                    id="contact_person",
                    label="Primary Contact Person",
                    field_type=FieldType.TEXT,
                    required=True,
                    profile_field="contact_name",
                    order=2
                ),
                TemplateField(
                    id="contact_email",
                    label="Contact Email",
                    field_type=FieldType.EMAIL,
                    required=True,
                    profile_field="contact_email",
                    order=3
                ),
                TemplateField(
                    id="org_mission",
                    label="Organization Mission",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    max_length=300,
                    profile_field="description",
                    order=4
                ),
                TemplateField(
                    id="request_summary",
                    label="Grant Request Summary",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    max_length=500,
                    help_text="Two-paragraph summary of your request",
                    order=5
                ),
                TemplateField(
                    id="program_description",
                    label="Program/Project Description",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    order=6
                ),
                TemplateField(
                    id="target_beneficiaries",
                    label="Target Beneficiaries",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Who will benefit from this grant?",
                    order=7
                ),
                TemplateField(
                    id="expected_outcomes",
                    label="Expected Outcomes",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    order=8
                ),
                TemplateField(
                    id="amount_requested",
                    label="Amount Requested",
                    field_type=FieldType.NUMBER,
                    required=True,
                    min_value=500,
                    order=9
                ),
                TemplateField(
                    id="project_timeline",
                    label="Project Timeline",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="When will the project start and end? Key milestones?",
                    order=10
                )
            ]
        )
    
    def _create_housing_development_template(self) -> ApplicationTemplate:
        """Create housing development grant template."""
        return ApplicationTemplate(
            id="housing_development_v1",
            name="Housing & Community Development Grant",
            description="Template for housing and community development grants",
            grant_type="Housing",
            organization="HUD/CDBG",
            created_by="System",
            fields=[
                TemplateField(
                    id="applicant_name",
                    label="Applicant Organization",
                    field_type=FieldType.TEXT,
                    required=True,
                    profile_field="name",
                    order=1
                ),
                TemplateField(
                    id="project_location",
                    label="Project Location",
                    field_type=FieldType.TEXT,
                    required=True,
                    help_text="City, State, ZIP code",
                    profile_field="location",
                    order=2
                ),
                TemplateField(
                    id="community_description",
                    label="Community Description",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Include demographics, income levels, housing conditions",
                    order=3
                ),
                TemplateField(
                    id="housing_needs",
                    label="Housing Needs Assessment",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    help_text="Document the housing needs in your community",
                    order=4
                ),
                TemplateField(
                    id="project_description",
                    label="Project Description",
                    field_type=FieldType.TEXTAREA,
                    required=True,
                    order=5
                ),
                TemplateField(
                    id="units_proposed",
                    label="Number of Housing Units Proposed",
                    field_type=FieldType.NUMBER,
                    required=True,
                    min_value=1,
                    order=6
                ),
                TemplateField(
                    id="total_cost",
                    label="Total Development Cost",
                    field_type=FieldType.NUMBER,
                    required=True,
                    min_value=10000,
                    order=7
                ),
                TemplateField(
                    id="requested_amount",
                    label="Amount Requested",
                    field_type=FieldType.NUMBER,
                    required=True,
                    min_value=5000,
                    order=8
                )
            ]
        )
    
    def get_all_templates(self) -> List[ApplicationTemplate]:
        """Get all available templates."""
        return list(self._templates.values())
    
    def get_template_by_id(self, template_id: str) -> Optional[ApplicationTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)
    
    def get_templates_by_type(self, grant_type: str) -> List[ApplicationTemplate]:
        """Get templates filtered by grant type."""
        return [t for t in self._templates.values() if t.grant_type.lower() == grant_type.lower()]
    
    def save_template(self, template: ApplicationTemplate) -> None:
        """Save a template."""
        self._templates[template.id] = template
        
        # Save to file
        template_file = self.data_dir / f"{template.id}.json"
        with open(template_file, 'w') as f:
            json.dump(template.dict(), f, indent=2, default=str)
    
    def create_response(self, template_id: str, organization_id: str = "") -> Optional[ApplicationResponse]:
        """Create a new response for a template."""
        template = self.get_template_by_id(template_id)
        if not template:
            return None
        
        import uuid
        return ApplicationResponse(
            id=str(uuid.uuid4()),
            template_id=template_id,
            organization_id=organization_id
        )


# Global template manager instance
template_manager = TemplateManager()


# Convenience functions
def get_available_templates() -> List[ApplicationTemplate]:
    """Get all available grant application templates."""
    return template_manager.get_all_templates()


def get_template_by_id(template_id: str) -> Optional[ApplicationTemplate]:
    """Get a specific template by ID."""
    return template_manager.get_template_by_id(template_id)


def get_templates_by_type(grant_type: str) -> List[ApplicationTemplate]:
    """Get templates filtered by grant type."""
    return template_manager.get_templates_by_type(grant_type)


# Example usage
if __name__ == "__main__":
    # Test the template manager
    templates = get_available_templates()
    
    print("Available Grant Application Templates:")
    print("=" * 50)
    
    for template in templates:
        print(f"\nTemplate: {template.name}")
        print(f"Type: {template.grant_type}")
        print(f"Organization: {template.organization}")
        print(f"Fields: {len(template.fields)}")
        print(f"Description: {template.description}")
    
    # Test template creation and response
    print("\n" + "=" * 50)
    print("TEMPLATE DETAILS")
    print("=" * 50)
    
    fed_template = get_template_by_id("federal_education_v1")
    if fed_template:
        print(f"Template: {fed_template.name}")
        print(f"Required fields: {len(fed_template.get_required_fields())}")
        
        # Create a response
        response = template_manager.create_response("federal_education_v1", "test_org")
        if response:
            print(f"Created response: {response.id}")
            print(f"Status: {response.status}")
