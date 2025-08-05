"""
CLI commands for AI-powered grant writing assistant
"""
import asyncio
import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..config import DATA_DIR
from ..services.ai_grant_writing import ai_writing_assistant

console = Console()

# Constants
STYLE_SUCCESS = "bold green"
STYLE_ERROR = "bold red"
STYLE_INFO = "bold blue"
STYLE_WARNING = "yellow"
PROPOSALS_FILE = "proposals.json"


@click.group(name="ai-writing")
def ai_writing_commands():
    """AI-powered grant writing assistance commands"""
    pass


@ai_writing_commands.command()
@click.option("--title", prompt="Proposal title",
              help="Title of the grant proposal")
@click.option("--grant-id", prompt="Grant ID", help="ID of the target grant")
@click.option("--organization", prompt="Organization",
              help="Organization name")
def create_proposal(title: str, grant_id: str, organization: str):
    """Create a new grant proposal"""
    proposal_id = ai_writing_assistant.create_proposal(
        title, grant_id, organization)

    console.print(f"✅ Created proposal: {proposal_id}", style=STYLE_SUCCESS)
    console.print(f"Title: {title}")
    console.print(f"Grant: {grant_id}")
    console.print(f"Organization: {organization}")

    # Save to file
    proposals_file = DATA_DIR / PROPOSALS_FILE
    ai_writing_assistant.save_proposals(str(proposals_file))


@ai_writing_commands.command()
def list_proposals():
    """List all grant proposals"""
    # Load proposals
    proposals_file = DATA_DIR / "proposals.json"
    ai_writing_assistant.load_proposals(str(proposals_file))

    if not ai_writing_assistant.proposals:
        console.print("No proposals found.", style="yellow")
        return

    table = Table(title="Grant Proposals")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Grant", style="green")
    table.add_column("Organization", style="blue")
    table.add_column("Status", style="yellow")
    table.add_column("Completion", style="red")

    for proposal_id, proposal in ai_writing_assistant.proposals.items():
        status = proposal.get_completion_status()
        completion_pct = f"{status['completion_percentage']:.1f}%"

        table.add_row(
            proposal_id[:20] + "..." if len(proposal_id) > 20 else proposal_id,
            proposal.title,
            proposal.grant_id,
            proposal.organization_id,
            status["status"],
            completion_pct
        )

    console.print(table)


@ai_writing_commands.command()
@click.argument("proposal_id")
@click.option("--section-type",
              type=click.Choice(["specific_aims", "narrative", "budget_narrative"]),
              prompt="Section type",
              help="Type of section to generate")
def generate_section(proposal_id: str, section_type: str):
    """Generate content for a proposal section using AI"""
    # Load proposals
    proposals_file = DATA_DIR / "proposals.json"
    ai_writing_assistant.load_proposals(str(proposals_file))

    if proposal_id not in ai_writing_assistant.proposals:
        console.print(f"❌ Proposal {proposal_id} not found", style="bold red")
        return

    proposal = ai_writing_assistant.proposals[proposal_id]

    # Gather context information
    context = {}
    if section_type == "specific_aims":
        context.update({
            "agency": Prompt.ask("Grant agency"),
            "program": Prompt.ask("Grant program"),
            "focus_area": Prompt.ask("Focus area"),
            "budget": Prompt.ask("Budget amount"),
            "organization_profile": Prompt.ask("Organization description"),
            "project_overview": Prompt.ask("Project overview")
        })
    elif section_type == "narrative":
        context.update({
            "title": proposal.title,
            "agency": Prompt.ask("Grant agency"),
            "focus_area": Prompt.ask("Focus area"),
            "target_audience": Prompt.ask("Target audience"),
            "organization_details": Prompt.ask("Organization details"),
            "project_summary": Prompt.ask("Project summary")
        })
    elif section_type == "budget_narrative":
        context.update({
            "duration": Prompt.ask("Project duration"),
            "total_budget": Prompt.ask("Total budget"),
            "project_type": Prompt.ask("Project type"),
            "budget_categories": Prompt.ask("Budget categories")
        })

    # Generate content
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating content with AI...", total=None)

        try:
            result = asyncio.run(
                ai_writing_assistant.generate_section_content(section_type, context)
            )

            if "error" in result:
                console.print(f"❌ Error: {result['error']}", style="bold red")
                return

            # Display generated content
            console.print("\n" + "="*80)
            console.print(f"Generated {section_type.replace('_', ' ').title()}",
                         style="bold blue")
            console.print("="*80)
            console.print(result["content"])
            console.print("="*80)
            console.print(f"Word count: {result['word_count']}")
            console.print(f"Generated by: {result['ai_provider']}")

            # Ask if user wants to save
            if Confirm.ask("Save this content to the proposal?"):
                from ..services.ai_grant_writing import ProposalSection

                section = ProposalSection(
                    title=section_type.replace('_', ' ').title(),
                    content=result["content"],
                    section_type=section_type
                )

                proposal.add_section(section)
                ai_writing_assistant.save_proposals(str(proposals_file))
                console.print("✅ Content saved to proposal", style="bold green")

        except Exception as e:
            console.print(f"❌ Error generating content: {str(e)}", style="bold red")


@ai_writing_commands.command()
@click.argument("proposal_id")
@click.argument("section_title")
@click.option("--review-type",
              type=click.Choice(["clarity_check", "alignment_analysis", "competitiveness_analysis"]),
              prompt="Review type",
              help="Type of review to perform")
def review_section(proposal_id: str, section_title: str, review_type: str):
    """Review a proposal section using AI"""
    # Load proposals
    proposals_file = DATA_DIR / "proposals.json"
    ai_writing_assistant.load_proposals(str(proposals_file))

    if proposal_id not in ai_writing_assistant.proposals:
        console.print(f"❌ Proposal {proposal_id} not found", style="bold red")
        return

    proposal = ai_writing_assistant.proposals[proposal_id]

    if section_title not in proposal.sections:
        console.print(f"❌ Section '{section_title}' not found", style="bold red")
        return

    section = proposal.sections[section_title]

    if not section.content.strip():
        console.print("❌ Section is empty", style="bold red")
        return

    # Gather review context
    context = {}
    if review_type == "alignment_analysis":
        context.update({
            "funder": Prompt.ask("Funder name"),
            "program": Prompt.ask("Grant program"),
            "priorities": Prompt.ask("Funding priorities")
        })
    elif review_type == "competitiveness_analysis":
        context.update({
            "program": Prompt.ask("Grant program"),
            "competition_level": Prompt.ask("Competition level (high/medium/low)"),
            "success_rate": Prompt.ask("Typical success rate")
        })

    # Perform review
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Reviewing content with AI...", total=None)

        try:
            result = asyncio.run(
                ai_writing_assistant.review_section(section.content, review_type, context)
            )

            if "error" in result:
                console.print(f"❌ Error: {result['error']}", style="bold red")
                return

            # Display review feedback
            panel = Panel(
                result["feedback"],
                title=f"AI Review: {review_type.replace('_', ' ').title()}",
                border_style="blue"
            )
            console.print(panel)

            # Save feedback to section
            section.review_feedback.append({
                "type": review_type,
                "feedback": result["feedback"],
                "timestamp": result["reviewed_at"]
            })

            ai_writing_assistant.save_proposals(str(proposals_file))
            console.print("✅ Review saved to proposal", style="bold green")

        except Exception as e:
            console.print(f"❌ Error reviewing content: {str(e)}", style="bold red")


@ai_writing_commands.command()
@click.argument("proposal_id")
def status(proposal_id: str):
    """Show detailed status of a proposal"""
    # Load proposals
    proposals_file = DATA_DIR / "proposals.json"
    ai_writing_assistant.load_proposals(str(proposals_file))

    status_info = ai_writing_assistant.get_proposal_status(proposal_id)

    if not status_info:
        console.print(f"❌ Proposal {proposal_id} not found", style="bold red")
        return

    # Display proposal info
    console.print(f"\n📄 Proposal: {status_info['proposal_info']['title']}",
                 style="bold blue")
    console.print(f"Grant: {status_info['proposal_info']['grant_id']}")
    console.print(f"Organization: {status_info['proposal_info']['organization_id']}")
    console.print(f"Created: {status_info['proposal_info']['created_at']}")

    # Display completion status
    completion = status_info['completion_status']
    console.print(f"\n📊 Status: {completion['status']}")
    console.print(f"Completion: {completion['completion_percentage']:.1f}%")
    console.print(f"Sections: {completion['completed_sections']}/{completion['total_sections']}")
    console.print(f"Total words: {completion['word_count']}")

    # Display section details
    if status_info['sections']:
        table = Table(title="Section Details")
        table.add_column("Section", style="cyan")
        table.add_column("Words", style="green")
        table.add_column("Limit", style="yellow")
        table.add_column("Status", style="red")
        table.add_column("Reviews", style="blue")

        for section_title, section_info in status_info['sections'].items():
            limit_str = str(section_info['word_limit']) if section_info['word_limit'] else "None"

            table.add_row(
                section_title,
                str(section_info['word_count']),
                limit_str,
                section_info['status'],
                str(section_info['ai_suggestions'])
            )

        console.print(table)


@ai_writing_commands.command()
@click.argument("proposal_id")
@click.argument("output_path")
def export_docx(proposal_id: str, output_path: str):
    """Export proposal to Word document"""
    # Load proposals
    proposals_file = DATA_DIR / "proposals.json"
    ai_writing_assistant.load_proposals(str(proposals_file))

    if proposal_id not in ai_writing_assistant.proposals:
        console.print(f"❌ Proposal {proposal_id} not found", style="bold red")
        return

    success = ai_writing_assistant.export_proposal_to_docx(proposal_id, output_path)

    if success:
        console.print(f"✅ Proposal exported to {output_path}", style="bold green")
    else:
        console.print("❌ Export failed", style="bold red")


@ai_writing_commands.command()
@click.argument("file_path")
def import_docx(file_path: str):
    """Import proposal from Word document"""
    if not Path(file_path).exists():
        console.print(f"❌ File {file_path} not found", style="bold red")
        return

    proposal_id = ai_writing_assistant.import_proposal_from_docx(file_path)

    if proposal_id:
        console.print(f"✅ Proposal imported as {proposal_id}", style="bold green")

        # Save to file
        proposals_file = DATA_DIR / "proposals.json"
        ai_writing_assistant.save_proposals(str(proposals_file))
    else:
        console.print("❌ Import failed", style="bold red")


@ai_writing_commands.command()
@click.argument("proposal_id")
@click.argument("note", required=False)
def add_note(proposal_id: str, note: Optional[str] = None):
    """Add a collaboration note to a proposal"""
    # Load proposals
    proposals_file = DATA_DIR / "proposals.json"
    ai_writing_assistant.load_proposals(str(proposals_file))

    if proposal_id not in ai_writing_assistant.proposals:
        console.print(f"❌ Proposal {proposal_id} not found", style="bold red")
        return

    if not note:
        note = Prompt.ask("Enter note")

    author = os.getenv("USER", "Unknown")
    ai_writing_assistant.add_collaboration_note(proposal_id, author, note)

    # Save to file
    ai_writing_assistant.save_proposals(str(proposals_file))

    console.print("✅ Note added to proposal", style="bold green")


@ai_writing_commands.command()
def setup():
    """Setup AI writing assistant environment"""
    console.print("🤖 AI Grant Writing Assistant Setup", style="bold blue")

    # Check for API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))

    if not has_openai and not has_anthropic:
        console.print("⚠️  No AI API keys found", style="yellow")
        console.print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        console.print("Fallback templates will be used instead")
    else:
        if has_openai:
            console.print("✅ OpenAI API key found", style="green")
        if has_anthropic:
            console.print("✅ Anthropic API key found", style="green")

    # Create data directory
    DATA_DIR.mkdir(exist_ok=True)

    # Check for optional dependencies
    try:
        import docx
        console.print("✅ python-docx available for Word export", style="green")
    except ImportError:
        console.print("⚠️  python-docx not available - install for Word export", style="yellow")

    console.print("\n🚀 AI Writing Assistant ready to use!", style="bold green")
    console.print("Use 'grant-ai ai-writing --help' for available commands")


if __name__ == "__main__":
    ai_writing_commands()
