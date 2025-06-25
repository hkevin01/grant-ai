"""
Questionnaire models for interactive organization profile creation.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .organization import FocusArea, ProgramType


class QuestionType(str, Enum):
    """Types of questions in the questionnaire."""
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    CHECKBOX = "checkbox"
    NUMBER = "number"
    EMAIL = "email"
    URL = "url"
    TEXTAREA = "textarea"


class Question(BaseModel):
    """Model representing a single question in the questionnaire."""
    
    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="Question text")
    question_type: QuestionType = Field(..., description="Type of question")
    required: bool = Field(True, description="Whether the question is required")
    help_text: Optional[str] = Field(None, description="Help text for the question")
    
    # For multiple choice questions
    options: Optional[List[str]] = Field(None, description="Available options")
    
    # For validation
    min_length: Optional[int] = Field(None, description="Minimum length for text")
    max_length: Optional[int] = Field(None, description="Maximum length for text")
    min_value: Optional[Union[int, float]] = Field(None, description="Minimum value for numbers")
    max_value: Optional[Union[int, float]] = Field(None, description="Maximum value for numbers")
    
    # For mapping to organization profile fields
    field_mapping: Optional[str] = Field(None, description="Corresponding field in OrganizationProfile")


class Questionnaire(BaseModel):
    """Model representing a complete questionnaire."""
    
    id: str = Field(..., description="Unique questionnaire identifier")
    title: str = Field(..., description="Questionnaire title")
    description: str = Field("", description="Questionnaire description")
    questions: List[Question] = Field(default_factory=list, description="List of questions")
    version: str = Field("1.0", description="Questionnaire version")
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get a question by its ID."""
        for question in self.questions:
            if question.id == question_id:
                return question
        return None
    
    def get_required_questions(self) -> List[Question]:
        """Get all required questions."""
        return [q for q in self.questions if q.required]


class QuestionnaireResponse(BaseModel):
    """Model representing a response to a questionnaire."""
    
    questionnaire_id: str = Field(..., description="ID of the questionnaire")
    responses: Dict[str, Any] = Field(default_factory=dict, description="Question ID to response mapping")
    completed: bool = Field(False, description="Whether the questionnaire is completed")
    created_at: str = Field(..., description="When the response was created")
    updated_at: str = Field(..., description="When the response was last updated")
    
    def get_response(self, question_id: str) -> Any:
        """Get response for a specific question."""
        return self.responses.get(question_id)
    
    def set_response(self, question_id: str, response: Any) -> None:
        """Set response for a specific question."""
        self.responses[question_id] = response
        self.updated_at = "now"  # In real implementation, use datetime
    
    def is_complete(self, questionnaire: Questionnaire) -> bool:
        """Check if all required questions are answered."""
        required_questions = questionnaire.get_required_questions()
        for question in required_questions:
            if question.id not in self.responses or not self.responses[question.id]:
                return False
        return True


def create_default_questionnaire() -> Questionnaire:
    """Create the default organization profile questionnaire."""
    return Questionnaire(
        id="org_profile_v1",
        title="Organization Profile Questionnaire",
        description="Please answer the following questions to create your organization profile.",
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
                id="org_description",
                text="Please describe your organization's mission and activities:",
                question_type=QuestionType.TEXTAREA,
                required=True,
                field_mapping="description",
                min_length=10,
                max_length=2000
            ),
            Question(
                id="focus_areas",
                text="What are your organization's primary focus areas? (Select all that apply)",
                question_type=QuestionType.CHECKBOX,
                required=True,
                options=[area.value for area in FocusArea],
                field_mapping="focus_areas"
            ),
            Question(
                id="program_types",
                text="What types of programs does your organization offer? (Select all that apply)",
                question_type=QuestionType.CHECKBOX,
                required=True,
                options=[ptype.value for ptype in ProgramType],
                field_mapping="program_types"
            ),
            Question(
                id="target_demographics",
                text="Who are your target demographics? (e.g., youth, seniors, families)",
                question_type=QuestionType.TEXT,
                required=False,
                field_mapping="target_demographics",
                help_text="Separate multiple demographics with commas"
            ),
            Question(
                id="annual_budget",
                text="What is your organization's annual operating budget? (USD)",
                question_type=QuestionType.NUMBER,
                required=False,
                field_mapping="annual_budget",
                min_value=0
            ),
            Question(
                id="location",
                text="Where is your organization located?",
                question_type=QuestionType.TEXT,
                required=True,
                field_mapping="location",
                max_length=200
            ),
            Question(
                id="website",
                text="What is your organization's website? (optional)",
                question_type=QuestionType.URL,
                required=False,
                field_mapping="website"
            ),
            Question(
                id="contact_name",
                text="What is the primary contact person's name?",
                question_type=QuestionType.TEXT,
                required=True,
                field_mapping="contact_name",
                max_length=100
            ),
            Question(
                id="contact_email",
                text="What is the primary contact email?",
                question_type=QuestionType.EMAIL,
                required=True,
                field_mapping="contact_email"
            ),
            Question(
                id="contact_phone",
                text="What is the primary contact phone number? (optional)",
                question_type=QuestionType.TEXT,
                required=False,
                field_mapping="contact_phone",
                max_length=20
            ),
            Question(
                id="ein",
                text="What is your organization's EIN (Employer Identification Number)? (optional)",
                question_type=QuestionType.TEXT,
                required=False,
                field_mapping="ein",
                help_text="Format: XX-XXXXXXX"
            ),
            Question(
                id="founded_year",
                text="In what year was your organization founded? (optional)",
                question_type=QuestionType.NUMBER,
                required=False,
                field_mapping="founded_year",
                min_value=1800,
                max_value=2024
            ),
            Question(
                id="preferred_grant_min",
                text="What is the minimum grant amount you typically seek? (USD)",
                question_type=QuestionType.NUMBER,
                required=False,
                field_mapping="preferred_grant_size_min",
                min_value=0
            ),
            Question(
                id="preferred_grant_max",
                text="What is the maximum grant amount you typically seek? (USD)",
                question_type=QuestionType.NUMBER,
                required=False,
                field_mapping="preferred_grant_size_max",
                min_value=0
            )
        ]
    ) 