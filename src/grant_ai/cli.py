"""Command line interface for Grant AI."""

import click
import json
from pathlib import Path
from typing import Optional

from grant_ai.models.organization import (
    OrganizationProfile,
    FocusArea,
    ProgramType
)
from grant_ai.analysis.grant_researcher import GrantResearcher


@click.group()
@click.version_option()
def main():
    """Grant AI - AI-powered grant research and application management."""
    pass


@main.group()
def profile():
    """Manage organization profiles."""
    pass


@profile.command()
@click.option('--name', required=True, help='Organization name')
@click.option('--description', help='Organization description')
@click.option('--focus-area', multiple=True,
              type=click.Choice([area.value for area in FocusArea]),
              help='Organization focus areas')
@click.option('--program-type', multiple=True,
              type=click.Choice([ptype.value for ptype in ProgramType]),
              help='Program types offered')
@click.option('--budget', type=int, help='Annual budget in USD')
@click.option('--location', help='Primary location')
@click.option('--website', help='Organization website')
@click.option('--contact-name', help='Primary contact name')
@click.option('--contact-email', help='Primary contact email')
@click.option('--output', '-o', help='Output file path (JSON)')
def create(name: str, description: Optional[str], focus_area: tuple,
           program_type: tuple, budget: Optional[int], location: Optional[str],
           website: Optional[str], contact_name: Optional[str],
           contact_email: Optional[str], output: Optional[str]):
    """Create a new organization profile."""
    
    # Convert focus areas and program types
    focus_areas = [FocusArea(area) for area in focus_area]
    program_types = [ProgramType(ptype) for ptype in program_type]
    
    # Create organization profile
    org = OrganizationProfile(
        name=name,
        description=description or "",
        focus_areas=focus_areas,
        program_types=program_types,
        annual_budget=budget,
        location=location or "",
        website=website,
        contact_name=contact_name or "",
        contact_email=contact_email or ""
    )
    
    # Save to file
    output_path = output or f"{name.lower().replace(' ', '_')}_profile.json"
    with open(output_path, 'w') as f:
        json.dump(org.dict(), f, indent=2, default=str)
    
    click.echo(f"Organization profile created: {output_path}")


@profile.command()
@click.argument('profile_file', type=click.Path(exists=True))
def show(profile_file: str):
    """Display organization profile details."""
    with open(profile_file, 'r') as f:
        profile_data = json.load(f)
    
    org = OrganizationProfile(**profile_data)
    
    click.echo(f"Organization: {org.name}")
    click.echo(f"Description: {org.description}")
    click.echo(f"Focus Areas: {', '.join(org.focus_areas)}")
    click.echo(f"Program Types: {', '.join(org.program_types)}")
    if org.annual_budget:
        click.echo(f"Annual Budget: ${org.annual_budget:,}")
    click.echo(f"Location: {org.location}")
    if org.website:
        click.echo(f"Website: {org.website}")


@main.group()
def research():
    """Research grants and AI companies."""
    pass


@research.command()
@click.option('--focus', multiple=True, help='Focus areas to search for')
@click.option('--company-type', default='ai',
              help='Type of companies to research')
@click.option('--output', '-o', help='Output file path')
def research_companies(focus: tuple, company_type: str, output: Optional[str]):
    """Research AI companies with grant programs."""
    focus_str = ', '.join(focus)
    click.echo(f"Researching {company_type} companies with focus on:")
    click.echo(f"  {focus_str}")
    
    # This would be implemented with actual web scraping
    # For now, show what the command would do
    click.echo("This feature will be implemented to:")
    click.echo("1. Search for AI companies with grant programs")
    click.echo("2. Filter by focus areas and reputation")
    click.echo("3. Generate a report of suitable companies")
    
    if output:
        click.echo(f"Results would be saved to: {output}")


@main.group()
def match():
    """Match organizations with grants and companies."""
    pass


@match.command()
@click.argument('profile_file', type=click.Path(exists=True))
@click.option('--min-score', default=0.4, help='Minimum match score (0.0-1.0)')
@click.option('--limit', type=int, help='Maximum number of results')
@click.option('--output', '-o', help='Output file path')
def grants(profile_file: str, min_score: float, limit: Optional[int], 
           output: Optional[str]):
    """Find grants matching an organization profile."""
    
    # Load organization profile
    with open(profile_file, 'r') as f:
        profile_data = json.load(f)
    
    org = OrganizationProfile(**profile_data)
    
    # Initialize researcher (would load from database in real implementation)
    researcher = GrantResearcher()
    
    click.echo(f"Searching for grants matching {org.name}...")
    click.echo(f"Minimum match score: {min_score}")
    
    # This would use actual grant data
    click.echo("This feature will be implemented to:")
    click.echo("1. Load grant database")
    click.echo("2. Calculate match scores based on organization profile")
    click.echo("3. Generate ranked list of suitable grants")
    
    if output:
        click.echo(f"Results would be saved to: {output}")


@match.command()
@click.argument('profile_file', type=click.Path(exists=True))
@click.option('--min-score', default=0.4, help='Minimum match score (0.0-1.0)')
@click.option('--limit', type=int, help='Maximum number of results')
@click.option('--output', '-o', help='Output file path')
def companies(profile_file: str, min_score: float, limit: Optional[int],
              output: Optional[str]):
    """Find AI companies matching an organization profile."""
    
    # Load organization profile
    with open(profile_file, 'r') as f:
        profile_data = json.load(f)
    
    org = OrganizationProfile(**profile_data)
    
    click.echo(f"Searching for AI companies matching {org.name}...")
    click.echo(f"Minimum match score: {min_score}")
    
    # This would use actual company data
    click.echo("This feature will be implemented to:")
    click.echo("1. Load AI company database")
    click.echo("2. Filter companies with grant programs")
    click.echo("3. Calculate match scores and generate shortlist")
    
    if output:
        click.echo(f"Results would be saved to: {output}")


@main.command()
def examples():
    """Show example usage and create sample data."""
    click.echo("Creating sample organization profiles...")
    
    # Create CODA profile
    coda = OrganizationProfile(
        name="CODA",
        description="Community organization focused on education programs in music, art, and robotics",
        focus_areas=[FocusArea.MUSIC_EDUCATION, FocusArea.ART_EDUCATION, FocusArea.ROBOTICS],
        program_types=[ProgramType.AFTER_SCHOOL, ProgramType.SUMMER_CAMPS],
        target_demographics=["youth", "students", "families"],
        annual_budget=250000,
        location="Local Community",
        contact_name="Program Director",
        contact_email="info@coda.org"
    )
    
    with open('coda_profile.json', 'w') as f:
        json.dump(coda.dict(), f, indent=2, default=str)
    
    # Create NRG Development profile
    nrg = OrganizationProfile(
        name="Christian Pocket Community/NRG Development",
        description="Developing affordable, efficient housing for retired people with support for struggling single mothers",
        focus_areas=[FocusArea.AFFORDABLE_HOUSING, FocusArea.COMMUNITY_DEVELOPMENT, FocusArea.SENIOR_SERVICES],
        program_types=[ProgramType.HOUSING_DEVELOPMENT, ProgramType.SUPPORT_SERVICES],
        target_demographics=["retired people", "single mothers", "low-income families"],
        annual_budget=500000,
        location="Regional",
        contact_name="Development Director",
        contact_email="info@nrgdev.org"
    )
    
    with open('nrg_profile.json', 'w') as f:
        json.dump(nrg.dict(), f, indent=2, default=str)
    
    click.echo("Sample profiles created:")
    click.echo("- coda_profile.json")
    click.echo("- nrg_profile.json")
    
    click.echo("\nExample commands:")
    click.echo("grant-ai profile show coda_profile.json")
    click.echo("grant-ai match grants coda_profile.json --output coda_grants.xlsx")
    click.echo("grant-ai match companies nrg_profile.json --min-score 0.5")


if __name__ == '__main__':
    main()
