"""Command line interface for Grant AI."""

import json
import time
from pathlib import Path
from typing import Optional

import click

from ..analysis.grant_researcher import GrantResearcher

# Import AI and Analytics CLI groups
from ..cli.ai_commands import ai
from ..cli.ai_writing_commands import ai_writing_commands
from ..cli.analytics_commands import analytics
from ..models.organization import FocusArea, OrganizationProfile, ProgramType
from ..services.grant_writing import GrantWritingAssistant
from ..services.organization_scraper import OrganizationScraper
from ..services.usaspending_scraper import USASpendingScraper
from ..utils.questionnaire_manager import QuestionnaireManager
from ..utils.reporting import ReportGenerator
from ..utils.template_manager import TemplateManager
from ..utils.tracking_manager import TrackingManager


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
@click.option("--name", required=True, help="Organization name")
@click.option("--description", help="Organization description")
@click.option(
    "--focus-area",
    multiple=True,
    type=click.Choice([area.value for area in FocusArea]),
    help="Organization focus areas",
)
@click.option(
    "--program-type",
    multiple=True,
    type=click.Choice([ptype.value for ptype in ProgramType]),
    help="Program types offered",
)
@click.option("--budget", type=int, help="Annual budget in USD")
@click.option("--location", help="Primary location")
@click.option("--website", help="Organization website")
@click.option("--contact-name", help="Primary contact name")
@click.option("--contact-email", help="Primary contact email")
@click.option("--output", "-o", help="Output file path (JSON)")
def create(
    name: str,
    description: Optional[str],
    focus_area: tuple,
    program_type: tuple,
    budget: Optional[int],
    location: Optional[str],
    website: Optional[str],
    contact_name: Optional[str],
    contact_email: Optional[str],
    output: Optional[str],
):
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
        contact_email=contact_email or "",
        ein=None,
        founded_year=None,
        preferred_grant_size=(10000, 100000),
        contact_phone="",
    )

    # Save to file
    output_path = output or f"{name.lower().replace(' ', '_')}_profile.json"
    with open(output_path, "w") as f:
        json.dump(org.model_dump(), f, indent=2, default=str)

    click.echo(f"Organization profile created: {output_path}")


@profile.command()
@click.argument("profile_file", type=click.Path(exists=True))
def show(profile_file: str):
    """Display organization profile details."""
    with open(profile_file, "r") as f:
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
@click.option("--focus", multiple=True, help="Focus areas to search for")
@click.option("--company-type", default="ai", help="Type of companies to research")
@click.option("--output", "-o", help="Output file path")
def research_companies(focus: tuple, company_type: str, output: Optional[str]):
    """Research AI companies with grant programs."""
    focus_str = ", ".join(focus)
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
@click.argument("profile_file", type=click.Path(exists=True))
@click.option("--min-score", default=0.4, help="Minimum match score (0.0-1.0)")
@click.option("--limit", type=int, help="Maximum number of results")
@click.option("--output", "-o", help="Output file path")
def grants(profile_file: str, min_score: float, limit: Optional[int], output: Optional[str]):
    """Find grants matching an organization profile."""

    # Load organization profile
    with open(profile_file, "r") as f:
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
@click.argument("profile_file", type=click.Path(exists=True))
@click.option("--min-score", default=0.4, help="Minimum match score (0.0-1.0)")
@click.option("--limit", type=int, help="Maximum number of results")
@click.option("--output", "-o", help="Output file path")
def companies(profile_file: str, min_score: float, limit: Optional[int], output: Optional[str]):
    """Find AI companies matching an organization profile."""

    # Load organization profile
    with open(profile_file, "r") as f:
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
        description="Community organization focused on education programs in "
        "music, art, and robotics",
        focus_areas=[FocusArea.MUSIC_EDUCATION, FocusArea.ART_EDUCATION, FocusArea.ROBOTICS],
        program_types=[ProgramType.AFTER_SCHOOL, ProgramType.SUMMER_CAMPS],
        target_demographics=["youth", "students", "families"],
        annual_budget=250000,
        location="Local Community",
        contact_name="Program Director",
        contact_email="info@coda.org",
        website=None,
        ein=None,
        founded_year=None,
        preferred_grant_size=(10000, 100000),
        contact_phone="",
    )

    with open("coda_profile.json", "w") as f:
        json.dump(coda.model_dump(), f, indent=2, default=str)

    # Create NRG Development profile
    nrg = OrganizationProfile(
        name="Christian Pocket Community/NRG Development",
        description="Developing affordable, efficient housing for retired people "
        "with support for struggling single mothers",
        focus_areas=[
            FocusArea.AFFORDABLE_HOUSING,
            FocusArea.COMMUNITY_DEVELOPMENT,
            FocusArea.SENIOR_SERVICES,
        ],
        program_types=[ProgramType.HOUSING_DEVELOPMENT, ProgramType.SUPPORT_SERVICES],
        target_demographics=["retired people", "single mothers", "low-income families"],
        annual_budget=500000,
        location="Regional",
        contact_name="Development Director",
        contact_email="info@nrgdev.org",
        website=None,
        ein=None,
        founded_year=None,
        preferred_grant_size=(10000, 100000),
        contact_phone="",
    )

    with open("nrg_profile.json", "w") as f:
        json.dump(nrg.model_dump(), f, indent=2, default=str)

    click.echo("Sample profiles created:")
    click.echo("- coda_profile.json")
    click.echo("- nrg_profile.json")

    click.echo("\nExample commands:")
    click.echo("grant-ai profile show coda_profile.json")
    click.echo("grant-ai match grants coda_profile.json --output coda_grants.xlsx")
    click.echo("grant-ai match companies nrg_profile.json --min-score 0.5")


@main.group()
def questionnaire():
    """Manage organization questionnaires."""
    pass


@questionnaire.command()
@click.option("--output", "-o", help="Output file path for the profile")
def create_profile(output: Optional[str]):
    """Create an organization profile using an interactive questionnaire."""
    manager = QuestionnaireManager()
    questionnaire = manager.get_default_questionnaire()
    response = manager.create_response(questionnaire.id)

    click.echo(f"🎯 {questionnaire.title}")
    click.echo(f"📝 {questionnaire.description}")
    click.echo()

    # Ask each question
    for question in questionnaire.questions:
        click.echo(f"❓ {question.text}")
        if question.help_text:
            click.echo(f"💡 {question.help_text}")

        if question.question_type.value == "text":
            value = click.prompt("Answer", type=str, default="")
            if value:
                response.set_response(question.id, value)

        elif question.question_type.value == "textarea":
            click.echo("Enter your answer (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines:
                    break
                lines.append(line)
            value = "\n".join(lines)
            if value:
                response.set_response(question.id, value)

        elif question.question_type.value == "number":
            value = click.prompt("Answer", type=int, default=None)
            if value is not None:
                response.set_response(question.id, value)

        elif question.question_type.value == "email":
            value = click.prompt("Answer", type=str, default="")
            if value:
                response.set_response(question.id, value)

        elif question.question_type.value == "url":
            value = click.prompt("Answer", type=str, default="")
            if value:
                response.set_response(question.id, value)

        elif question.question_type.value == "checkbox":
            if question.options:
                click.echo("Select options (comma-separated numbers):")
                for i, option in enumerate(question.options, 1):
                    click.echo(f"  {i}. {option}")
                selection = click.prompt("Answer", type=str, default="")
                if selection:
                    try:
                        indices = [int(x.strip()) - 1 for x in selection.split(",")]
                        selected = [
                            question.options[i] for i in indices if 0 <= i < len(question.options)
                        ]
                        response.set_response(question.id, selected)
                    except (ValueError, IndexError):
                        click.echo("Invalid selection, skipping...")

        elif question.question_type.value == "multiple_choice":
            if question.options:
                click.echo("Select an option:")
                for i, option in enumerate(question.options, 1):
                    click.echo(f"  {i}. {option}")
                selection = click.prompt("Answer", type=int, default=None)
                if selection and 1 <= selection <= len(question.options):
                    response.set_response(question.id, question.options[selection - 1])

        click.echo()

    # Validate response
    errors = manager.validate_response(response, questionnaire)
    if errors:
        click.echo("❌ Validation errors:")
        for error in errors:
            click.echo(f"  - {error}")
        return

    # Convert to profile
    profile = manager.convert_response_to_profile(response, questionnaire)
    if not profile:
        click.echo("❌ Failed to create profile from questionnaire")
        return

    # Save profile
    output_path = output or f"{profile.name.lower().replace(' ', '_')}_profile.json"
    with open(output_path, "w") as f:
        json.dump(profile.model_dump(), f, indent=2, default=str)

    click.echo(f"✅ Organization profile created: {output_path}")
    click.echo(f"📊 Organization: {profile.name}")
    click.echo(f"🎯 Focus Areas: {', '.join(str(area) for area in profile.focus_areas)}")
    click.echo(f"📋 Program Types: {', '.join(str(ptype) for ptype in profile.program_types)}")


@questionnaire.command()
def show_questionnaire():
    """Show the default questionnaire."""
    manager = QuestionnaireManager()
    questionnaire = manager.get_default_questionnaire()

    click.echo(f"📋 {questionnaire.title}")
    click.echo(f"📝 {questionnaire.description}")
    click.echo(f"📊 Version: {questionnaire.version}")
    click.echo(f"❓ Total Questions: {len(questionnaire.questions)}")
    click.echo()

    for i, question in enumerate(questionnaire.questions, 1):
        click.echo(f"{i}. {question.text}")
        if question.help_text:
            click.echo(f"   💡 {question.help_text}")
        click.echo(f"   Type: {question.question_type.value}")
        click.echo(f"   Required: {'Yes' if question.required else 'No'}")
        if question.options:
            click.echo(f"   Options: {', '.join(question.options)}")
        click.echo()


@main.group()
def template():
    """Manage application templates."""
    pass


@template.command()
def list():
    """List all available application templates."""
    manager = TemplateManager()
    templates = manager.list_templates()

    if not templates:
        # Create default template if none exist
        default_template = manager.get_default_template()
        manager.save_template(default_template)
        templates = [default_template]

    click.echo(f"📋 Found {len(templates)} template(s):")
    click.echo()

    for template in templates:
        click.echo(f"🆔 {template.id}")
        click.echo(f"📝 {template.name}")
        click.echo(f"📄 {template.description}")
        click.echo(f"🏢 {template.organization}")
        click.echo(f"📊 {len(template.fields)} fields")
        click.echo(f"📅 Created: {template.created_at}")
        click.echo()


@template.command()
@click.argument("template_id")
def show_template(template_id: str):
    """Show details of a specific template."""
    manager = TemplateManager()
    template = manager.load_template(template_id)

    if not template:
        click.echo(f"❌ Template '{template_id}' not found")
        return

    click.echo(f"📋 {template.name}")
    click.echo(f"📝 {template.description}")
    click.echo(f"🏢 Organization: {template.organization}")
    click.echo(f"📊 Grant Type: {template.grant_type}")
    click.echo(f"📅 Created: {template.created_at}")
    click.echo(f"👤 Created by: {template.created_by}")
    click.echo()

    click.echo("📋 Fields:")
    for field in template.get_fields_in_order():
        click.echo(f"  {field.order}. {field.label}")
        click.echo(f"     Type: {field.field_type.value}")
        click.echo(f"     Required: {'Yes' if field.required else 'No'}")
        if field.help_text:
            click.echo(f"     Help: {field.help_text}")
        click.echo()


@template.command()
@click.argument("template_id")
@click.argument("organization_id")
@click.option("--grant-id", help="Grant ID being applied for")
@click.option("--output", "-o", help="Output file path")
def create_application(
    template_id: str, organization_id: str, grant_id: str, output: Optional[str]
):
    """Create a new application using a template."""
    manager = TemplateManager()

    # Load template
    template = manager.load_template(template_id)
    if not template:
        click.echo(f"❌ Template '{template_id}' not found")
        return

    # Create application
    application = manager.create_application(
        template_id=template_id,
        organization_id=organization_id,
        grant_id=grant_id or "",
        created_by="CLI User",
    )

    if not application:
        click.echo("❌ Failed to create application")
        return

    click.echo(f"📝 Creating application using template: {template.name}")
    click.echo(f"🆔 Application ID: {application.id}")
    click.echo()

    # Fill out the application
    for field in template.get_fields_in_order():
        click.echo(f"❓ {field.label}")
        if field.help_text:
            click.echo(f"💡 {field.help_text}")

        if field.field_type.value == "text":
            value = click.prompt("Answer", type=str, default="")
            if value:
                application.set_response(field.id, value)

        elif field.field_type.value == "textarea":
            click.echo("Enter your answer (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines:
                    break
                lines.append(line)
            value = "\n".join(lines)
            if value:
                application.set_response(field.id, value)

        elif field.field_type.value == "number":
            value = click.prompt("Answer", type=float, default=None)
            if value is not None:
                application.set_response(field.id, value)

        elif field.field_type.value == "date":
            value = click.prompt("Answer (YYYY-MM-DD)", type=str, default="")
            if value:
                application.set_response(field.id, value)

        elif field.field_type.value == "email":
            value = click.prompt("Answer", type=str, default="")
            if value:
                application.set_response(field.id, value)

        elif field.field_type.value == "url":
            value = click.prompt("Answer", type=str, default="")
            if value:
                application.set_response(field.id, value)

        elif field.field_type.value == "multiple_choice":
            if field.options:
                click.echo("Select an option:")
                for i, option in enumerate(field.options, 1):
                    click.echo(f"  {i}. {option}")
                selection = click.prompt("Answer", type=int, default=None)
                if selection and 1 <= selection <= len(field.options):
                    application.set_response(field.id, field.options[selection - 1])

        elif field.field_type.value == "checkbox":
            if field.options:
                click.echo("Select options (comma-separated numbers):")
                for i, option in enumerate(field.options, 1):
                    click.echo(f"  {i}. {option}")
                selection = click.prompt("Answer", type=str, default="")
                if selection:
                    try:
                        indices = [int(x.strip()) - 1 for x in selection.split(",")]
                        selected = [
                            field.options[i] for i in indices if 0 <= i < len(field.options)
                        ]
                        application.set_response(field.id, selected)
                    except (ValueError, IndexError):
                        click.echo("Invalid selection, skipping...")

        click.echo()

    # Validate application
    errors = manager.validate_application(application, template)
    if errors:
        click.echo("❌ Validation errors:")
        for error in errors:
            click.echo(f"  - {error}")
        return

    # Save application
    if manager.save_application(application):
        click.echo(f"✅ Application saved: {application.id}")

        # Export if requested
        if output:
            export_data = manager.export_application(application, template, "json")
            if export_data:
                with open(output, "w") as f:
                    f.write(export_data)
                click.echo(f"📄 Application exported to: {output}")
    else:
        click.echo("❌ Failed to save application")


@template.command()
@click.argument("application_id")
@click.option("--format", default="text", help="Export format (text, json)")
@click.option("--output", "-o", help="Output file path")
def export_application(application_id: str, format: str, output: Optional[str]):
    """Export an application to various formats."""
    manager = TemplateManager()

    # Load application
    application = manager.load_application(application_id)
    if not application:
        click.echo(f"❌ Application '{application_id}' not found")
        return

    # Load template
    template = manager.load_template(application.template_id)
    if not template:
        click.echo(f"❌ Template '{application.template_id}' not found")
        return

    # Export
    export_data = manager.export_application(application, template, format)
    if not export_data:
        click.echo("❌ Failed to export application")
        return

    if output:
        with open(output, "w") as f:
            f.write(export_data)
        click.echo(f"📄 Application exported to: {output}")
    else:
        click.echo(export_data)


@main.group()
def tracking():
    """Manage application tracking."""
    pass


@tracking.command()
@click.option("--organization-id", help="Filter by organization ID")
def list_tracking(organization_id: Optional[str]):
    """List all application tracking records."""
    manager = TrackingManager()
    tracking_records = manager.list_tracking(organization_id)

    if not tracking_records:
        click.echo("📋 No tracking records found")
        return

    click.echo(f"📋 Found {len(tracking_records)} tracking record(s):")
    click.echo()

    for tracking in tracking_records:
        click.echo(f"🆔 {tracking.application_id}")
        click.echo(f"🏢 Organization: {tracking.organization_id}")
        click.echo(f"📊 Status: {tracking.current_status.value}")
        click.echo(f"📈 Completion: {tracking.get_completion_percentage():.1f}%")
        click.echo()


@tracking.command()
def dashboard():
    """Show tracking dashboard with overview."""
    manager = TrackingManager()

    # Get various statistics
    all_tracking = manager.list_tracking()
    overdue_applications = manager.get_overdue_applications()
    due_soon_applications = manager.get_applications_due_soon()

    click.echo("📊 Application Tracking Dashboard")
    click.echo("=" * 40)
    click.echo()

    click.echo(f"📋 Total Applications: {len(all_tracking)}")
    click.echo(f"⚠️  Overdue Applications: {len(overdue_applications)}")
    click.echo(f"📅 Due Soon (7 days): {len(due_soon_applications)}")
    click.echo()

    if overdue_applications:
        click.echo("⚠️  Overdue Applications:")
        for app in overdue_applications:
            days = app.days_until_deadline()
            if days is not None:
                click.echo(f"  - {app.application_id} (overdue by {abs(days)} days)")
        click.echo()

    if due_soon_applications:
        click.echo("📅 Applications Due Soon:")
        for app in due_soon_applications:
            days = app.days_until_deadline()
            if days is not None:
                click.echo(f"  - {app.application_id} (due in {days} days)")
        click.echo()


@main.group()
def report():
    """Generate various reports and analytics."""
    pass


@report.command()
@click.argument("organization_id")
@click.option("--format", default="text", help="Output format (text, json)")
@click.option("--output", "-o", help="Output file path")
def organization(organization_id: str, format: str, output: Optional[str]):
    """Generate a comprehensive report for an organization."""
    generator = ReportGenerator()
    report_data = generator.generate_organization_report(organization_id)

    output_text = generator.export_report(report_data, format, output)

    if not output:
        click.echo(output_text)


@report.command()
@click.option("--status", help="Filter by application status")
@click.option("--format", default="text", help="Output format (text, json)")
@click.option("--output", "-o", help="Output file path")
def status(status: Optional[str], format: str, output: Optional[str]):
    """Generate a report based on application status."""
    from grant_ai.models.application_tracking import ApplicationStatus

    status_filter = None
    if status:
        try:
            status_filter = ApplicationStatus(status)
        except ValueError:
            click.echo(f"❌ Invalid status: {status}")
            click.echo(f"Valid statuses: {', '.join([s.value for s in ApplicationStatus])}")
            return

    generator = ReportGenerator()
    report_data = generator.generate_status_report(status_filter)

    output_text = generator.export_report(report_data, format, output)

    if not output:
        click.echo(output_text)


@report.command()
@click.option("--days", default=30, help="Number of days to include in timeline")
@click.option("--format", default="text", help="Output format (text, json)")
@click.option("--output", "-o", help="Output file path")
def timeline(days: int, format: str, output: Optional[str]):
    """Generate a timeline report of recent events."""
    generator = ReportGenerator()
    report_data = generator.generate_timeline_report(days)

    output_text = generator.export_report(report_data, format, output)

    if not output:
        click.echo(output_text)


@report.command()
@click.option("--format", default="text", help="Output format (text, json)")
@click.option("--output", "-o", help="Output file path")
def performance(format: str, output: Optional[str]):
    """Generate a performance report with key metrics."""
    generator = ReportGenerator()
    report_data = generator.generate_performance_report()

    output_text = generator.export_report(report_data, format, output)

    if not output:
        click.echo(output_text)


@main.command()
def load_sample_data():
    """Load sample data into the system."""
    from ..utils.load_sample_data import load_all_sample_data
    load_all_sample_data()


@main.command()
def load_coda_profile():
    """Load Coda Mountain Academy profile into the database."""
    try:
        from grant_ai.utils.scrape_coda import create_coda_profile

        # Create Coda profile
        coda_profile = create_coda_profile()

        # Save to database (if database is set up)
        click.echo("✅ Coda Mountain Academy profile created:")
        click.echo(f"   Name: {coda_profile.name}")
        click.echo(f"   Location: {coda_profile.location}")
        click.echo(f"   Contact: {coda_profile.contact_email} | {coda_profile.contact_phone}")
        click.echo(f"   Focus Areas: {', '.join([str(area) for area in coda_profile.focus_areas])}")
        click.echo(f"   Programs: {', '.join([str(prog) for prog in coda_profile.program_types])}")
        click.echo(f"   Mission: {coda_profile.description[:100]}...")

        # Save to file
        from grant_ai.utils.scrape_coda import save_coda_profile_to_file
        save_coda_profile_to_file()

        click.echo("\n✅ Coda profile saved to data/profiles/coda_profile.json")
        click.echo("   You can now use this profile in the GUI!")

    except Exception as e:
        click.echo(f"❌ Error loading Coda profile: {e}")
        import traceback
        click.echo(traceback.format_exc())


@main.group()
def gui():
    """Launch GUI applications for Grant-AI."""
    pass


@gui.command()
@click.option('--modern/--classic', default=True,
              help='Launch modern Material Design interface or classic')
def launch(modern):
    """Launch the Grant-AI GUI application."""
    if modern:
        click.echo("🚀 Launching Grant-AI Modern Interface...")
        click.echo("✨ Material Design 3.0 theme loaded")

        try:
            from grant_ai.gui.modern_ui import create_modern_app
            app, _ = create_modern_app()
            click.echo("🎯 Modern interface ready!")
            app.exec_()
        except Exception as e:
            click.echo(f"❌ Failed to launch modern GUI: {e}")
            click.echo("🔄 Falling back to classic interface...")
            modern = False

    if not modern:
        click.echo("🔄 Launching Grant-AI Classic Interface...")
        try:
            # Set environment variables to suppress Qt warnings
            import os
            os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
            os.environ['QT_QPA_PLATFORM'] = 'xcb'

            # Check and update grant database in background
            click.echo("🔄 Checking for grant database updates...")
            try:
                from grant_ai.utils.grant_database_manager import update_grant_database
                update_grant_database(force_update=False)
                click.echo("✅ Grant database is up to date")
            except Exception as e:
                click.echo(f"⚠️  Grant database update failed: {e}")
                click.echo("   GUI will continue without database update")

            # Import and launch classic GUI
            from grant_ai.gui.qt_app import main as gui_main

            click.echo("✅ Environment configured successfully")
            click.echo("🖥️  Starting classic GUI application...")
            click.echo()
            click.echo("💡 Tips:")
            click.echo("   • Go to 'Organization Profile' tab")
            click.echo("   • Select 'Coda Mountain Academy' from dropdown")
            click.echo("   • The profile should load without crashes")
            click.echo("   • Use Ctrl+C in terminal to close the GUI")
            click.echo()

            # Launch the GUI
            gui_main()

        except ImportError as e:
            click.echo(f"❌ Import error: {e}")
            click.echo("💡 Make sure PyQt5 is installed: pip install PyQt5")
            return 1
        except Exception as e:
            click.echo(f"❌ Error launching GUI: {e}")
            import traceback
            click.echo(traceback.format_exc())
            return 1


@gui.command()
def modern():
    """Launch the modern Material Design GUI"""
    click.echo("🚀 Launching Grant-AI Modern Interface...")
    click.echo("✨ Material Design 3.0 theme loaded")

    try:
        from grant_ai.gui.modern_ui import create_modern_app
        app, _ = create_modern_app()
        click.echo("🎯 Modern interface ready!")
        app.exec_()
    except Exception as e:
        click.echo(f"❌ Failed to launch modern GUI: {e}")
        raise click.Abort()


@gui.command()
def classic():
    """Launch the classic PyQt5 GUI"""
    click.echo("🔄 Launching Grant-AI Classic Interface...")

    try:
        # Set environment variables to suppress Qt warnings
        import os
        os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
        os.environ['QT_QPA_PLATFORM'] = 'xcb'

        from grant_ai.gui.qt_app import main as gui_main

        click.echo("📱 Classic interface ready!")
        gui_main()
    except Exception as e:
        click.echo(f"❌ Failed to launch classic GUI: {e}")
        raise click.Abort()

    return 0


@main.group()
def discover():
    """AI-powered grant discovery and research."""
    pass


@discover.command()
@click.argument("profile_file", type=click.Path(exists=True))
@click.option("--country", default="USA", help="Country to search in")
@click.option("--state", default="West Virginia", help="State to search in")
@click.option("--output", "-o", help="Output file path for results")
@click.option("--limit", default=20, help="Maximum number of results to return")
def comprehensive(profile_file: str, country: str, state: str, output: Optional[str], limit: int):
    """Comprehensive grant search using AI agent and location-specific scrapers."""
    try:
        # Load organization profile
        with open(profile_file, "r") as f:
            profile_data = json.load(f)

        from grant_ai.models.organization import OrganizationProfile
        profile = OrganizationProfile(**profile_data)

        click.echo(f"🔍 Comprehensive grant search for {profile.name}...")
        click.echo(f"Location: {state}, {country}")
        click.echo(f"Focus areas: {', '.join([str(fa) for fa in profile.focus_areas])}")
        click.echo()

        all_grants = []

        # AI Agent discovery (always run)
        click.echo("🤖 Using AI Agent for web search...")
        from grant_ai.utils.ai_grant_agent import AIGrantAgent
        agent = AIGrantAgent()
        ai_grants = agent.search_grants_for_profile(profile)
        all_grants.extend(ai_grants)
        click.echo(f"   Found {len(ai_grants)} grants via AI Agent")

        # Location-specific scrapers
        if country == "USA":
            if state == "West Virginia":
                click.echo("🏔️ Searching West Virginia sources...")
                from grant_ai.scrapers.wv_grants import WVGrantScraper
                scraper = WVGrantScraper()
                wv_grants = scraper.scrape_all_sources()
                all_grants.extend(wv_grants)
                click.echo(f"   Found {len(wv_grants)} grants via WV Scraper")
            elif state == "All States":
                click.echo("🏔️ Searching West Virginia sources...")
                from grant_ai.scrapers.wv_grants import WVGrantScraper
                scraper = WVGrantScraper()
                wv_grants = scraper.scrape_all_sources()
                all_grants.extend(wv_grants)
                click.echo(f"   Found {len(wv_grants)} grants via WV Scraper")
                # Could add other state scrapers here in the future

        # Remove duplicates
        seen = set()
        unique_grants = []
        for grant in all_grants:
            key = (grant.title.lower(), grant.funder_name.lower())
            if key not in seen:
                seen.add(key)
                unique_grants.append(grant)

        # Limit results
        unique_grants = unique_grants[:limit]

        click.echo()
        click.echo(f"✅ Comprehensive search found {len(unique_grants)} unique grant opportunities:")
        click.echo()

        for i, grant in enumerate(unique_grants, 1):
            # Determine source icon
            if "WV" in grant.source or "West Virginia" in grant.source:
                source_icon = "🏔️"
            elif grant.source == "AI Web Search":
                source_icon = "🤖"
            elif "Grants.gov" in grant.source:
                source_icon = "🇺🇸"
            else:
                source_icon = "💰"

            click.echo(f"{i}. {source_icon} {grant.title}")
            click.echo(f"   Funder: {grant.funder_name}")
            click.echo(f"   Amount: ${grant.amount_typical:,}")
            click.echo(f"   Source: {grant.source}")
            click.echo(f"   Focus: {', '.join(grant.focus_areas)}")
            click.echo(f"   Eligibility: {', '.join([str(e) for e in grant.eligibility_types])}")
            click.echo(f"   URL: {grant.application_url}")
            click.echo()

        # Save results if output specified
        if output:
            results = [grant.model_dump() for grant in unique_grants]
            with open(output, "w") as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"📄 Results saved to: {output}")

    except Exception as e:
        click.echo(f"❌ Error during comprehensive search: {e}")
        import traceback
        click.echo(traceback.format_exc())


@main.command()
def update_database():
    """Update the grant database with latest grants from federal, state, and foundation sources."""
    try:
        click.echo("🔄 Updating grant database...")
        from grant_ai.utils.grant_database_manager import (
            get_database_stats,
            update_grant_database,
        )

        # Update the database
        update_grant_database(force_update=True)

        # Show updated statistics
        stats = get_database_stats()
        click.echo("\n📊 Updated Database Statistics:")
        click.echo(f"   Total grants: {stats.get('total_grants', 0)}")
        click.echo(f"   Federal grants: {stats.get('federal_grants', 0)}")
        click.echo(f"   State grants: {stats.get('state_grants', 0)}")
        click.echo(f"   Foundation grants: {stats.get('foundation_grants', 0)}")
        click.echo(f"   Last update: {stats.get('last_update', 'Unknown')}")
        click.echo(f"   Next update: {stats.get('next_update', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Error updating database: {e}")
        import traceback
        click.echo(traceback.format_exc())
        return 1

    return 0


@main.command()
def database_stats():
    """Show current grant database statistics."""
    try:
        from grant_ai.utils.grant_database_manager import get_database_stats

        stats = get_database_stats()
        click.echo("📊 Grant Database Statistics:")
        click.echo(f"   Total grants: {stats.get('total_grants', 0)}")
        click.echo(f"   Federal grants: {stats.get('federal_grants', 0)}")
        click.echo(f"   State grants: {stats.get('state_grants', 0)}")
        click.echo(f"   Foundation grants: {stats.get('foundation_grants', 0)}")
        click.echo(f"   Last update: {stats.get('last_update', 'Never')}")
        click.echo(f"   Next update: {stats.get('next_update', 'Unknown')}")

    except Exception as e:
        click.echo(f"❌ Error getting database stats: {e}")
        return 1

    return 0


@main.group()
def writing():
    """AI-powered grant writing assistance."""
    pass


@writing.command()
def assistant():
    """Launch interactive grant writing assistant."""
    assistant = GrantWritingAssistant()
    assistant.interactive_mode()


@writing.command()
@click.argument("text_file", type=click.Path(exists=True))
@click.option("--enhance", is_flag=True, help="Enhance text clarity")
@click.option("--compelling", is_flag=True, help="Make text more compelling")
@click.option("--align", help="Align with funding agency mission")
@click.option("--output", "-o", help="Output file path")
def improve_text(text_file: str, enhance: bool, compelling: bool, align: Optional[str], output: Optional[str]):
    """Improve grant writing text using AI prompts."""
    assistant = GrantWritingAssistant()

    with open(text_file, 'r') as f:
        text = f.read()

    result = None

    if enhance:
        result = assistant.enhance_clarity(text)
        click.echo("Enhanced text:")
        click.echo(result['enhanced_text'])
        click.echo("\nSuggestions:")
        for suggestion in result['suggestions']:
            click.echo(f"  - {suggestion}")

    elif compelling:
        result = assistant.make_compelling(text)
        click.echo("Compelling text:")
        click.echo(result['compelling_text'])
        click.echo("\nSuggestions:")
        for suggestion in result['suggestions']:
            click.echo(f"  - {suggestion}")

    elif align:
        result = assistant.align_with_mission(text, align)
        click.echo("Mission-aligned text:")
        click.echo(result['aligned_text'])
        click.echo("\nSuggestions:")
        for suggestion in result['suggestions']:
            click.echo(f"  - {suggestion}")

    else:
        click.echo("Please specify an improvement type: --enhance, --compelling, or --align")
        return

    if output and result:
        with open(output, 'w') as f:
            json.dump(result, f, indent=2)
        click.echo(f"\nResults saved to: {output}")


@writing.command()
@click.argument("abstract", type=str)
@click.option("--output", "-o", help="Output file path")
def generate_title(abstract: str, output: Optional[str]):
    """Generate compelling grant titles based on abstract."""
    assistant = GrantWritingAssistant()
    titles = assistant.generate_title(abstract)

    click.echo("Title options:")
    for i, title in enumerate(titles, 1):
        click.echo(f"\n{i}. {title['title']}")
        click.echo(f"   Explanation: {title['explanation']}")
        click.echo(f"   Strengths: {', '.join(title['strengths'])}")

    if output:
        with open(output, 'w') as f:
            json.dump(titles, f, indent=2)
        click.echo(f"\nTitles saved to: {output}")


@writing.command()
@click.argument("aims", type=str)
@click.option("--output", "-o", help="Output file path")
def identify_challenges(aims: str, output: Optional[str]):
    """Identify potential challenges and mitigation strategies."""
    assistant = GrantWritingAssistant()
    challenges = assistant.identify_challenges(aims)

    click.echo("Technical challenges:")
    for challenge in challenges['technical_challenges']:
        click.echo(f"  - {challenge}")

    click.echo("\nFeasibility concerns:")
    for concern in challenges['feasibility_concerns']:
        click.echo(f"  - {concern}")

    click.echo("\nMitigation strategies:")
    for strategy in challenges['mitigation_strategies']:
        click.echo(f"  - {strategy}")

    if output:
        with open(output, 'w') as f:
            json.dump(challenges, f, indent=2)
        click.echo(f"\nChallenges saved to: {output}")


@writing.command()
@click.argument("summary", type=str)
@click.option("--duration", default="12 months", help="Project duration")
@click.option("--output", "-o", help="Output file path")
def create_timeline(summary: str, duration: str, output: Optional[str]):
    """Create detailed project timeline."""
    assistant = GrantWritingAssistant()
    timeline = assistant.create_timeline(summary, duration)

    click.echo("Project timeline:")
    for period, activity in timeline['timeline'].items():
        click.echo(f"  {period}: {activity}")

    click.echo("\nMilestones:")
    for milestone in timeline['milestones']:
        click.echo(f"  - {milestone}")

    if output:
        with open(output, 'w') as f:
            json.dump(timeline, f, indent=2)
        click.echo(f"\nTimeline saved to: {output}")


@writing.command()
@click.argument("template_type", type=str)
@click.option("--output", "-o", help="Output file path")
def get_template(template_type: str, output: Optional[str]):
    """Get a writing template for a specific grant section."""
    assistant = GrantWritingAssistant()

    try:
        template = assistant.get_template(template_type)
        click.echo(f"{template_type.upper()} Template:")
        click.echo(template)

        if output:
            with open(output, 'w') as f:
                f.write(template)
            click.echo(f"\nTemplate saved to: {output}")

    except ValueError as e:
        click.echo(f"Error: {e}")
        click.echo("Available templates:")
        for template_name in assistant.templates.keys():
            click.echo(f"  - {template_name}")


@writing.command()
def list_templates():
    """List available writing templates."""
    assistant = GrantWritingAssistant()

    click.echo("Available writing templates:")
    for template_name in assistant.templates.keys():
        click.echo(f"  - {template_name}")


@writing.command()
def list_prompts():
    """List available AI prompts for grant writing."""
    assistant = GrantWritingAssistant()

    click.echo("Available prompt categories:")
    for category, prompts in assistant.prompts.items():
        click.echo(f"\n{category.upper()}:")
        for prompt_name in prompts.keys():
            click.echo(f"  - {prompt_name}")


@main.group()
def scrape():
    """Web scraping tools for organization data."""
    pass


@scrape.command()
@click.argument("website_url")
@click.option("--output", "-o", help="Output file path for scraped data")
def organization(website_url: str, output: Optional[str]):
    """Scrape organization information from a website."""
    scraper = OrganizationScraper()

    click.echo(f"Scraping organization data from: {website_url}")

    try:
        scraped_data = scraper.scrape_organization(website_url)

        if not scraped_data:
            click.echo("❌ Failed to scrape organization data")
            return

        click.echo("✅ Successfully scraped organization data:")
        click.echo()

        for key, value in scraped_data.items():
            if value:
                if isinstance(value, list):
                    click.echo(f"{key}: {', '.join(value)}")
                else:
                    click.echo(f"{key}: {value}")

        if output:
            with open(output, 'w') as f:
                json.dump(scraped_data, f, indent=2)
            click.echo(f"\nData saved to: {output}")

    except Exception as e:
        click.echo(f"❌ Error scraping website: {e}")


@scrape.command()
@click.argument("website_url")
@click.option("--output", "-o", help="Output file path for questionnaire response")
def fill_questionnaire(website_url: str, output: Optional[str]):
    """Fill organization questionnaire with data scraped from website."""
    scraper = OrganizationScraper()
    qm = QuestionnaireManager()

    click.echo(f"Scraping and filling questionnaire for: {website_url}")

    try:
        # Get default questionnaire
        questionnaire = qm.get_default_questionnaire()

        # Fill questionnaire with scraped data
        response = scraper.fill_questionnaire_from_website(website_url, questionnaire)

        if not response.responses:
            click.echo("❌ Failed to extract questionnaire data")
            return

        click.echo("✅ Successfully filled questionnaire:")
        click.echo()
        click.echo(f"Completed: {response.completed}")
        click.echo(f"Questions answered: {len(response.responses)}/{len(questionnaire.questions)}")
        click.echo()

        # Show responses
        for question in questionnaire.questions:
            if question.id in response.responses:
                value = response.responses[question.id]
                if isinstance(value, list):
                    click.echo(f"{question.text}: {', '.join(value)}")
                else:
                    click.echo(f"{question.text}: {value}")
            else:
                click.echo(f"{question.text}: [Not found]")

        if output:
            with open(output, 'w') as f:
                json.dump(response.dict(), f, indent=2)
            click.echo(f"\nQuestionnaire response saved to: {output}")

        # Option to create organization profile
        if click.confirm("\nWould you like to create an organization profile from this data?"):
            profile = qm.convert_response_to_profile(response, questionnaire)
            if profile:
                profile_file = f"{profile.name.lower().replace(' ', '_')}_scraped_profile.json"
                with open(profile_file, 'w') as f:
                    json.dump(profile.dict(), f, indent=2, default=str)
                click.echo(f"✅ Organization profile created: {profile_file}")
            else:
                click.echo("❌ Failed to create organization profile")

    except Exception as e:
        click.echo(f"❌ Error filling questionnaire: {e}")


@scrape.command()
@click.argument("website_url")
@click.option("--output", "-o", help="Output file path for organization profile")
def create_profile(website_url: str, output: Optional[str]):
    """Create organization profile directly from scraped website data."""
    scraper = OrganizationScraper()
    qm = QuestionnaireManager()

    click.echo(f"Creating organization profile from: {website_url}")

    try:
        # Get default questionnaire
        questionnaire = qm.get_default_questionnaire()

        # Fill questionnaire with scraped data
        response = scraper.fill_questionnaire_from_website(website_url, questionnaire)

        if not response.responses:
            click.echo("❌ Failed to extract organization data")
            return

        # Convert to organization profile
        profile = qm.convert_response_to_profile(response, questionnaire)

        if not profile:
            click.echo("❌ Failed to create organization profile")
            return

        click.echo("✅ Successfully created organization profile:")
        click.echo()
        click.echo(f"Name: {profile.name}")
        click.echo(f"Description: {profile.description[:100]}...")
        click.echo(f"Location: {profile.location}")
        click.echo(f"Focus Areas: {', '.join(profile.focus_areas)}")
        click.echo(f"Program Types: {', '.join(profile.program_types)}")
        if profile.contact_email:
            click.echo(f"Contact Email: {profile.contact_email}")

        # Save profile
        output_file = output or f"{profile.name.lower().replace(' ', '_')}_profile.json"
        with open(output_file, 'w') as f:
            json.dump(profile.dict(), f, indent=2, default=str)

        click.echo(f"\n✅ Organization profile saved to: {output_file}")

    except Exception as e:
        click.echo(f"❌ Error creating profile: {e}")


@scrape.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--output-dir", "-o", help="Output directory for profiles")
def batch_scrape(input_file: str, output_dir: Optional[str]):
    """Scrape multiple organizations from a list of URLs."""
    scraper = OrganizationScraper()
    qm = QuestionnaireManager()

    # Read URLs from file
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    click.echo(f"Scraping {len(urls)} organizations...")

    output_path = Path(output_dir) if output_dir else Path("scraped_profiles")
    output_path.mkdir(exist_ok=True)

    successful = 0
    failed = 0

    for i, url in enumerate(urls, 1):
        click.echo(f"\n[{i}/{len(urls)}] Scraping: {url}")

        try:
            # Get default questionnaire
            questionnaire = qm.get_default_questionnaire()

            # Fill questionnaire with scraped data
            response = scraper.fill_questionnaire_from_website(url, questionnaire)

            if not response.responses:
                click.echo("  ❌ Failed to extract data")
                failed += 1
                continue

            # Convert to organization profile
            profile = qm.convert_response_to_profile(response, questionnaire)

            if not profile:
                click.echo("  ❌ Failed to create profile")
                failed += 1
                continue

            # Save profile
            profile_file = output_path / f"{profile.name.lower().replace(' ', '_')}_profile.json"
            with open(profile_file, 'w') as f:
                json.dump(profile.dict(), f, indent=2, default=str)

            click.echo(f"  ✅ Created: {profile.name}")
            successful += 1

            # Be respectful with requests
            time.sleep(1)

        except Exception as e:
            click.echo(f"  ❌ Error: {e}")
            failed += 1

    click.echo("\n✅ Batch scraping complete!")
    click.echo(f"Successful: {successful}")
    click.echo(f"Failed: {failed}")
    click.echo(f"Profiles saved to: {output_path}")


@main.group()
def past_grants():
    """Commands for fetching and displaying past grants."""
    pass


@past_grants.command()
@click.argument("org_name")
@click.option("--ein", help="Organization EIN (optional, for more precise search)")
@click.option("--limit", default=20, help="Max number of grants to fetch")
def fetch(org_name, ein, limit):
    """Fetch and display past grants for an organization from USASpending.gov."""
    scraper = USASpendingScraper()
    click.echo(f"Fetching past grants for: {org_name} (EIN: {ein or 'N/A'})")
    try:
        grants = scraper.fetch_awarded_grants(org_name=org_name, ein=ein, limit=limit)
        if not grants:
            click.echo("No past grants found.")
            return
        click.echo(f"Found {len(grants)} past grants:\n")
        for g in grants:
            click.echo(f"- {g.year}: {g.name} | {g.funder} | ${g.amount:,.2f} | Status: {g.status}")
            if g.url:
                click.echo(f"  Details: {g.url}")
            if g.next_estimated_open:
                click.echo(f"  Next Estimated Open: {g.next_estimated_open}")
            click.echo("")
    except Exception as e:
        click.echo(f"Error fetching past grants: {e}")


@main.group()
def foundations():
    """Manage foundation and donor database."""
    pass


@foundations.command()
def setup():
    """Set up and populate the foundation database."""

    from ..core.db import init_db
    from ..models.foundation import (
        ApplicationProcess,
        Foundation,
        FoundationType,
        GeographicScope,
    )
    from ..services.foundation_service import foundation_service

    click.echo("Setting up foundation database...")

    # Initialize database tables
    init_db()
    click.echo("✅ Database tables created")

    # Foundation data
    foundations_data = [
        {
            "name": "Claude Worthington Benedum Foundation",
            "website": "https://benedum.org/",
            "contact_email": "info@benedum.org",
            "contact_phone": "(412) 288-0360",
            "foundation_type": FoundationType.PRIVATE,
            "focus_areas": ["education", "economic development",
                           "community development"],
            "geographic_scope": GeographicScope.REGIONAL,
            "geographic_focus": ["west virginia", "southwestern pennsylvania"],
            "grant_range_min": 10000,
            "grant_range_max": 500000,
            "application_process": ApplicationProcess.LETTER_OF_INQUIRY,
            "key_programs": ["Education Excellence", "Economic Development",
                           "Community Development"],
            "integration_notes": "Ideal for CODA-type organizations in WV/PA"
        },
        {
            "name": "United Way of Central West Virginia",
            "website": "https://www.unitedwaycwv.org/",
            "contact_email": "info@unitedwaycwv.org",
            "contact_phone": "(304) 340-3557",
            "foundation_type": FoundationType.COMMUNITY,
            "focus_areas": ["education", "health", "financial stability"],
            "geographic_scope": GeographicScope.REGIONAL,
            "geographic_focus": ["central west virginia"],
            "grant_range_min": 1000,
            "grant_range_max": 25000,
            "application_process": ApplicationProcess.SPECIFIC_DEADLINES,
            "key_programs": ["Community Impact", "Education", "Health"],
            "integration_notes": "Great for social service programs"
        },
        {
            "name": "National Science Foundation",
            "website": "https://www.nsf.gov/",
            "foundation_type": FoundationType.GOVERNMENT,
            "focus_areas": ["STEM education", "research", "innovation"],
            "geographic_scope": GeographicScope.NATIONAL,
            "geographic_focus": ["united states"],
            "grant_range_min": 50000,
            "grant_range_max": 5000000,
            "application_process": ApplicationProcess.ONLINE_APPLICATION,
            "key_programs": ["Education and Human Resources",
                           "Computer and Information Science"],
            "integration_notes": "Perfect for STEM/robotics programs"
        }
    ]

    added_count = 0
    for foundation_data in foundations_data:
        try:
            foundation = Foundation(**foundation_data)
            foundation_id = foundation_service.add_foundation(foundation)
            click.echo(f"✅ Added: {foundation.name}")
            added_count += 1
        except Exception as e:
            click.echo(f"❌ Error adding {foundation_data['name']}: {e}")

    click.echo(f"\n📊 Added {added_count}/{len(foundations_data)} foundations to database")


@foundations.command()
@click.argument("organization_name")
def match(organization_name):
    """Find foundations that match an organization profile."""
    from ..models.organization import OrganizationProfile
    from ..services.foundation_service import foundation_service

    # Load organization profile
    profiles_dir = Path("data/profiles")
    profile_file = profiles_dir / f"{organization_name.lower().replace(' ', '_')}.json"

    if not profile_file.exists():
        click.echo(f"❌ Organization profile not found: {profile_file}")
        return

    try:
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)

        org_profile = OrganizationProfile(**profile_data)
        matches = foundation_service.match_foundations_for_organization(org_profile)

        click.echo(f"\n🎯 Found {len(matches)} matching foundations for {org_profile.name}:")
        click.echo("=" * 60)

        for i, foundation in enumerate(matches[:10], 1):  # Top 10
            score = getattr(foundation, 'match_score', 0)
            click.echo(f"\n{i}. {foundation.name} (Match Score: {score:.2f})")
            click.echo(f"   Focus Areas: {', '.join(foundation.focus_areas[:3])}")
            click.echo(f"   Grant Range: ${foundation.grant_range_min:,} - ${foundation.grant_range_max:,}")
            click.echo(f"   Geographic: {', '.join(foundation.geographic_focus)}")
            if foundation.contact_email:
                click.echo(f"   Contact: {foundation.contact_email}")
            if foundation.integration_notes:
                click.echo(f"   Notes: {foundation.integration_notes}")

    except Exception as e:
        click.echo(f"❌ Error matching foundations: {e}")


@foundations.command()
def list():
    """List all foundations in the database."""
    from ..core.db import init_db
    from ..services.foundation_service import foundation_service

    # Initialize database tables
    init_db()

    try:
        foundations = foundation_service.get_all_foundations()

        if not foundations:
            click.echo("📋 No foundations found in database")
            msg = "💡 Use 'foundations setup' to populate with defaults"
            click.echo(msg)
            return

        click.echo(f"📋 Found {len(foundations)} foundation(s) in database:")
        click.echo("=" * 60)

        for i, foundation in enumerate(foundations, 1):
            click.echo(f"\n{i}. {foundation.name}")
            click.echo(f"   Type: {foundation.foundation_type}")
            click.echo(f"   Focus: {', '.join(foundation.focus_areas[:3])}")
            if foundation.grant_range_min and foundation.grant_range_max:
                min_amt = foundation.grant_range_min
                max_amt = foundation.grant_range_max
                click.echo(f"   Grant Range: ${min_amt:,} - ${max_amt:,}")
            click.echo(f"   Geographic: {foundation.geographic_scope}")
            if foundation.contact_email:
                click.echo(f"   Contact: {foundation.contact_email}")

    except Exception as e:
        click.echo(f"❌ Error listing foundations: {e}")


@foundations.command()
@click.argument("query")
def search(query):
    """Search foundations by name, focus area, or description."""
    from ..services.foundation_service import foundation_service

    try:
        foundations = foundation_service.search_foundations(query)

        if not foundations:
            click.echo(f"🔍 No foundations found matching: {query}")
            return

        click.echo(f"🔍 Found {len(foundations)} foundation(s) matching '{query}':")
        click.echo("=" * 60)

        for i, foundation in enumerate(foundations, 1):
            click.echo(f"\n{i}. {foundation.name}")
            click.echo(f"   Focus: {', '.join(foundation.focus_areas)}")
            if foundation.grant_range_min and foundation.grant_range_max:
                min_amt = foundation.grant_range_min
                max_amt = foundation.grant_range_max
                click.echo(f"   Grant Range: ${min_amt:,} - ${max_amt:,}")
            if foundation.integration_notes:
                click.echo(f"   Notes: {foundation.integration_notes}")

    except Exception as e:
        click.echo(f"❌ Error searching foundations: {e}")


@foundations.command()
@click.option("--min-amount", type=int, required=True, help="Minimum grant amount")
@click.option("--max-amount", type=int, required=True, help="Maximum grant amount")
def range_search(min_amount, max_amount):
    """Find foundations by grant amount range."""
    from ..services.foundation_service import foundation_service

    try:
        foundations = foundation_service.get_foundations_by_grant_range(
            min_amount, max_amount
        )

        if not foundations:
            range_str = f"${min_amount:,} - ${max_amount:,}"
            click.echo(f"💰 No foundations found for range: {range_str}")
            return

        range_str = f"${min_amount:,} - ${max_amount:,}"
        click.echo(f"💰 Found {len(foundations)} foundation(s) in range {range_str}:")
        click.echo("=" * 60)

        for i, foundation in enumerate(foundations, 1):
            min_amt = foundation.grant_range_min
            max_amt = foundation.grant_range_max
            click.echo(f"\n{i}. {foundation.name}")
            click.echo(f"   Grant Range: ${min_amt:,} - ${max_amt:,}")
            click.echo(f"   Focus: {', '.join(foundation.focus_areas[:3])}")
            if foundation.contact_email:
                click.echo(f"   Contact: {foundation.contact_email}")

    except Exception as e:
        click.echo(f"❌ Error searching by range: {e}")


@foundations.command()
def stats():
    """Show foundation database statistics."""
    from ..services.foundation_service import foundation_service

    try:
        stats = foundation_service.get_foundation_statistics()

        click.echo("📊 Foundation Database Statistics")
        click.echo("=" * 40)
        click.echo(f"Total Foundations: {stats['total_foundations']}")
        click.echo(f"Total Historical Grants: {stats['total_historical_grants']}")
        total_amount = stats['total_grant_amount']
        click.echo(f"Total Grant Amount: ${total_amount:,}")

        if stats['average_grant_min']:
            avg_min = stats['average_grant_min']
            click.echo(f"Average Min Grant: ${avg_min:,}")
        if stats['average_grant_max']:
            avg_max = stats['average_grant_max']
            click.echo(f"Average Max Grant: ${avg_max:,}")

        click.echo("\nFoundation Types:")
        for ftype, count in stats['foundation_types'].items():
            click.echo(f"  {ftype}: {count}")

        click.echo("\nGeographic Scopes:")
        for scope, count in stats['geographic_scopes'].items():
            click.echo(f"  {scope}: {count}")

    except Exception as e:
        click.echo(f"❌ Error getting statistics: {e}")


@foundations.command()
@click.argument("foundation_name")
def report(foundation_name):
    """Generate comprehensive report for a foundation."""
    from ..services.foundation_service import foundation_service

    try:
        # Search for foundation by name
        foundations = foundation_service.search_foundations(foundation_name)

        if not foundations:
            click.echo(f"❌ Foundation not found: {foundation_name}")
            return

        if len(foundations) > 1:
            click.echo(f"🔍 Multiple foundations found for '{foundation_name}':")
            for i, f in enumerate(foundations, 1):
                click.echo(f"  {i}. {f.name}")
            return

        foundation = foundations[0]
        report_data = foundation_service.generate_foundation_report(foundation.id)

        if not report_data:
            click.echo(f"❌ Could not generate report for {foundation.name}")
            return

        click.echo(f"📋 Foundation Report: {foundation.name}")
        click.echo("=" * 60)

        # Foundation details
        f_data = report_data['foundation']
        click.echo(f"Website: {f_data.get('website', 'N/A')}")
        click.echo(f"Type: {f_data.get('foundation_type', 'N/A')}")
        click.echo(f"Focus Areas: {', '.join(f_data.get('focus_areas', []))}")

        if f_data.get('grant_range_min') and f_data.get('grant_range_max'):
            min_amt = f_data['grant_range_min']
            max_amt = f_data['grant_range_max']
            click.echo(f"Grant Range: ${min_amt:,} - ${max_amt:,}")

        # Statistics
        stats = report_data['statistics']
        click.echo("\nGrant History:")
        click.echo(f"  Total Grants: {stats['total_grants']}")
        click.echo(f"  Total Amount: ${stats['total_amount']:,}")
        if stats['success_rate']:
            success_pct = stats['success_rate'] * 100
            click.echo(f"  Success Rate: {success_pct:.1f}%")
        if stats['last_contact']:
            click.echo(f"  Last Contact: {stats['last_contact']}")

        # Recent grants
        grants = report_data['historical_grants']
        if grants:
            click.echo(f"\nRecent Grants ({len(grants)}):")
            for grant in grants[:5]:  # Show last 5
                amount = grant['amount']
                click.echo(f"  {grant['date']}: {grant['organization']} - ${amount:,}")
                click.echo(f"    Purpose: {grant['purpose']}")

        # Contact history
        contacts = report_data['contact_history']
        if contacts:
            click.echo(f"\nRecent Contacts ({len(contacts)}):")
            for contact in contacts[:3]:  # Show last 3
                click.echo(f"  {contact['date']}: {contact['type']}")
                click.echo(f"    Purpose: {contact['purpose']}")
                if contact['outcome']:
                    click.echo(f"    Outcome: {contact['outcome']}")

    except Exception as e:
        click.echo(f"❌ Error generating report: {e}")


@foundations.command()
@click.argument("foundation_name")
@click.argument("contact_type")
@click.argument("purpose")
@click.option("--person", help="Person contacted")
@click.option("--outcome", help="Contact outcome")
@click.option("--follow-up", is_flag=True, help="Requires follow-up")
@click.option("--follow-up-date", help="Follow-up date (YYYY-MM-DD)")
@click.option("--notes", help="Additional notes")
def add_contact(foundation_name, contact_type, purpose, person, outcome,
                follow_up, follow_up_date, notes):
    """Add a contact record for a foundation."""
    from datetime import datetime

    from ..models.foundation import FoundationContact
    from ..services.foundation_service import foundation_service

    try:
        # Find foundation
        foundations = foundation_service.search_foundations(foundation_name)

        if not foundations:
            click.echo(f"❌ Foundation not found: {foundation_name}")
            return

        if len(foundations) > 1:
            click.echo(f"🔍 Multiple foundations found for '{foundation_name}':")
            for i, f in enumerate(foundations, 1):
                click.echo(f"  {i}. {f.name}")
            return

        foundation = foundations[0]

        # Parse follow-up date
        followup_date = None
        if follow_up_date:
            followup_date = datetime.strptime(follow_up_date, "%Y-%m-%d").date()

        # Create contact record
        contact = FoundationContact(
            foundation_id=foundation.id,
            contact_date=date.today(),
            contact_type=contact_type,
            contact_person=person,
            purpose=purpose,
            outcome=outcome,
            follow_up_required=follow_up,
            follow_up_date=followup_date,
            notes=notes
        )

        contact_id = foundation_service.add_foundation_contact(contact)
        click.echo(f"✅ Added contact record for {foundation.name}")
        click.echo(f"   Type: {contact_type}")
        click.echo(f"   Purpose: {purpose}")
        if follow_up:
            click.echo(f"   Follow-up required: {follow_up_date or 'TBD'}")

    except Exception as e:
        click.echo(f"❌ Error adding contact: {e}")


@foundations.command()
def deadlines():
    """Show upcoming foundation deadlines and follow-ups."""
    from ..services.foundation_service import foundation_service

    try:
        deadlines = foundation_service.get_upcoming_deadlines()

        if not deadlines:
            click.echo("📅 No upcoming deadlines or follow-ups")
            return

        click.echo(f"📅 Found {len(deadlines)} upcoming deadline(s):")
        click.echo("=" * 50)

        for deadline in deadlines:
            click.echo(f"\n🔔 {deadline['foundation_name']}")
            click.echo(f"   Type: {deadline['type']}")
            click.echo(f"   Date: {deadline['contact_date']}")
            click.echo(f"   Purpose: {deadline['purpose']}")
            if deadline['notes']:
                click.echo(f"   Notes: {deadline['notes']}")

    except Exception as e:
        click.echo(f"❌ Error getting deadlines: {e}")


# Register AI and Analytics command groups
main.add_command(ai)
main.add_command(ai_writing_commands)
main.add_command(analytics)
