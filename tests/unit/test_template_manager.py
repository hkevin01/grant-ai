"""
Unit tests for TemplateManager.
"""
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from grant_ai.models.application_template import (
    ApplicationResponse,
    ApplicationTemplate,
    FieldType,
    TemplateField,
)
from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType
from grant_ai.utils.template_manager import TemplateManager


class TestTemplateManager:
    """Test cases for TemplateManager."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as templates_dir, \
             tempfile.TemporaryDirectory() as applications_dir:
            yield Path(templates_dir), Path(applications_dir)
    
    @pytest.fixture
    def manager(self, temp_dirs):
        """Create a TemplateManager instance."""
        templates_dir, applications_dir = temp_dirs
        return TemplateManager(templates_dir, applications_dir)
    
    @pytest.fixture
    def sample_template(self):
        """Create a sample application template for testing."""
        return ApplicationTemplate(
            id="test_template",
            name="Test Template",
            description="A test template",
            grant_type="Test Grant",
            organization="Test Org",
            created_by="Test User",
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
                    id="project_title",
                    label="Project Title",
                    field_type=FieldType.TEXT,
                    required=True,
                    max_length=200,
                    order=2
                ),
                TemplateField(
                    id="requested_amount",
                    label="Requested Amount",
                    field_type=FieldType.NUMBER,
                    required=True,
                    min_value=0,
                    order=3
                )
            ]
        )
    
    @pytest.fixture
    def sample_profile(self):
        """Create a sample organization profile for testing."""
        return OrganizationProfile(
            name="Test Organization",
            description="A test organization",
            focus_areas=[FocusArea.EDUCATION],
            program_types=[ProgramType.AFTER_SCHOOL],
            target_demographics=["youth"],
            annual_budget=100000,
            location="Test City",
            contact_name="Test Contact",
            contact_email="test@example.com",
            website="https://example.com",
            ein="12-3456789",
            founded_year=2020,
            preferred_grant_size=(10000, 50000),
            contact_phone="555-1234"
        )
    
    def test_get_default_template(self, manager):
        """Test getting the default template."""
        template = manager.get_default_template()
        
        assert template.id == "general_grant_v1"
        assert template.name == "General Grant Application"
        assert len(template.fields) > 0
        
        # Check that required fields exist
        required_fields = [f for f in template.fields if f.required]
        assert len(required_fields) > 0
    
    def test_save_and_load_template(self, manager, sample_template):
        """Test saving and loading a template."""
        # Save template
        success = manager.save_template(sample_template)
        assert success is True
        
        # Load template
        loaded = manager.load_template(sample_template.id)
        assert loaded is not None
        assert loaded.id == sample_template.id
        assert loaded.name == sample_template.name
        assert len(loaded.fields) == len(sample_template.fields)
    
    def test_load_nonexistent_template(self, manager):
        """Test loading a template that doesn't exist."""
        loaded = manager.load_template("nonexistent")
        assert loaded is None
    
    def test_list_templates(self, manager, sample_template):
        """Test listing templates."""
        # Initially no templates
        templates = manager.list_templates()
        assert len(templates) == 0
        
        # Save a template
        manager.save_template(sample_template)
        
        # Now should have one template
        templates = manager.list_templates()
        assert len(templates) == 1
        assert templates[0].id == sample_template.id
    
    def test_create_application(self, manager, sample_template):
        """Test creating a new application."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org",
            grant_id="test_grant",
            created_by="test_user"
        )
        
        assert application is not None
        assert application.template_id == sample_template.id
        assert application.organization_id == "test_org"
        assert application.grant_id == "test_grant"
        assert application.created_by == "test_user"
        assert application.status == "draft"
    
    def test_create_application_nonexistent_template(self, manager):
        """Test creating an application with a nonexistent template."""
        application = manager.create_application(
            template_id="nonexistent",
            organization_id="test_org"
        )
        assert application is None
    
    def test_save_and_load_application(self, manager, sample_template):
        """Test saving and loading an application."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create and save application
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        application.set_response("project_title", "Test Project")
        application.set_response("requested_amount", 50000)
        
        success = manager.save_application(application)
        assert success is True
        
        # Load application
        loaded = manager.load_application(application.id)
        assert loaded is not None
        assert loaded.template_id == sample_template.id
        assert loaded.get_response("org_name") == "Test Organization"
        assert loaded.get_response("project_title") == "Test Project"
        assert loaded.get_response("requested_amount") == 50000
    
    def test_load_nonexistent_application(self, manager):
        """Test loading an application that doesn't exist."""
        loaded = manager.load_application("nonexistent")
        assert loaded is None
    
    def test_list_applications(self, manager, sample_template):
        """Test listing applications."""
        # Initially no applications
        applications = manager.list_applications()
        assert len(applications) == 0
        
        # Save template and create application
        manager.save_template(sample_template)
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        manager.save_application(application)
        
        # Now should have one application
        applications = manager.list_applications()
        assert len(applications) == 1
        assert applications[0].id == application.id
        
        # Test filtering by organization
        applications = manager.list_applications("test_org")
        assert len(applications) == 1
        
        applications = manager.list_applications("other_org")
        assert len(applications) == 0
    
    def test_auto_fill_from_profile(self, manager, sample_template, sample_profile):
        """Test auto-filling application from organization profile."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        
        # Auto-fill from profile
        filled_application = manager.auto_fill_from_profile(
            application, sample_template, sample_profile
        )
        
        # Check that profile fields were filled
        assert filled_application.get_response("org_name") == "Test Organization"
    
    def test_validate_application_valid(self, manager, sample_template):
        """Test validating a valid application."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application with valid data
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        application.set_response("project_title", "Test Project")
        application.set_response("requested_amount", 50000)
        
        errors = manager.validate_application(application, sample_template)
        assert len(errors) == 0
    
    def test_validate_application_missing_required(self, manager, sample_template):
        """Test validating an application with missing required fields."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application without required fields
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        # Don't set any responses
        
        errors = manager.validate_application(application, sample_template)
        assert len(errors) > 0
        assert any("org_name" in error for error in errors)
        assert any("project_title" in error for error in errors)
        assert any("requested_amount" in error for error in errors)
    
    def test_validate_application_invalid_text_length(self, manager, sample_template):
        """Test validating an application with invalid text length."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application with invalid text length
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        application.set_response("project_title", "")  # Too short
        application.set_response("requested_amount", 50000)
        
        errors = manager.validate_application(application, sample_template)
        assert len(errors) > 0
        assert any("project_title" in error for error in errors)
    
    def test_validate_application_invalid_number(self, manager, sample_template):
        """Test validating an application with invalid number."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application with invalid number
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        application.set_response("project_title", "Test Project")
        application.set_response("requested_amount", "not-a-number")  # Invalid
        
        errors = manager.validate_application(application, sample_template)
        assert len(errors) > 0
        assert any("requested_amount" in error for error in errors)
    
    def test_export_application_json(self, manager, sample_template):
        """Test exporting an application to JSON format."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        
        # Export to JSON
        export_data = manager.export_application(application, sample_template, "json")
        
        assert export_data is not None
        assert "Test Organization" in export_data
    
    def test_export_application_text(self, manager, sample_template):
        """Test exporting an application to text format."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        
        # Export to text
        export_data = manager.export_application(application, sample_template, "text")
        
        assert export_data is not None
        assert "Test Organization" in export_data
        assert "Organization Name:" in export_data
    
    def test_export_application_invalid_format(self, manager, sample_template):
        """Test exporting an application with invalid format."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        
        # Export with invalid format
        export_data = manager.export_application(application, sample_template, "invalid")
        
        assert export_data is None
    
    def test_is_complete_true(self, manager, sample_template):
        """Test checking if an application is complete."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application with all required fields
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        application.set_response("project_title", "Test Project")
        application.set_response("requested_amount", 50000)
        
        assert application.is_complete(sample_template) is True
    
    def test_is_complete_false(self, manager, sample_template):
        """Test checking if an application is incomplete."""
        # Save template first
        manager.save_template(sample_template)
        
        # Create application with missing required fields
        application = manager.create_application(
            template_id=sample_template.id,
            organization_id="test_org"
        )
        application.set_response("org_name", "Test Organization")
        # Don't set other required fields
        
        assert application.is_complete(sample_template) is False 