"""
AI-powered questionnaire filler service.

This service uses lightweight LLMs to intelligently fill out organization
questionnaires based on basic organization information.
"""

import json
import re
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import time

class AIQuestionnaireFiller:
    """Service for AI-powered questionnaire filling."""
    
    def __init__(self, model_name: str = "deepseek-coder", api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        import os
        # Try different environment variables
        for key in ["DEEPSEEK_API_KEY", "OPENAI_API_KEY", "AI_API_KEY"]:
            if os.getenv(key):
                return os.getenv(key)
        
        # Try to read from config file
        config_path = Path.home() / ".grant_ai" / "ai_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get("api_key", "")
            except:
                pass
        
        return ""
    
    def fill_questionnaire(self, org_name: str, org_description: str = "", 
                         location: str = "", website: str = "") -> Dict[str, Any]:
        """
        Fill out a complete questionnaire using AI based on organization information.
        
        Args:
            org_name: Organization name
            org_description: Brief description of the organization
            location: Organization location
            website: Organization website
            
        Returns:
            Dictionary with filled questionnaire responses
        """
        try:
            # Create a comprehensive prompt for the AI
            prompt = self._create_fill_prompt(org_name, org_description, location, website)
            
            # Get AI response
            ai_response = self._get_ai_response(prompt)
            
            # Parse the response into structured data
            filled_responses = self._parse_ai_response(ai_response)
            
            # Validate and clean the responses
            cleaned_responses = self._validate_responses(filled_responses)
            
            return cleaned_responses
            
        except Exception as e:
            print(f"Error filling questionnaire with AI: {e}")
            # Return basic fallback responses
            return self._get_fallback_responses(org_name, org_description, location, website)
    
    def _create_fill_prompt(self, org_name: str, org_description: str, 
                           location: str, website: str) -> str:
        """Create a comprehensive prompt for the AI to fill the questionnaire."""
        
        prompt = f"""
You are an expert grant consultant helping to fill out an organization profile questionnaire. 
Based on the following organization information, please provide intelligent, realistic responses 
for all questionnaire fields.

ORGANIZATION INFORMATION:
- Name: {org_name}
- Description: {org_description or 'Not provided'}
- Location: {location or 'Not provided'}
- Website: {website or 'Not provided'}

QUESTIONNAIRE FIELDS TO FILL:

1. Organization Name: {org_name}

2. Organization Description: Provide a compelling 2-3 sentence description of the organization's mission and impact.

3. Focus Areas (select all that apply): education, music_education, art_education, robotics, housing, affordable_housing, community_development, social_services, youth_development, senior_services

4. Program Types (select all that apply): after_school, summer_camps, housing_development, support_services, educational_workshops, community_outreach

5. Target Demographics: Who does this organization serve? (e.g., "youth ages 5-18, low-income families, rural communities")

6. Annual Budget: Estimate a realistic annual operating budget in USD

7. Location: {location or 'Provide a realistic location'}

8. Website: {website or 'Provide a realistic website URL'}

9. EIN: Generate a realistic EIN in format XX-XXXXXXX

10. Founded Year: Estimate when this organization was likely founded (between 1900-2024)

11. Preferred Grant Range: Suggest realistic minimum and maximum grant amounts this organization would seek

12. Contact Information: Generate realistic contact person name, email, and phone number

Please respond in JSON format with the following structure:
{{
    "org_name": "exact name provided",
    "org_description": "compelling description",
    "focus_areas": ["list", "of", "selected", "focus", "areas"],
    "program_types": ["list", "of", "selected", "program", "types"],
    "target_demographics": "target audience description",
    "annual_budget": 500000,
    "location": "City, State",
    "website": "https://www.example.org",
    "ein": "12-3456789",
    "founded_year": 2010,
    "preferred_grant_min": 10000,
    "preferred_grant_max": 100000,
    "contact_name": "John Smith",
    "contact_email": "john@example.org",
    "contact_phone": "555-123-4567"
}}

IMPORTANT GUIDELINES:
- Make responses realistic and appropriate for the organization type
- If the organization name suggests education focus, prioritize education-related focus areas
- If location is provided, use it; otherwise suggest a realistic location
- Generate realistic contact information that matches the organization
- Ensure all responses are appropriate for grant applications
- Make the organization sound professional and impactful
"""
        
        return prompt
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI model."""
        
        # Try DeepSeek first
        if self.api_key and "deepseek" in self.model_name.lower():
            return self._call_deepseek_api(prompt)
        
        # Fallback to local model or other API
        return self._call_fallback_api(prompt)
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """Call DeepSeek API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-coder:6.7b-instruct",
                "messages": [
                    {"role": "system", "content": "You are a helpful grant consultant assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            return ""
    
    def _call_fallback_api(self, prompt: str) -> str:
        """Fallback API call or local model."""
        try:
            # Try OpenAI as fallback
            if self.api_key:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful grant consultant assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions", 
                    headers=headers, json=data, timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            print(f"Fallback API error: {e}")
        
        return ""
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            
            # If no JSON found, try to parse manually
            return self._parse_text_response(ai_response)
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return {}
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails."""
        responses = {}
        
        # Extract key-value pairs from text
        lines = text.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip().strip('"').strip("'")
                
                # Convert to appropriate types
                if key in ['annual_budget', 'founded_year', 'preferred_grant_min', 'preferred_grant_max']:
                    try:
                        responses[key] = int(value)
                    except:
                        responses[key] = 0
                elif key in ['focus_areas', 'program_types']:
                    # Parse list format
                    if '[' in value and ']' in value:
                        items = re.findall(r'"([^"]*)"', value)
                        responses[key] = items
                    else:
                        responses[key] = [value]
                else:
                    responses[key] = value
        
        return responses
    
    def _validate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the AI responses."""
        cleaned = {}
        
        # Ensure required fields have values
        required_fields = {
            'org_name': str,
            'org_description': str,
            'focus_areas': list,
            'program_types': list,
            'target_demographics': str,
            'location': str,
            'contact_name': str,
            'contact_email': str,
            'contact_phone': str
        }
        
        for field, field_type in required_fields.items():
            if field in responses:
                value = responses[field]
                if field_type == list and not isinstance(value, list):
                    cleaned[field] = [str(value)]
                elif field_type == str and not isinstance(value, str):
                    cleaned[field] = str(value)
                else:
                    cleaned[field] = value
            else:
                # Provide default values
                if field_type == list:
                    cleaned[field] = []
                else:
                    cleaned[field] = ""
        
        # Validate specific fields
        if 'annual_budget' not in responses or not responses['annual_budget']:
            cleaned['annual_budget'] = 500000
        
        if 'founded_year' not in responses or not responses['founded_year']:
            cleaned['founded_year'] = 2010
        
        if 'preferred_grant_min' not in responses or not responses['preferred_grant_min']:
            cleaned['preferred_grant_min'] = 10000
        
        if 'preferred_grant_max' not in responses or not responses['preferred_grant_max']:
            cleaned['preferred_grant_max'] = 100000
        
        # Validate EIN format
        if 'ein' in responses and responses['ein']:
            ein = responses['ein']
            if not re.match(r'^\d{2}-\d{7}$', ein):
                cleaned['ein'] = "12-3456789"
        else:
            cleaned['ein'] = "12-3456789"
        
        # Validate phone format
        if 'contact_phone' in responses and responses['contact_phone']:
            phone = responses['contact_phone']
            if not re.match(r'^\d{3}-\d{3}-\d{4}$', phone):
                cleaned['contact_phone'] = "555-123-4567"
        else:
            cleaned['contact_phone'] = "555-123-4567"
        
        return cleaned
    
    def _get_fallback_responses(self, org_name: str, org_description: str, 
                               location: str, website: str) -> Dict[str, Any]:
        """Provide fallback responses when AI fails."""
        
        # Analyze organization name to determine focus areas
        name_lower = org_name.lower()
        focus_areas = []
        program_types = []
        
        if any(word in name_lower for word in ['academy', 'school', 'education', 'learning']):
            focus_areas.extend(['education', 'youth_development'])
            program_types.extend(['after_school', 'educational_workshops'])
        
        if any(word in name_lower for word in ['music', 'art', 'creative']):
            focus_areas.extend(['music_education', 'art_education'])
            program_types.extend(['after_school', 'summer_camps'])
        
        if any(word in name_lower for word in ['robotics', 'tech', 'stem']):
            focus_areas.extend(['education', 'youth_development'])
            program_types.extend(['after_school', 'educational_workshops'])
        
        if any(word in name_lower for word in ['housing', 'home', 'shelter']):
            focus_areas.extend(['housing', 'affordable_housing', 'community_development'])
            program_types.extend(['housing_development', 'support_services'])
        
        if any(word in name_lower for word in ['community', 'neighborhood']):
            focus_areas.extend(['community_development', 'social_services'])
            program_types.extend(['community_outreach', 'support_services'])
        
        # Default focus areas if none detected
        if not focus_areas:
            focus_areas = ['education', 'youth_development']
            program_types = ['after_school', 'educational_workshops']
        
        return {
            'org_name': org_name,
            'org_description': org_description or f"{org_name} is dedicated to serving our community through innovative programs and initiatives.",
            'focus_areas': focus_areas,
            'program_types': program_types,
            'target_demographics': 'youth, families, community members',
            'annual_budget': 500000,
            'location': location or 'Charleston, WV',
            'website': website or f"https://www.{org_name.lower().replace(' ', '')}.org",
            'ein': '12-3456789',
            'founded_year': 2010,
            'preferred_grant_min': 10000,
            'preferred_grant_max': 100000,
            'contact_name': 'John Smith',
            'contact_email': f'contact@{org_name.lower().replace(" ", "")}.org',
            'contact_phone': '555-123-4567'
        } 