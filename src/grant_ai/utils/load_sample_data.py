"""
Utility script to load sample data into the Grant AI system.
"""
import json
from pathlib import Path
from typing import List

from ..config import APPLICATIONS_DIR, DATA_DIR, PROFILES_DIR, TEMPLATES_DIR
from ..models.application_template import ApplicationTemplate
from ..models.application_tracking import ApplicationTracking
from ..models.organization import OrganizationProfile
from ..models.questionnaire import Questionnaire
from ..utils.questionnaire_manager import QuestionnaireManager
from ..utils.template_manager import TemplateManager
from ..utils.tracking_manager import TrackingManager


def load_sample_questionnaire() -> None:
    """Load the sample questionnaire."""
    questionnaire_file = DATA_DIR / "templates" / "sample_questionnaire.json"
    if not questionnaire_file.exists():
        print(f"Sample questionnaire file not found: {questionnaire_file}")
        return
    
    try:
        with open(questionnaire_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        questionnaire = Questionnaire(**data)
        manager = QuestionnaireManager()
        manager.save_questionnaire(questionnaire)
        print(f"✓ Loaded questionnaire: {questionnaire.title}")
    except Exception as e:
        print(f"✗ Error loading questionnaire: {e}")


def load_sample_organizations() -> None:
    """Load sample organization profiles."""
    profiles_file = DATA_DIR / "profiles" / "sample_organizations.json"
    if not profiles_file.exists():
        print(f"Sample organizations file not found: {profiles_file}")
        return
    
    try:
        with open(profiles_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Save profiles directly to files
        for org_data in data:
            profile = OrganizationProfile(**org_data)
            profile_file = PROFILES_DIR / f"{profile.name.lower().replace(' ', '_')}.json"
            with open(profile_file, "w", encoding="utf-8") as f:
                json.dump(profile.dict(), f, indent=2, ensure_ascii=False, default=str)
            print(f"✓ Loaded organization: {profile.name}")
    except Exception as e:
        print(f"✗ Error loading organizations: {e}")


def load_sample_application_template() -> None:
    """Load the sample application template."""
    template_file = DATA_DIR / "templates" / "sample_application_template.json"
    if not template_file.exists():
        print(f"Sample template file not found: {template_file}")
        return
    
    try:
        with open(template_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        template = ApplicationTemplate(**data)
        manager = TemplateManager()
        manager.save_template(template)
        print(f"✓ Loaded template: {template.name}")
    except Exception as e:
        print(f"✗ Error loading template: {e}")


def load_sample_tracking_data() -> None:
    """Load sample application tracking data."""
    tracking_file = DATA_DIR / "applications" / "sample_tracking.json"
    if not tracking_file.exists():
        print(f"Sample tracking file not found: {tracking_file}")
        return
    
    try:
        with open(tracking_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        manager = TrackingManager()
        for tracking_data in data:
            tracking = ApplicationTracking(**tracking_data)
            manager.save_tracking(tracking)
            print(f"✓ Loaded tracking: {tracking.application_id}")
    except Exception as e:
        print(f"✗ Error loading tracking data: {e}")


def create_sample_applications() -> None:
    """Create sample application responses using the template and organizations."""
    try:
        template_manager = TemplateManager()
        questionnaire_manager = QuestionnaireManager()
        
        # Get the template
        template = template_manager.load_template("general_grant_v1")
        if not template:
            print("✗ Template not found, skipping sample applications")
            return
        
        # Get organizations
        organizations = [
            "Youth Music Foundation",
            "Community Housing Initiative", 
            "STEM Robotics Academy"
        ]
        
        for i, org_name in enumerate(organizations, 1):
            # Create application
            application = template_manager.create_application(
                template_id="general_grant_v1",
                organization_id=f"org_{i}",
                grant_id=f"grant_2024_{i:03d}",
                created_by=f"user_{i}"
            )
            
            if application:
                # Add some sample responses
                application.responses.update({
                    "project_title": f"Sample Project {i}",
                    "project_description": f"This is a sample project description for {org_name}.",
                    "project_goals": "To improve community outcomes through innovative programming.",
                    "target_population": "Community members in need",
                    "project_duration": 12,
                    "requested_amount": 25000 + (i * 10000),
                    "budget_breakdown": "Personnel: 60%, Materials: 25%, Administrative: 15%",
                    "timeline": "Phase 1: Planning (3 months), Phase 2: Implementation (6 months), Phase 3: Evaluation (3 months)",
                    "expected_outcomes": "Improved community engagement and measurable positive impact.",
                    "evaluation_plan": "Regular assessments, surveys, and outcome tracking.",
                    "sustainability": "Long-term funding partnerships and community support."
                })
                
                template_manager.save_application(application)
                print(f"✓ Created sample application: {application.id}")
    except Exception as e:
        print(f"✗ Error creating sample applications: {e}")


def load_all_sample_data() -> None:
    """Load all sample data into the system."""
    print("Loading sample data into Grant AI system...")
    print("=" * 50)
    
    # Ensure directories exist
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    APPLICATIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data in order
    load_sample_questionnaire()
    load_sample_organizations()
    load_sample_application_template()
    load_sample_tracking_data()
    create_sample_applications()
    
    print("=" * 50)
    print("Sample data loading complete!")


if __name__ == "__main__":
    load_all_sample_data() 