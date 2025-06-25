"""
Questionnaire manager for handling questionnaire operations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..config import PROFILES_DIR
from ..models.organization import FocusArea, OrganizationProfile, ProgramType
from ..models.questionnaire import (
    Questionnaire,
    QuestionnaireResponse,
    create_default_questionnaire,
)


class QuestionnaireManager:
    """Manager for handling questionnaire operations."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the questionnaire manager."""
        self.data_dir = data_dir or PROFILES_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def get_default_questionnaire(self) -> Questionnaire:
        """Get the default organization profile questionnaire."""
        return create_default_questionnaire()

    def load_questionnaire(self, questionnaire_id: str) -> Optional[Questionnaire]:
        """Load a questionnaire from file."""
        questionnaire_file = self.data_dir / f"{questionnaire_id}.json"
        if not questionnaire_file.exists():
            return None

        try:
            with open(questionnaire_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Questionnaire(**data)
        except Exception as e:
            print(f"Error loading questionnaire: {e}")
            return None

    def save_questionnaire(self, questionnaire: Questionnaire) -> bool:
        """Save a questionnaire to file."""
        try:
            questionnaire_file = self.data_dir / f"{questionnaire.id}.json"
            with open(questionnaire_file, "w", encoding="utf-8") as f:
                json.dump(questionnaire.dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving questionnaire: {e}")
            return False

    def create_response(self, questionnaire_id: str) -> QuestionnaireResponse:
        """Create a new questionnaire response."""
        now = datetime.now().isoformat()
        return QuestionnaireResponse(
            questionnaire_id=questionnaire_id, created_at=now, updated_at=now, completed=False
        )

    def save_response(self, response: QuestionnaireResponse) -> bool:
        """Save a questionnaire response to file."""
        try:
            response_file = (
                self.data_dir
                / f"response_{response.questionnaire_id}_{response.created_at[:10]}.json"
            )
            with open(response_file, "w", encoding="utf-8") as f:
                json.dump(response.dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving response: {e}")
            return False

    def load_response(self, response_file: Path) -> Optional[QuestionnaireResponse]:
        """Load a questionnaire response from file."""
        try:
            with open(response_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return QuestionnaireResponse(**data)
        except Exception as e:
            print(f"Error loading response: {e}")
            return None

    def convert_response_to_profile(
        self, response: QuestionnaireResponse, questionnaire: Questionnaire
    ) -> Optional[OrganizationProfile]:
        """Convert a questionnaire response to an organization profile."""
        try:
            # Extract responses
            responses = response.responses

            # Map responses to profile fields
            profile_data = {}

            for question in questionnaire.questions:
                if question.field_mapping and question.id in responses:
                    value = responses[question.id]

                    # Handle special field mappings
                    if question.field_mapping == "focus_areas":
                        if isinstance(value, list):
                            profile_data["focus_areas"] = [FocusArea(area) for area in value]
                        else:
                            profile_data["focus_areas"] = []

                    elif question.field_mapping == "program_types":
                        if isinstance(value, list):
                            profile_data["program_types"] = [ProgramType(ptype) for ptype in value]
                        else:
                            profile_data["program_types"] = []

                    elif question.field_mapping == "target_demographics":
                        if isinstance(value, str):
                            profile_data["target_demographics"] = [
                                d.strip() for d in value.split(",") if d.strip()
                            ]
                        else:
                            profile_data["target_demographics"] = []

                    elif question.field_mapping == "preferred_grant_size_min":
                        # Handle grant size range
                        min_amount = value if value else 10000
                        max_amount = responses.get("preferred_grant_max", 100000)
                        profile_data["preferred_grant_size"] = (min_amount, max_amount)

                    elif question.field_mapping == "preferred_grant_size_max":
                        # Skip this as it's handled with min
                        continue

                    else:
                        # Direct mapping
                        profile_data[question.field_mapping] = value

            # Set defaults for missing required fields
            if "focus_areas" not in profile_data:
                profile_data["focus_areas"] = []
            if "program_types" not in profile_data:
                profile_data["program_types"] = []
            if "target_demographics" not in profile_data:
                profile_data["target_demographics"] = []
            if "preferred_grant_size" not in profile_data:
                profile_data["preferred_grant_size"] = (10000, 100000)

            # Create the profile
            return OrganizationProfile(**profile_data)

        except Exception as e:
            print(f"Error converting response to profile: {e}")
            return None

    def validate_response(
        self, response: QuestionnaireResponse, questionnaire: Questionnaire
    ) -> List[str]:
        """Validate a questionnaire response and return error messages."""
        errors = []

        for question in questionnaire.questions:
            if question.required and question.id not in response.responses:
                errors.append(f"Required field '{question.id}' is missing")
                continue

            if question.id in response.responses:
                value = response.responses[question.id]

                # Check for empty required fields
                if question.required and (value is None or value == ""):
                    errors.append(f"Required field '{question.id}' cannot be empty")
                    continue

                # Validate based on question type
                if question.question_type.value == "text":
                    if question.min_length and len(str(value)) < question.min_length:
                        errors.append(
                            f"'{question.id}' must be at least {question.min_length} characters"
                        )
                    if question.max_length and len(str(value)) > question.max_length:
                        errors.append(
                            f"'{question.id}' must be at most {question.max_length} characters"
                        )

                elif question.question_type.value == "number":
                    try:
                        num_value = float(value)
                        if question.min_value is not None and num_value < question.min_value:
                            errors.append(
                                f"'{question.id}' must be at least {question.min_value}"
                            )
                        if question.max_value is not None and num_value > question.max_value:
                            errors.append(f"'{question.id}' must be at most {question.max_value}")
                    except (ValueError, TypeError):
                        errors.append(f"'{question.id}' must be a valid number")

                elif question.question_type.value == "email":
                    if value and "@" not in str(value):
                        errors.append(f"'{question.id}' must be a valid email address")

        return errors
