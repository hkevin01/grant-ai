"""
Tracking manager for handling application tracking operations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..config import APPLICATIONS_DIR
from ..models.application_tracking import (
    ApplicationReminder,
    ApplicationStatus,
    ApplicationTracking,
)


class TrackingManager:
    """Manager for handling application tracking operations."""

    def __init__(self, applications_dir: Optional[Path] = None):
        """Initialize the tracking manager."""
        self.applications_dir = applications_dir or APPLICATIONS_DIR
        self.applications_dir.mkdir(parents=True, exist_ok=True)

    def create_tracking(
        self, application_id: str, organization_id: str, grant_id: str = "", assigned_to: str = ""
    ) -> ApplicationTracking:
        """Create a new application tracking record."""
        tracking = ApplicationTracking(
            id=f"tracking_{application_id}",
            application_id=application_id,
            organization_id=organization_id,
            grant_id=grant_id,
            assigned_to=assigned_to,
            current_status=ApplicationStatus.DRAFT,
            grant_deadline=None,
            award_date=None,
            funding_amount=None,
        )

        # Add initial event
        tracking.add_event(
            event_type="created",
            status_to=ApplicationStatus.DRAFT,
            description="Application created",
            created_by=assigned_to or "System",
        )

        return tracking

    def load_tracking(self, application_id: str) -> Optional[ApplicationTracking]:
        """Load tracking information for an application."""
        tracking_file = self.applications_dir / f"tracking_{application_id}.json"
        if not tracking_file.exists():
            return None

        try:
            with open(tracking_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ApplicationTracking(**data)
        except Exception as e:
            print(f"Error loading tracking: {e}")
            return None

    def save_tracking(self, tracking: ApplicationTracking) -> bool:
        """Save tracking information to file."""
        try:
            tracking_file = self.applications_dir / f"tracking_{tracking.application_id}.json"
            with open(tracking_file, "w", encoding="utf-8") as f:
                json.dump(tracking.dict(), f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Error saving tracking: {e}")
            return False

    def list_tracking(self, organization_id: Optional[str] = None) -> List[ApplicationTracking]:
        """List all tracking records, optionally filtered by organization."""
        tracking_records = []
        for tracking_file in self.applications_dir.glob("tracking_*.json"):
            application_id = tracking_file.stem.replace("tracking_", "")
            tracking = self.load_tracking(application_id)
            if tracking and (not organization_id or tracking.organization_id == organization_id):
                tracking_records.append(tracking)
        return tracking_records

    def update_status(
        self,
        application_id: str,
        new_status: ApplicationStatus,
        description: str = "",
        created_by: str = "",
    ) -> bool:
        """Update the status of an application."""
        tracking = self.load_tracking(application_id)
        if not tracking:
            return False

        tracking.add_event(
            event_type="status_change",
            status_to=new_status,
            description=description,
            created_by=created_by,
        )

        return self.save_tracking(tracking)

    def add_note(
        self,
        application_id: str,
        title: str,
        content: str,
        created_by: str,
        is_internal: bool = True,
    ) -> bool:
        """Add a note to an application."""
        tracking = self.load_tracking(application_id)
        if not tracking:
            return False

        tracking.add_note(title, content, created_by, is_internal)
        return self.save_tracking(tracking)

    def add_reminder(
        self,
        application_id: str,
        title: str,
        due_date: datetime,
        description: str = "",
        created_by: str = "",
        send_email: bool = True,
        send_notification: bool = True,
    ) -> bool:
        """Add a reminder to an application."""
        tracking = self.load_tracking(application_id)
        if not tracking:
            return False

        tracking.add_reminder(
            title, due_date, description, created_by, send_email, send_notification
        )
        return self.save_tracking(tracking)

    def get_overdue_applications(self) -> List[ApplicationTracking]:
        """Get all overdue applications."""
        all_tracking = self.list_tracking()
        return [t for t in all_tracking if t.is_overdue()]

    def get_applications_by_status(self, status: ApplicationStatus) -> List[ApplicationTracking]:
        """Get all applications with a specific status."""
        all_tracking = self.list_tracking()
        return [t for t in all_tracking if t.current_status == status]

    def get_applications_due_soon(self, days: int = 7) -> List[ApplicationTracking]:
        """Get applications due within the specified number of days."""
        all_tracking = self.list_tracking()
        due_soon = []

        for tracking in all_tracking:
            days_until = tracking.days_until_deadline()
            if days_until is not None and 0 <= days_until <= days:
                due_soon.append(tracking)

        return due_soon

    def get_pending_reminders(self) -> List[ApplicationReminder]:
        """Get all pending reminders across all applications."""
        all_tracking = self.list_tracking()
        all_reminders = []

        for tracking in all_tracking:
            all_reminders.extend(tracking.get_pending_reminders())

        return all_reminders

    def get_overdue_reminders(self) -> List[ApplicationReminder]:
        """Get all overdue reminders across all applications."""
        all_tracking = self.list_tracking()
        all_reminders = []

        for tracking in all_tracking:
            all_reminders.extend(tracking.get_overdue_reminders())

        return all_reminders

    def get_application_summary(self, application_id: str) -> Optional[dict]:
        """Get a summary of an application's tracking information."""
        tracking = self.load_tracking(application_id)
        if not tracking:
            return None

        return {
            "application_id": tracking.application_id,
            "organization_id": tracking.organization_id,
            "grant_id": tracking.grant_id,
            "current_status": tracking.current_status.value,
            "completion_percentage": tracking.get_completion_percentage(),
            "days_until_deadline": tracking.days_until_deadline(),
            "is_overdue": tracking.is_overdue(),
            "total_events": len(tracking.events),
            "total_notes": len(tracking.notes),
            "pending_reminders": len(tracking.get_pending_reminders()),
            "overdue_reminders": len(tracking.get_overdue_reminders()),
            "last_updated": tracking.updated_at.isoformat(),
            "assigned_to": tracking.assigned_to,
        }

    def get_organization_summary(self, organization_id: str) -> dict:
        """Get a summary of all applications for an organization."""
        tracking_records = self.list_tracking(organization_id)

        status_counts = {}
        total_applications = len(tracking_records)
        overdue_count = 0
        due_soon_count = 0

        for tracking in tracking_records:
            status = tracking.current_status.value
            status_counts[status] = status_counts.get(status, 0) + 1

            if tracking.is_overdue():
                overdue_count += 1

            days_until = tracking.days_until_deadline()
            if days_until is not None and 0 <= days_until <= 7:
                due_soon_count += 1

        return {
            "organization_id": organization_id,
            "total_applications": total_applications,
            "status_counts": status_counts,
            "overdue_applications": overdue_count,
            "due_soon_applications": due_soon_count,
            "completion_rate": (
                sum(t.get_completion_percentage() for t in tracking_records) / total_applications
                if total_applications > 0
                else 0
            ),
        }
