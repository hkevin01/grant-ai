"""
Unit tests for QuestionnaireManager.
"""
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType
from grant_ai.models.questionnaire import (
    Question,
    Questionnaire,
    QuestionnaireResponse,
    QuestionType,
)
from grant_ai.utils.questionnaire_manager import QuestionnaireManager


class TestQuestionnaireManager:
    """Test cases for QuestionnaireManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create a QuestionnaireManager instance."""
        return QuestionnaireManager(data_dir=temp_dir)
    
    @pytest.fixture
    def sample_questionnaire(self):
        """Create a sample questionnaire for testing."""
        return Questionnaire(
            id="test_questionnaire",
            title="Test Questionnaire",
            description="A test questionnaire",
            questions=[
                Question(
                    id="org_name",
                    text="What is your organization's name?",
                    question_type=QuestionType.TEXT,
                    required=True,
                    field_mapping="name",
                    min_length=1,
                    max_length=200
                ),
                Question(
                    id="focus_areas",
                    text="What are your focus areas?",
                    question_type=QuestionType.CHECKBOX,
                    required=True,
                    options=[area.value for area in FocusArea],
                    field_mapping="focus_areas"
                )
            ]
        )
    
    def test_get_default_questionnaire(self, manager):
        """Test getting the default questionnaire."""
        questionnaire = manager.get_default_questionnaire()
        
        assert questionnaire.id == "org_profile_v1"
        assert questionnaire.title == "Organization Profile Questionnaire"
        assert len(questionnaire.questions) > 0
        
        # Check that required questions exist
        required_questions = [q for q in questionnaire.questions if q.required]
        assert len(required_questions) > 0
    
    def test_save_and_load_questionnaire(self, manager, sample_questionnaire):
        """Test saving and loading a questionnaire."""
        # Save questionnaire
        success = manager.save_questionnaire(sample_questionnaire)
        assert success is True
        
        # Load questionnaire
        loaded = manager.load_questionnaire(sample_questionnaire.id)
        assert loaded is not None
        assert loaded.id == sample_questionnaire.id
        assert loaded.title == sample_questionnaire.title
        assert len(loaded.questions) == len(sample_questionnaire.questions)
    
    def test_load_nonexistent_questionnaire(self, manager):
        """Test loading a questionnaire that doesn't exist."""
        loaded = manager.load_questionnaire("nonexistent")
        assert loaded is None
    
    def test_create_response(self, manager):
        """Test creating a new questionnaire response."""
        response = manager.create_response("test_questionnaire")
        
        assert response.questionnaire_id == "test_questionnaire"
        assert response.completed is False
        assert response.created_at is not None
        assert response.updated_at is not None
    
    def test_save_and_load_response(self, manager, sample_questionnaire):
        """Test saving and loading a questionnaire response."""
        # Save questionnaire first
        manager.save_questionnaire(sample_questionnaire)
        
        # Create and save response
        response = manager.create_response(sample_questionnaire.id)
        response.set_response("org_name", "Test Organization")
        
        success = manager.save_response(response)
        assert success is True
        
        # Load response
        response_files = list(manager.data_dir.glob("response_*.json"))
        assert len(response_files) == 1
        
        loaded = manager.load_response(response_files[0])
        assert loaded is not None
        assert loaded.questionnaire_id == sample_questionnaire.id
        assert loaded.get_response("org_name") == "Test Organization"
    
    def test_convert_response_to_profile(self, manager, sample_questionnaire):
        """Test converting a questionnaire response to an organization profile."""
        # Create response with data
        response = manager.create_response(sample_questionnaire.id)
        response.set_response("org_name", "Test Organization")
        response.set_response("focus_areas", ["education", "music_education"])
        
        # Convert to profile
        profile = manager.convert_response_to_profile(response, sample_questionnaire)
        
        assert profile is not None
        assert profile.name == "Test Organization"
        assert FocusArea.EDUCATION in profile.focus_areas
        assert FocusArea.MUSIC_EDUCATION in profile.focus_areas
    
    def test_convert_response_with_missing_data(self, manager, sample_questionnaire):
        """Test converting a response with missing data."""
        # Create response with minimal data
        response = manager.create_response(sample_questionnaire.id)
        response.set_response("org_name", "Test Organization")
        # Don't set focus_areas
        
        # Convert to profile
        profile = manager.convert_response_to_profile(response, sample_questionnaire)
        
        assert profile is not None
        assert profile.name == "Test Organization"
        assert profile.focus_areas == []  # Should have default empty list
    
    def test_validate_response_valid(self, manager, sample_questionnaire):
        """Test validating a valid response."""
        response = manager.create_response(sample_questionnaire.id)
        response.set_response("org_name", "Test Organization")
        response.set_response("focus_areas", ["education"])
        
        errors = manager.validate_response(response, sample_questionnaire)
        assert len(errors) == 0
    
    def test_validate_response_missing_required(self, manager, sample_questionnaire):
        """Test validating a response with missing required fields."""
        response = manager.create_response(sample_questionnaire.id)
        # Don't set any responses
        
        errors = manager.validate_response(response, sample_questionnaire)
        assert len(errors) > 0
        assert any("org_name" in error for error in errors)
        assert any("focus_areas" in error for error in errors)
    
    def test_validate_response_invalid_text_length(self, manager, sample_questionnaire):
        """Test validating a response with invalid text length."""
        response = manager.create_response(sample_questionnaire.id)
        response.set_response("org_name", "")  # Too short
        response.set_response("focus_areas", ["education"])
        
        errors = manager.validate_response(response, sample_questionnaire)
        assert len(errors) > 0
        assert any("org_name" in error for error in errors)
    
    def test_validate_response_invalid_email(self, manager):
        """Test validating a response with invalid email."""
        questionnaire = Questionnaire(
            id="test_email",
            title="Email Test",
            questions=[
                Question(
                    id="email",
                    text="Email address",
                    question_type=QuestionType.EMAIL,
                    required=True,
                    field_mapping="contact_email"
                )
            ]
        )
        
        response = manager.create_response(questionnaire.id)
        response.set_response("email", "invalid-email")  # Invalid email
        
        errors = manager.validate_response(response, questionnaire)
        assert len(errors) > 0
        assert any("email" in error.lower() for error in errors)
    
    def test_validate_response_invalid_number(self, manager):
        """Test validating a response with invalid number."""
        questionnaire = Questionnaire(
            id="test_number",
            title="Number Test",
            questions=[
                Question(
                    id="budget",
                    text="Budget",
                    question_type=QuestionType.NUMBER,
                    required=True,
                    field_mapping="annual_budget",
                    min_value=0
                )
            ]
        )
        
        response = manager.create_response(questionnaire.id)
        response.set_response("budget", "not-a-number")  # Invalid number
        
        errors = manager.validate_response(response, questionnaire)
        assert len(errors) > 0
        assert any("budget" in error.lower() for error in errors)
    
    def test_is_complete_true(self, manager, sample_questionnaire):
        """Test checking if a response is complete."""
        response = manager.create_response(sample_questionnaire.id)
        response.set_response("org_name", "Test Organization")
        response.set_response("focus_areas", ["education"])
        
        assert response.is_complete(sample_questionnaire) is True
    
    def test_is_complete_false(self, manager, sample_questionnaire):
        """Test checking if a response is incomplete."""
        response = manager.create_response(sample_questionnaire.id)
        response.set_response("org_name", "Test Organization")
        # Don't set focus_areas (required)
        
        assert response.is_complete(sample_questionnaire) is False 