"""
Questionnaire management for organization profiling.
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType
from grant_ai.models.questionnaire import (
    Questionnaire,
    QuestionnaireResponse,
    QuestionType,
    create_default_questionnaire,
)


class QuestionnaireManager:
    """Manages questionnaires and their responses."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize questionnaire manager.
        
        Args:
            data_dir: Directory to store questionnaire data
        """
        self.data_dir = (
            data_dir or Path.home() / ".grant_ai" / "questionnaires"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or create default questionnaire
        self.default_questionnaire = create_default_questionnaire()
    
    def get_questionnaire(self, questionnaire_id: str = "org_profile_v1") -> Questionnaire:
        """Get a questionnaire by ID.
        
        Args:
            questionnaire_id: ID of the questionnaire
            
        Returns:
            Questionnaire object
        """
        if questionnaire_id == "org_profile_v1":
            return self.default_questionnaire
        
        # In future: load from database or file
        return self.default_questionnaire
    
    def create_response(self, questionnaire_id: str) -> QuestionnaireResponse:
        """Create a new questionnaire response.
        
        Args:
            questionnaire_id: ID of the questionnaire
            
        Returns:
            New QuestionnaireResponse object
        """
        return QuestionnaireResponse(
            questionnaire_id=questionnaire_id,
            responses={},
            completed=False,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    
    def save_response(self, response: QuestionnaireResponse) -> None:
        """Save a questionnaire response.
        
        Args:
            response: QuestionnaireResponse to save
        """
        response_file = self.data_dir / f"response_{response.questionnaire_id}.json"
        response_data = response.dict()
        
        with open(response_file, 'w') as f:
            json.dump(response_data, f, indent=2)
    
    def load_response(self, questionnaire_id: str) -> Optional[QuestionnaireResponse]:
        """Load a saved questionnaire response.
        
        Args:
            questionnaire_id: ID of the questionnaire
            
        Returns:
            QuestionnaireResponse if found, None otherwise
        """
        response_file = self.data_dir / f"response_{questionnaire_id}.json"
        
        if not response_file.exists():
            return None
        
        try:
            with open(response_file, 'r') as f:
                response_data = json.load(f)
            return QuestionnaireResponse(**response_data)
        except Exception:
            return None
    
    def validate_response(
        self, 
        response: QuestionnaireResponse, 
        questionnaire: Questionnaire
    ) -> List[str]:
        """Validate a questionnaire response.
        
        Args:
            response: QuestionnaireResponse to validate
            questionnaire: Questionnaire to validate against
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        for question in questionnaire.questions:
            if question.required and question.id not in response.responses:
                errors.append(f"Question '{question.text}' is required")
                continue
            
            if question.id not in response.responses:
                continue
                
            answer = response.responses[question.id]
            
            # Validate based on question type
            if question.question_type == QuestionType.TEXT:
                if not isinstance(answer, str):
                    errors.append(f"Question '{question.text}' must be text")
                elif question.min_length and len(answer) < question.min_length:
                    errors.append(
                        f"Question '{question.text}' must be at least "
                        f"{question.min_length} characters"
                    )
                elif question.max_length and len(answer) > question.max_length:
                    errors.append(
                        f"Question '{question.text}' must be at most "
                        f"{question.max_length} characters"
                    )
            
            elif question.question_type == QuestionType.EMAIL:
                if not isinstance(answer, str) or '@' not in answer:
                    errors.append(f"Question '{question.text}' must be a valid email")
            
            elif question.question_type == QuestionType.URL:
                if not isinstance(answer, str) or not answer.startswith(('http://', 'https://')):
                    errors.append(f"Question '{question.text}' must be a valid URL")
            
            elif question.question_type == QuestionType.NUMBER:
                try:
                    num_value = float(answer)
                    if question.min_value is not None and num_value < question.min_value:
                        errors.append(
                            f"Question '{question.text}' must be at least {question.min_value}"
                        )
                    if question.max_value is not None and num_value > question.max_value:
                        errors.append(
                            f"Question '{question.text}' must be at most {question.max_value}"
                        )
                except (ValueError, TypeError):
                    errors.append(f"Question '{question.text}' must be a number")
            
            elif question.question_type == QuestionType.CHECKBOX:
                if not isinstance(answer, list):
                    errors.append(f"Question '{question.text}' must be a list of selections")
                elif question.options:
                    invalid_options = [opt for opt in answer if opt not in question.options]
                    if invalid_options:
                        errors.append(
                            f"Question '{question.text}' has invalid options: {invalid_options}"
                        )
        
        return errors
    
    def convert_to_organization_profile(
        self, 
        response: QuestionnaireResponse,
        questionnaire: Questionnaire
    ) -> OrganizationProfile:
        """Convert a questionnaire response to an organization profile.
        
        Args:
            response: QuestionnaireResponse to convert
            questionnaire: Questionnaire for field mapping
            
        Returns:
            OrganizationProfile object
        """
        profile_data = {}
        
        for question in questionnaire.questions:
            if (question.field_mapping and 
                question.id in response.responses):
                
                answer = response.responses[question.id]
                field_name = question.field_mapping
                
                # Handle special field mappings
                if field_name == "focus_areas":
                    # Convert strings to FocusArea enums
                    focus_areas = []
                    for area_str in answer:
                        try:
                            focus_areas.append(FocusArea(area_str))
                        except ValueError:
                            pass  # Skip invalid values
                    profile_data[field_name] = focus_areas
                
                elif field_name == "program_types":
                    # Convert strings to ProgramType enums
                    program_types = []
                    for ptype_str in answer:
                        try:
                            program_types.append(ProgramType(ptype_str))
                        except ValueError:
                            pass  # Skip invalid values
                    profile_data[field_name] = program_types
                
                elif field_name == "target_demographics":
                    # Convert comma-separated string to list
                    if isinstance(answer, str):
                        profile_data[field_name] = [
                            demo.strip() for demo in answer.split(',') if demo.strip()
                        ]
                    else:
                        profile_data[field_name] = answer
                
                elif field_name in ["preferred_grant_size_min", "preferred_grant_size_max"]:
                    # Handle grant size range
                    if "preferred_grant_size" not in profile_data:
                        profile_data["preferred_grant_size"] = [None, None]
                    
                    if field_name == "preferred_grant_size_min":
                        profile_data["preferred_grant_size"][0] = answer
                    else:
                        profile_data["preferred_grant_size"][1] = answer
                
                else:
                    profile_data[field_name] = answer
        
        # Ensure required fields have defaults
        if "id" not in profile_data:
            profile_data["id"] = str(uuid.uuid4())
        
        # Clean up preferred_grant_size if both values are None
        if ("preferred_grant_size" in profile_data and 
            profile_data["preferred_grant_size"] == [None, None]):
            del profile_data["preferred_grant_size"]
        
        return OrganizationProfile(**profile_data)


def create_organization_questionnaire() -> Questionnaire:
    """Create a comprehensive organization questionnaire.
    
    Returns:
        Questionnaire for organization profiling
    """
    return create_default_questionnaire()


# Example usage and testing
if __name__ == "__main__":
    # Create manager
    manager = QuestionnaireManager()
    
    # Get questionnaire
    questionnaire = manager.get_questionnaire()
    print(f"Questionnaire: {questionnaire.title}")
    print(f"Questions: {len(questionnaire.questions)}")
    
    # Create and fill response
    response = manager.create_response("org_profile_v1")
    response.set_response("org_name", "Example Non-Profit")
    response.set_response("org_description", "We help communities through education and support programs.")
    response.set_response("focus_areas", ["education", "community_development"])
    response.set_response("location", "Charleston, WV")
    response.set_response("contact_name", "Jane Doe")
    response.set_response("contact_email", "jane@example.org")
    
    # Validate
    errors = manager.validate_response(response, questionnaire)
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("Response is valid!")
        
        # Convert to profile
        profile = manager.convert_to_organization_profile(response, questionnaire)
        print(f"Created profile: {profile.name}")
        print(f"Focus areas: {profile.focus_areas}")
