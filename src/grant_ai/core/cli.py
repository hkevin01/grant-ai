"""Command line interface for Grant AI."""

import json
from typing import Optional

import click

from grant_ai.analysis.grant_researcher import GrantResearcher
from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType
from grant_ai.utils import load_json_file, save_json_file
from grant_ai.utils.questionnaire_manager import QuestionnaireManager
from grant_ai.utils.reporting import ReportGenerator
from grant_ai.utils.template_manager import TemplateManager
from grant_ai.utils.tracking_manager import TrackingManager


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
        from grant_ai.models.organization import OrganizationProfile
        from grant_ai.utils.scrape_coda import create_coda_profile

        # Create Coda profile
        coda_profile = create_coda_profile()
        
        # Save to database (if database is set up)
        click.echo(f"✅ Coda Mountain Academy profile created:")
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


@main.command()
def gui():
    """Launch the PyQt5 GUI application."""
    try:
        click.echo("🚀 Launching Grant AI GUI...")
        click.echo("📝 Setting up environment...")
        
        # Set environment variables to suppress Qt warnings
        import os
        os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        
        # Check and update grant database in background
        click.echo("🔄 Checking for grant database updates...")
        try:
            from grant_ai.utils.grant_database_manager import update_grant_database
            update_grant_database(force_update=False)  # Only update if needed
            click.echo("✅ Grant database is up to date")
        except Exception as e:
            click.echo(f"⚠️  Grant database update failed: {e}")
            click.echo("   GUI will continue without database update")
        
        # Import and launch GUI
        from grant_ai.gui.qt_app import main as gui_main
        
        click.echo("✅ Environment configured successfully")
        click.echo("🖥️  Starting GUI application...")
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


if __name__ == "__main__":
    main()
