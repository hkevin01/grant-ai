"""
Grant Writing Assistant Service

This module integrates AI for Grant Writing prompts and techniques into the Grant AI platform,
providing AI-powered writing assistance for grant applications.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import click

from ..config import DATA_DIR


class GrantWritingAssistant:
    """
    AI-powered grant writing assistance using prompts from ai-for-grant-writing repository.
    
    This service provides writing assistance for grant applications by leveraging
    proven prompts and techniques from the AI for Grant Writing community.
    """
    
    def __init__(self):
        """Initialize the Grant Writing Assistant with prompts and templates."""
        self.prompts = self._load_prompts()
        self.templates = self._load_templates()
        
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from the AI for Grant Writing repository."""
        prompts_file = DATA_DIR / "templates" / "ai_grant_writing_prompts.json"
        
        if not prompts_file.exists():
            return self._get_default_prompts()
        
        try:
            with open(prompts_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """Get default prompts from AI for Grant Writing repository."""
        return {
            "clarity": {
                "enhance": """As a non-native English speaker, kindly help me revise the following text for improved understanding and clarity. Please check for spelling and sentence structure errors and suggest alternatives.

Text to improve: {text}

Please provide:
1. Corrected version with improved clarity
2. Specific suggestions for improvement
3. Alternative phrasings for complex sentences""",
                
                "identify_difficult": """Please identify any parts of my writing that may be difficult for a lay audience to understand.

Text to analyze: {text}

Please highlight:
1. Technical jargon that needs simplification
2. Complex sentences that could be broken down
3. Assumptions that may not be clear to reviewers
4. Suggestions for making the text more accessible"""
            },
            
            "compelling": {
                "persuasive": """Please provide feedback on my writing style and how I can make it more persuasive and compelling for the grant reviewer.

Text to improve: {text}

Please suggest:
1. Ways to strengthen the argument
2. More compelling language choices
3. Better hooks and transitions
4. Emotional appeals that could be added""",
                
                "strong_intro": """I'm trying to hook my reader with a strong introduction. Can you suggest a more captivating first sentence to draw them in from the start?

Current introduction: {text}

Please provide:
1. 3-5 alternative opening sentences
2. Explanation of why each is effective
3. Suggestions for building on the chosen opening"""
            },
            
            "structure": {
                "specific_aims": """I want to improve the overall structure of my Specific Aims. What tips do you have to structure it more effectively?

Current Specific Aims: {text}

Please suggest:
1. Better organization of aims
2. Logical flow improvements
3. Clear connections between aims
4. Effective transitions""",
                
                "significance": """Can you recommend an effective way to organize my Significance section to highlight the innovative aspects of our approach?

Current Significance section: {text}

Please suggest:
1. Better structure for impact presentation
2. Ways to emphasize innovation
3. Logical progression of arguments
4. Stronger conclusion statements"""
            },
            
            "alignment": {
                "mission": """I'm working on a grant application. Can you please review my text and suggest ways to better align it with {agency}'s mission?

Text to review: {text}

Please suggest:
1. Specific mission alignment points
2. Language that reflects the agency's priorities
3. Ways to emphasize shared goals
4. Examples that resonate with the agency's mission""",
                
                "review_criteria": """I am applying to {grant_name}. Please provide me feedback on how well I am addressing this review criteria: {criteria}, and suggestions for what I am missing and how I can improve.

Text to evaluate: {text}

Please provide:
1. Assessment of criteria coverage
2. Missing elements
3. Specific improvement suggestions
4. Examples of stronger responses"""
            },
            
            "titles": {
                "generate": """Suggest five potential titles for a grant proposal that will attract readers while encompassing the research question and key elements from the provided abstract.

Abstract summary: {abstract}

Please provide:
1. 5 compelling title options
2. Explanation of each title's strengths
3. Keywords that should be included
4. Length and style recommendations"""
            },
            
            "challenges": {
                "identify": """Help identify potential challenges that may arise with my proposed aims and suggest strategies to address them.

Specific aims: {aims}

Please identify:
1. Potential technical challenges
2. Feasibility concerns
3. Timeline risks
4. Resource limitations
5. Mitigation strategies for each challenge""",
                
                "reviewer_concerns": """What are some potential questions or concerns that {grant_name} reviewers may have regarding my specific aims?

Specific aims: {aims}

Please anticipate:
1. Technical feasibility questions
2. Innovation concerns
3. Impact questions
4. Methodology concerns
5. Suggested responses to each concern"""
            },
            
            "timeline": {
                "project": """Assist in developing a detailed project timeline and milestones for my grant proposal to demonstrate feasibility using my project summary and specific aims.

Project summary: {summary}

Please create:
1. Detailed timeline with milestones
2. Resource allocation suggestions
3. Risk mitigation timeline
4. Success metrics for each milestone""",
                
                "career_development": """Please develop a feasible project timeline for my grant proposal relating to my career development plan using this list of activities for {duration} months starting in {start_month}.

Activities: {activities}

Please create:
1. Monthly timeline with activities
2. Learning objectives for each period
3. Mentorship milestones
4. Publication and presentation goals"""
            }
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load writing templates for different grant types."""
        templates_file = DATA_DIR / "templates" / "grant_writing_templates.json"
        
        if not templates_file.exists():
            return self._get_default_templates()
        
        try:
            with open(templates_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._get_default_templates()
    
    def _get_default_templates(self) -> Dict[str, str]:
        """Get default writing templates."""
        return {
            "specific_aims": """SPECIFIC AIMS

{aim1_title}
{aim1_description}

{aim2_title}
{aim2_description}

{aim3_title}
{aim3_description}

Expected Outcomes:
{expected_outcomes}

Innovation:
{innovation_statement}""",
            
            "significance": """SIGNIFICANCE

Background:
{background}

Problem Statement:
{problem_statement}

Impact:
{impact_statement}

Innovation:
{innovation_description}

Expected Outcomes:
{expected_outcomes}""",
            
            "approach": """APPROACH

Overall Strategy:
{overall_strategy}

Specific Methods:
{specific_methods}

Timeline:
{timeline}

Expected Results:
{expected_results}

Alternative Approaches:
{alternative_approaches}""",
            
            "budget_justification": """BUDGET JUSTIFICATION

Personnel:
{personnel_justification}

Equipment:
{equipment_justification}

Supplies:
{supplies_justification}

Travel:
{travel_justification}

Other Expenses:
{other_expenses_justification}"""
        }
    
    def enhance_clarity(self, text: str) -> Dict[str, str]:
        """
        Enhance text clarity using AI for Grant Writing prompts.
        
        Args:
            text: Text to enhance
            
        Returns:
            Dictionary with enhanced text and suggestions
        """
        prompt = self.prompts["clarity"]["enhance"].format(text=text)
        
        # In a real implementation, this would call an AI service
        # For now, return a structured response
        return {
            "enhanced_text": f"Enhanced version of: {text[:100]}...",
            "suggestions": [
                "Simplify technical jargon",
                "Break down complex sentences",
                "Add transitional phrases",
                "Use active voice"
            ],
            "prompt_used": prompt
        }
    
    def make_compelling(self, text: str) -> Dict[str, str]:
        """
        Make text more compelling for grant reviewers.
        
        Args:
            text: Text to make more compelling
            
        Returns:
            Dictionary with compelling text and suggestions
        """
        prompt = self.prompts["compelling"]["persuasive"].format(text=text)
        
        return {
            "compelling_text": f"Compelling version of: {text[:100]}...",
            "suggestions": [
                "Add emotional appeals",
                "Use stronger action verbs",
                "Include specific examples",
                "Create urgency and importance"
            ],
            "prompt_used": prompt
        }
    
    def align_with_mission(self, text: str, funding_agency: str) -> Dict[str, str]:
        """
        Align text with funding agency mission.
        
        Args:
            text: Text to align
            funding_agency: Name of the funding agency
            
        Returns:
            Dictionary with aligned text and suggestions
        """
        prompt = self.prompts["alignment"]["mission"].format(
            agency=funding_agency, text=text
        )
        
        return {
            "aligned_text": f"Mission-aligned version of: {text[:100]}...",
            "suggestions": [
                f"Emphasize {funding_agency} priorities",
                "Use agency-specific language",
                "Reference agency goals",
                "Connect to agency impact areas"
            ],
            "prompt_used": prompt
        }
    
    def generate_title(self, abstract: str) -> List[Dict[str, str]]:
        """
        Generate compelling grant titles based on abstract.
        
        Args:
            abstract: Abstract or project summary
            
        Returns:
            List of title options with explanations
        """
        prompt = self.prompts["titles"]["generate"].format(abstract=abstract)
        
        return [
            {
                "title": f"Title Option {i+1}",
                "explanation": f"Explanation for title {i+1}",
                "strengths": ["Compelling", "Clear", "Specific"]
            }
            for i in range(5)
        ]
    
    def identify_challenges(self, aims: str) -> Dict[str, List[str]]:
        """
        Identify potential challenges and mitigation strategies.
        
        Args:
            aims: Specific aims text
            
        Returns:
            Dictionary with challenges and strategies
        """
        prompt = self.prompts["challenges"]["identify"].format(aims=aims)
        
        return {
            "technical_challenges": [
                "Sample technical challenge 1",
                "Sample technical challenge 2"
            ],
            "feasibility_concerns": [
                "Sample feasibility concern 1",
                "Sample feasibility concern 2"
            ],
            "mitigation_strategies": [
                "Sample mitigation strategy 1",
                "Sample mitigation strategy 2"
            ],
            "prompt_used": prompt
        }
    
    def create_timeline(self, summary: str, duration: str = "12 months") -> Dict[str, Any]:
        """
        Create detailed project timeline.
        
        Args:
            summary: Project summary
            duration: Project duration
            
        Returns:
            Dictionary with timeline and milestones
        """
        prompt = self.prompts["timeline"]["project"].format(summary=summary)
        
        return {
            "timeline": {
                "Month 1-3": "Project setup and preliminary work",
                "Month 4-6": "Data collection and analysis",
                "Month 7-9": "Implementation and testing",
                "Month 10-12": "Evaluation and reporting"
            },
            "milestones": [
                "Project initiation",
                "Data collection complete",
                "Analysis complete",
                "Final report"
            ],
            "prompt_used": prompt
        }
    
    def get_template(self, template_type: str, **kwargs) -> str:
        """
        Get a writing template for a specific grant section.
        
        Args:
            template_type: Type of template to get
            **kwargs: Variables to fill in the template
            
        Returns:
            Filled template
        """
        if template_type not in self.templates:
            raise ValueError(f"Unknown template type: {template_type}")
        
        template = self.templates[template_type]
        return template.format(**kwargs)
    
    def interactive_mode(self):
        """Launch interactive grant writing assistant."""
        click.echo("🎯 Grant Writing Assistant")
        click.echo("=" * 50)
        
        while True:
            click.echo("\nAvailable options:")
            click.echo("1. Enhance text clarity")
            click.echo("2. Make text more compelling")
            click.echo("3. Align with funding agency")
            click.echo("4. Generate grant title")
            click.echo("5. Identify challenges")
            click.echo("6. Create timeline")
            click.echo("7. Get writing template")
            click.echo("8. Exit")
            
            choice = click.prompt("Choose an option", type=int)
            
            if choice == 8:
                click.echo("Goodbye!")
                break
            
            try:
                if choice == 1:
                    text = click.prompt("Enter text to enhance")
                    result = self.enhance_clarity(text)
                    click.echo(f"\nEnhanced text: {result['enhanced_text']}")
                    click.echo("Suggestions:")
                    for suggestion in result['suggestions']:
                        click.echo(f"  - {suggestion}")
                
                elif choice == 2:
                    text = click.prompt("Enter text to make compelling")
                    result = self.make_compelling(text)
                    click.echo(f"\nCompelling text: {result['compelling_text']}")
                    click.echo("Suggestions:")
                    for suggestion in result['suggestions']:
                        click.echo(f"  - {suggestion}")
                
                elif choice == 3:
                    text = click.prompt("Enter text to align")
                    agency = click.prompt("Enter funding agency name")
                    result = self.align_with_mission(text, agency)
                    click.echo(f"\nAligned text: {result['aligned_text']}")
                    click.echo("Suggestions:")
                    for suggestion in result['suggestions']:
                        click.echo(f"  - {suggestion}")
                
                elif choice == 4:
                    abstract = click.prompt("Enter abstract or project summary")
                    titles = self.generate_title(abstract)
                    click.echo("\nTitle options:")
                    for i, title in enumerate(titles, 1):
                        click.echo(f"{i}. {title['title']}")
                        click.echo(f"   Explanation: {title['explanation']}")
                
                elif choice == 5:
                    aims = click.prompt("Enter specific aims")
                    challenges = self.identify_challenges(aims)
                    click.echo("\nIdentified challenges:")
                    for challenge in challenges['technical_challenges']:
                        click.echo(f"  - {challenge}")
                    click.echo("\nMitigation strategies:")
                    for strategy in challenges['mitigation_strategies']:
                        click.echo(f"  - {strategy}")
                
                elif choice == 6:
                    summary = click.prompt("Enter project summary")
                    duration = click.prompt("Enter project duration (e.g., '12 months')", default="12 months")
                    timeline = self.create_timeline(summary, duration)
                    click.echo("\nProject timeline:")
                    for period, activity in timeline['timeline'].items():
                        click.echo(f"  {period}: {activity}")
                
                elif choice == 7:
                    template_types = list(self.templates.keys())
                    click.echo("Available templates:")
                    for i, template_type in enumerate(template_types, 1):
                        click.echo(f"{i}. {template_type}")
                    
                    template_choice = click.prompt("Choose template", type=int) - 1
                    if 0 <= template_choice < len(template_types):
                        template_type = template_types[template_choice]
                        template = self.get_template(template_type)
                        click.echo(f"\n{template_type.upper()} Template:")
                        click.echo(template)
                    else:
                        click.echo("Invalid choice")
                
            except Exception as e:
                click.echo(f"Error: {e}")


def main():
    """Main entry point for the grant writing assistant."""
    assistant = GrantWritingAssistant()
    assistant.interactive_mode()


if __name__ == "__main__":
    main() 