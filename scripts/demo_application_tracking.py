#!/usr/bin/env python3
"""
Demonstration script for Application Tracking functionality.

This script showcases the comprehensive application tracking system
including creating applications, updating statuses, adding notes,
and viewing analytics.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from grant_ai.models.application_tracking import ApplicationStatus
from grant_ai.utils.tracking_manager import TrackingManager


def main():
    """Run the application tracking demonstration."""
    print("🚀 Grant AI Application Tracking System Demo")
    print("=" * 50)
    
    # Initialize tracking manager
    manager = TrackingManager()
    
    # Create sample applications
    print("\n📝 Creating Sample Applications...")
    
    applications = [
        {
            "id": "CODA_ARTS_2025",
            "org": "CODA",
            "grant": "NEA_ARTS_EDUCATION_2025",
            "assigned": "Arts Director"
        },
        {
            "id": "CODA_STEM_2025",
            "org": "CODA",
            "grant": "NSF_STEM_YOUTH_2025",
            "assigned": "STEM Coordinator"
        },
        {
            "id": "NRG_HOUSING_2025",
            "org": "NRG_Development",
            "grant": "HUD_AFFORDABLE_HOUSING_2025",
            "assigned": "Housing Manager"
        }
    ]
    
    for app_data in applications:
        tracking = manager.create_tracking(
            application_id=app_data["id"],
            organization_id=app_data["org"],
            grant_id=app_data["grant"],
            assigned_to=app_data["assigned"]
        )
        
        # Set deadlines and funding amounts
        tracking.grant_deadline = datetime.now() + timedelta(
            days=30 + hash(app_data["id"]) % 60
        )
        tracking.funding_amount = 25000 + (hash(app_data["id"]) % 75000)
        
        manager.save_tracking(tracking)
        print(f"  ✅ Created: {app_data['id']}")
    
    # Simulate application progression
    print("\n⚙️ Simulating Application Progression...")
    
    # Move CODA Arts to submitted
    manager.update_status(
        "CODA_ARTS_2025",
        ApplicationStatus.SUBMITTED,
        "Application submitted with complete portfolio",
        "Arts Director"
    )
    
    # Add progress note
    manager.add_note(
        "CODA_ARTS_2025",
        "Portfolio Review",
        "Received positive feedback on student artwork samples. "
        "Reviewers particularly impressed with robotics art integration.",
        "Arts Director"
    )
    
    # Move CODA STEM to under review
    manager.update_status(
        "CODA_STEM_2025",
        ApplicationStatus.IN_PROGRESS,
        "Working on final budget details",
        "STEM Coordinator"
    )
    
    manager.update_status(
        "CODA_STEM_2025",
        ApplicationStatus.SUBMITTED,
        "Submitted with detailed STEM curriculum plan",
        "STEM Coordinator"
    )
    
    manager.update_status(
        "CODA_STEM_2025",
        ApplicationStatus.UNDER_REVIEW,
        "NSF has begun technical review process",
        "STEM Coordinator"
    )
    
    # Add reminder
    manager.add_reminder(
        "CODA_STEM_2025",
        "Follow up with Program Officer",
        datetime.now() + timedelta(days=7),
        "Check on review timeline and any additional requirements",
        "STEM Coordinator"
    )
    
    # Move NRG Housing to approved
    manager.update_status(
        "NRG_HOUSING_2025",
        ApplicationStatus.SUBMITTED,
        "Complete housing development proposal submitted",
        "Housing Manager"
    )
    
    manager.update_status(
        "NRG_HOUSING_2025",
        ApplicationStatus.APPROVED,
        "Approved for Phase 1 funding!",
        "Housing Manager"
    )
    
    print("  ✅ Application progressions complete")
    
    # Display current status
    print("\n📊 Current Application Status")
    print("-" * 40)
    
    all_apps = manager.list_tracking()
    
    for app in all_apps:
        status_emoji = {
            "draft": "📝",
            "in_progress": "⚙️",
            "submitted": "📤",
            "under_review": "👀",
            "approved": "✅",
            "rejected": "❌",
            "awarded": "🏆"
        }.get(app.current_status.value, "📄")
        
        days_left = ""
        if hasattr(app, 'days_until_deadline'):
            days_until = app.days_until_deadline()
            if days_until is not None:
                if days_until < 0:
                    days_left = f" (⚠️ {abs(days_until)} days overdue)"
                elif days_until <= 7:
                    days_left = f" (⏰ {days_until} days left)"
                else:
                    days_left = f" ({days_until} days left)"
        
        funding_text = ""
        if hasattr(app, 'funding_amount') and app.funding_amount:
            funding_text = f" - ${app.funding_amount:,.0f}"
        
        print(f"{status_emoji} {app.application_id}")
        status_text = app.current_status.value.replace('_', ' ').title()
        print(f"   Status: {status_text}{days_left}")
        print(f"   Org: {app.organization_id}{funding_text}")
        print(f"   Events: {len(app.events)} | Notes: {len(app.notes)} | "
              f"Reminders: {len(app.reminders)}")
        
        if app.assigned_to:
            print(f"   Assigned: {app.assigned_to}")
        print()
    
    # Show organization summaries
    print("\n📈 Organization Summaries")
    print("-" * 30)
    
    for org_id in ["CODA", "NRG_Development"]:
        summary = manager.get_organization_summary(org_id)
        print(f"\n🏢 {org_id}")
        print(f"   Total Applications: {summary['total_applications']}")
        print("   Status Breakdown:")
        for status, count in summary['status_counts'].items():
            print(f"     - {status.replace('_', ' ').title()}: {count}")
        
        if summary['overdue_applications'] > 0:
            print(f"   ⚠️ Overdue: {summary['overdue_applications']}")
        if summary['due_soon_applications'] > 0:
            print(f"   ⏰ Due Soon: {summary['due_soon_applications']}")
    
    # Show pending reminders
    pending_reminders = manager.get_pending_reminders()
    if pending_reminders:
        print("\n🔔 Pending Reminders")
        print("-" * 20)
        for reminder in pending_reminders:
            due_date_str = reminder.due_date.strftime('%Y-%m-%d')
            print(f"   📅 {reminder.title} (Due: {due_date_str})")
            print(f"      App: {reminder.application_id}")
            if reminder.description:
                print(f"      Note: {reminder.description}")
    
    print("\n🎉 Demo Complete!")
    print("\nThe application tracking system provides:")
    print("✅ Complete application lifecycle management")
    print("✅ Status tracking with event timeline")
    print("✅ Note and reminder system")
    print("✅ Organization-level analytics")
    print("✅ Deadline monitoring and alerts")
    print("✅ PyQt GUI integration")
    
    print(f"\n📁 Applications stored in: {manager.applications_dir}")
    print("💡 Use the PyQt GUI to interact with these applications!")


if __name__ == "__main__":
    main()
