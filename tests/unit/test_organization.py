"""Unit tests for organization model."""

from datetime import datetime

import pytest

from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType


class TestOrganizationProfile:
    """Test cases for OrganizationProfile model."""
    
    def test_create_basic_organization(self):
        """Test creating a basic organization profile."""
        org = OrganizationProfile(
            name="Test Org",
            description="A test organization"
        )
        
        assert org.name == "Test Org"
        assert org.description == "A test organization"
        assert isinstance(org.created_at, datetime)
        assert isinstance(org.updated_at, datetime)
    
    def test_add_focus_area(self, sample_organization):
        """Test adding focus areas to organization."""
        initial_count = len(sample_organization.focus_areas)
        sample_organization.add_focus_area(FocusArea.MUSIC_EDUCATION)
        
        assert len(sample_organization.focus_areas) == initial_count + 1
        assert FocusArea.MUSIC_EDUCATION in sample_organization.focus_areas
    
    def test_add_duplicate_focus_area(self, sample_organization):
        """Test that duplicate focus areas are not added."""
        initial_areas = sample_organization.focus_areas.copy()
        existing_area = sample_organization.focus_areas[0]
        
        sample_organization.add_focus_area(existing_area)
        
        assert sample_organization.focus_areas == initial_areas
    
    def test_add_program_type(self, sample_organization):
        """Test adding program types to organization."""
        initial_count = len(sample_organization.program_types)
        sample_organization.add_program_type(ProgramType.SUMMER_CAMPS)
        
        assert len(sample_organization.program_types) == initial_count + 1
        assert ProgramType.SUMMER_CAMPS in sample_organization.program_types
    
    def test_is_eligible_for_amount(self, sample_organization):
        """Test grant amount eligibility checking."""
        # Within range
        assert sample_organization.is_eligible_for_amount(25000) == True
        
        # Below range
        assert sample_organization.is_eligible_for_amount(5000) == False
        
        # Above range
        assert sample_organization.is_eligible_for_amount(75000) == False
        
        # At boundaries
        assert sample_organization.is_eligible_for_amount(10000) == True
        assert sample_organization.is_eligible_for_amount(50000) == True
    
    def test_get_focus_keywords(self, sample_organization):
        """Test focus keyword generation."""
        keywords = sample_organization.get_focus_keywords()
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        
        # Should contain keywords for education and robotics
        assert any("education" in keyword.lower() for keyword in keywords)
        assert any("robotics" in keyword.lower() for keyword in keywords)
    
    def test_update_timestamp(self, sample_organization):
        """Test timestamp updating."""
        original_time = sample_organization.updated_at
        sample_organization.update_timestamp()
        
        assert sample_organization.updated_at > original_time
    
    def test_model_validation(self):
        """Test model validation with invalid data."""
        with pytest.raises(ValueError):
            OrganizationProfile(
                name="",  # Empty name should be invalid
                preferred_grant_size=(50000, 10000)  # Min > Max should be invalid
            )
