"""
Template manager for handling application template operations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..config import APPLICATIONS_DIR, TEMPLATES_DIR
from ..models.application_template import (
    ApplicationResponse,
    ApplicationTemplate,
    create_default_template,
)
from ..models.organization import OrganizationProfile


class TemplateManager:
    """Manager for handling application template operations."""

    def __init__(
        self, templates_dir: Optional[Path] = None, applications_dir: Optional[Path] = None
    ):
        """Initialize the template manager."""
        self.templates_dir = templates_dir or TEMPLATES_DIR
        self.applications_dir = applications_dir or APPLICATIONS_DIR
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.applications_dir.mkdir(parents=True, exist_ok=True)

    def get_default_template(self) -> ApplicationTemplate:
        """Get the default application template."""
        return create_default_template()

    def load_template(self, template_id: str) -> Optional[ApplicationTemplate]:
        """Load a template from file."""
        template_file = self.templates_dir / f"{template_id}.json"
        if not template_file.exists():
            return None

        try:
            with open(template_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ApplicationTemplate(**data)
        except Exception as e:
            print(f"Error loading template: {e}")
            return None

    def save_template(self, template: ApplicationTemplate) -> bool:
        """Save a template to file."""
        try:
            template_file = self.templates_dir / f"{template.id}.json"
            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(template.model_dump(), f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Error saving template: {e}")
            return False

    def list_templates(self) -> List[ApplicationTemplate]:
        """List all available templates."""
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            template = self.load_template(template_file.stem)
            if template:
                templates.append(template)
        return templates

    def create_application(
        self, template_id: str, organization_id: str, grant_id: str = "", created_by: str = ""
    ) -> Optional[ApplicationResponse]:
        """Create a new application response."""
        template = self.load_template(template_id)
        if not template:
            return None

        now = datetime.now()
        response = ApplicationResponse(
            id=f"app_{template_id}_{now.strftime('%Y%m%d_%H%M%S')}",
            template_id=template_id,
            organization_id=organization_id,
            grant_id=grant_id,
            created_by=created_by,
            created_at=now,
            updated_at=now,
            status="draft",
            submitted_at=None,
            notes="",
        )

        return response

    def save_application(self, application: ApplicationResponse) -> bool:
        """Save an application response to file."""
        try:
            app_file = self.applications_dir / f"{application.id}.json"
            with open(app_file, "w", encoding="utf-8") as f:
                json.dump(application.model_dump(), f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Error saving application: {e}")
            return False

    def load_application(self, application_id: str) -> Optional[ApplicationResponse]:
        """Load an application response from file."""
        app_file = self.applications_dir / f"{application_id}.json"
        if not app_file.exists():
            return None

        try:
            with open(app_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ApplicationResponse(**data)
        except Exception as e:
            print(f"Error loading application: {e}")
            return None

    def list_applications(self, organization_id: Optional[str] = None) -> List[ApplicationResponse]:
        """List all applications, optionally filtered by organization."""
        applications = []
        for app_file in self.applications_dir.glob("*.json"):
            app = self.load_application(app_file.stem)
            if app and (not organization_id or app.organization_id == organization_id):
                applications.append(app)
        return applications

    def auto_fill_from_profile(
        self,
        application: ApplicationResponse,
        template: ApplicationTemplate,
        profile: OrganizationProfile,
    ) -> ApplicationResponse:
        """Auto-fill application fields from organization profile."""
        profile_data = profile.model_dump()

        for field in template.fields:
            if field.profile_field and field.profile_field in profile_data:
                value = profile_data[field.profile_field]
                if value:  # Only fill if value exists
                    application.set_response(field.id, value)

        return application

    def validate_application(
        self, application: ApplicationResponse, template: ApplicationTemplate
    ) -> List[str]:
        """Validate an application response and return error messages."""
        errors = []

        for field in template.fields:
            if field.required and field.id not in application.responses:
                errors.append(f"Required field '{field.id}' is missing")
                continue

            if field.id in application.responses:
                value = application.responses[field.id]

                # Check for empty required fields
                if field.required and (value is None or value == ""):
                    errors.append(f"Required field '{field.id}' cannot be empty")
                    continue

                # Validate based on field type
                if field.field_type.value == "text":
                    if field.min_length and len(str(value)) < field.min_length:
                        errors.append(
                            f"'{field.id}' must be at least {field.min_length} characters"
                        )
                    if field.max_length and len(str(value)) > field.max_length:
                        errors.append(
                            f"'{field.id}' must be at most {field.max_length} characters"
                        )

                elif field.field_type.value == "number":
                    try:
                        num_value = float(value)
                        if field.min_value is not None and num_value < field.min_value:
                            errors.append(
                                f"'{field.id}' must be at least {field.min_value}"
                            )
                        if field.max_value is not None and num_value > field.max_value:
                            errors.append(f"'{field.id}' must be at most {field.max_value}")
                    except (ValueError, TypeError):
                        errors.append(f"'{field.id}' must be a valid number")

                elif field.field_type.value == "email":
                    if value and "@" not in str(value):
                        errors.append(f"'{field.id}' must be a valid email address")

        return errors

    def export_application(
        self, application: ApplicationResponse, template: ApplicationTemplate, format: str = "json"
    ) -> Optional[str]:
        """Export an application to various formats."""
        if format.lower() == "json":
            return json.dumps(application.model_dump(), indent=2, default=str)
        elif format.lower() == "text":
            lines = []
            lines.append(f"Application: {application.id}")
            lines.append(f"Template: {template.name}")
            lines.append(f"Status: {application.status}")
            lines.append(f"Created: {application.created_at}")
            lines.append("")

            for field in template.get_fields_in_order():
                if field.id in application.responses:
                    lines.append(f"{field.label}:")
                    lines.append(f"  {application.responses[field.id]}")
                    lines.append("")

            return "\n".join(lines)
        else:
            print(f"Unsupported export format: {format}")
            return None
