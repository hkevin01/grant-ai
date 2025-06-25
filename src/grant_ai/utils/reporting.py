"""
Reporting system for generating various reports and analytics.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..models.application_tracking import ApplicationStatus
from ..utils.questionnaire_manager import QuestionnaireManager
from ..utils.template_manager import TemplateManager
from ..utils.tracking_manager import TrackingManager


class ReportGenerator:
    """Generator for various reports and analytics."""

    def __init__(self):
        """Initialize the report generator."""
        self.tracking_manager = TrackingManager()
        self.template_manager = TemplateManager()
        self.questionnaire_manager = QuestionnaireManager()

    def generate_organization_report(self, organization_id: str) -> Dict[str, Any]:
        """Generate a comprehensive report for an organization."""
        # Get organization summary
        org_summary = self.tracking_manager.get_organization_summary(organization_id)

        # Get all applications for the organization
        tracking_records = self.tracking_manager.list_tracking(organization_id)

        # Calculate additional metrics
        total_funding_requested = 0
        total_funding_awarded = 0
        success_rate = 0
        avg_completion_time = 0

        completed_applications = []
        for tracking in tracking_records:
            if tracking.funding_amount:
                total_funding_requested += tracking.funding_amount

            if tracking.current_status in [ApplicationStatus.AWARDED, ApplicationStatus.APPROVED]:
                completed_applications.append(tracking)
                if tracking.funding_amount:
                    total_funding_awarded += tracking.funding_amount

        if completed_applications:
            success_rate = len(completed_applications) / len(tracking_records) * 100

        # Calculate average completion time
        completion_times = []
        for tracking in tracking_records:
            if tracking.current_status in [
                ApplicationStatus.AWARDED,
                ApplicationStatus.REJECTED,
                ApplicationStatus.DECLINED,
            ]:
                # Find the first and last events
                if tracking.events:
                    first_event = min(tracking.events, key=lambda e: e.created_at)
                    last_event = max(tracking.events, key=lambda e: e.created_at)
                    completion_time = (last_event.created_at - first_event.created_at).days
                    completion_times.append(completion_time)

        if completion_times:
            avg_completion_time = sum(completion_times) / len(completion_times)

        return {
            "organization_id": organization_id,
            "generated_at": datetime.now().isoformat(),
            "summary": org_summary,
            "metrics": {
                "total_funding_requested": total_funding_requested,
                "total_funding_awarded": total_funding_awarded,
                "success_rate": success_rate,
                "avg_completion_time_days": avg_completion_time,
                "total_completed_applications": len(completed_applications),
            },
            "applications": [
                {
                    "application_id": t.application_id,
                    "grant_id": t.grant_id,
                    "status": t.current_status.value,
                    "completion_percentage": t.get_completion_percentage(),
                    "funding_amount": t.funding_amount,
                    "created_at": t.created_at.isoformat(),
                    "last_updated": t.updated_at.isoformat(),
                    "is_overdue": t.is_overdue(),
                    "days_until_deadline": t.days_until_deadline(),
                }
                for t in tracking_records
            ],
        }

    def generate_status_report(self, status: Optional[ApplicationStatus] = None) -> Dict[str, Any]:
        """Generate a report based on application status."""
        all_tracking = self.tracking_manager.list_tracking()

        if status:
            tracking_records = [t for t in all_tracking if t.current_status == status]
        else:
            tracking_records = all_tracking

        # Group by organization
        org_groups = {}
        for tracking in tracking_records:
            org_id = tracking.organization_id
            if org_id not in org_groups:
                org_groups[org_id] = []
            org_groups[org_id].append(tracking)

        # Calculate metrics
        total_applications = len(tracking_records)
        overdue_count = sum(1 for t in tracking_records if t.is_overdue())
        total_funding = sum(t.funding_amount or 0 for t in tracking_records)

        return {
            "report_type": "status_report",
            "status_filter": status.value if status else "all",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_applications": total_applications,
                "overdue_applications": overdue_count,
                "total_funding_requested": total_funding,
                "organizations_count": len(org_groups),
            },
            "by_organization": {
                org_id: {
                    "applications_count": len(apps),
                    "overdue_count": sum(1 for a in apps if a.is_overdue()),
                    "total_funding": sum(a.funding_amount or 0 for a in apps),
                    "avg_completion": (
                        sum(a.get_completion_percentage() for a in apps) / len(apps) if apps else 0
                    ),
                }
                for org_id, apps in org_groups.items()
            },
            "applications": [
                {
                    "application_id": t.application_id,
                    "organization_id": t.organization_id,
                    "grant_id": t.grant_id,
                    "status": t.current_status.value,
                    "completion_percentage": t.get_completion_percentage(),
                    "funding_amount": t.funding_amount,
                    "is_overdue": t.is_overdue(),
                    "days_until_deadline": t.days_until_deadline(),
                    "created_at": t.created_at.isoformat(),
                }
                for t in tracking_records
            ],
        }

    def generate_timeline_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate a timeline report for the specified number of days."""
        all_tracking = self.tracking_manager.list_tracking()
        cutoff_date = datetime.now() - timedelta(days=days)

        # Filter events within the timeline
        timeline_events = []
        for tracking in all_tracking:
            for event in tracking.events:
                if event.created_at >= cutoff_date:
                    timeline_events.append(
                        {
                            "application_id": tracking.application_id,
                            "organization_id": tracking.organization_id,
                            "event_type": event.event_type,
                            "description": event.description,
                            "status_from": event.status_from,
                            "status_to": event.status_to,
                            "created_at": event.created_at.isoformat(),
                            "created_by": event.created_by,
                        }
                    )

        # Sort by date
        timeline_events.sort(key=lambda e: e["created_at"], reverse=True)

        # Group by date
        events_by_date = {}
        for event in timeline_events:
            date_key = event["created_at"][:10]  # YYYY-MM-DD
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(event)

        return {
            "report_type": "timeline_report",
            "period_days": days,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_events": len(timeline_events),
                "unique_applications": len(set(e["application_id"] for e in timeline_events)),
                "unique_organizations": len(set(e["organization_id"] for e in timeline_events)),
            },
            "events_by_date": events_by_date,
            "all_events": timeline_events,
        }

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report with key metrics."""
        all_tracking = self.tracking_manager.list_tracking()

        # Calculate various metrics
        total_applications = len(all_tracking)
        status_counts = {}
        completion_rates = {}

        for tracking in all_tracking:
            status = tracking.current_status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate completion rates by status
        for status in ApplicationStatus:
            status_apps = [t for t in all_tracking if t.current_status == status]
            if status_apps:
                avg_completion = sum(t.get_completion_percentage() for t in status_apps) / len(
                    status_apps
                )
                completion_rates[status.value] = avg_completion

        # Calculate success rate
        successful_apps = [
            t
            for t in all_tracking
            if t.current_status in [ApplicationStatus.AWARDED, ApplicationStatus.APPROVED]
        ]
        success_rate = (
            len(successful_apps) / total_applications * 100 if total_applications > 0 else 0
        )

        # Calculate average funding
        funding_apps = [t for t in all_tracking if t.funding_amount]
        avg_funding = (
            sum(t.funding_amount or 0 for t in funding_apps) / len(funding_apps)
            if funding_apps
            else 0
        )

        return {
            "report_type": "performance_report",
            "generated_at": datetime.now().isoformat(),
            "metrics": {
                "total_applications": total_applications,
                "success_rate": success_rate,
                "avg_funding_requested": avg_funding,
                "overdue_applications": len([t for t in all_tracking if t.is_overdue()]),
                "due_soon_applications": len(self.tracking_manager.get_applications_due_soon()),
            },
            "status_distribution": status_counts,
            "completion_rates_by_status": completion_rates,
            "top_organizations": self._get_top_organizations(all_tracking),
        }

    def _get_top_organizations(self, tracking_records: List) -> List[Dict[str, Any]]:
        """Get top organizations by application count and success rate."""
        org_stats = {}

        for tracking in tracking_records:
            org_id = tracking.organization_id
            if org_id not in org_stats:
                org_stats[org_id] = {
                    "total_applications": 0,
                    "successful_applications": 0,
                    "total_funding": 0,
                }

            org_stats[org_id]["total_applications"] += 1
            if tracking.current_status in [ApplicationStatus.AWARDED, ApplicationStatus.APPROVED]:
                org_stats[org_id]["successful_applications"] += 1

            if tracking.funding_amount:
                org_stats[org_id]["total_funding"] += tracking.funding_amount

        # Calculate success rates and sort
        for org_id, stats in org_stats.items():
            stats["success_rate"] = (
                (stats["successful_applications"] / stats["total_applications"] * 100)
                if stats["total_applications"] > 0
                else 0
            )

        # Sort by success rate and total applications
        sorted_orgs = sorted(
            org_stats.items(),
            key=lambda x: (x[1]["success_rate"], x[1]["total_applications"]),
            reverse=True,
        )

        return [
            {
                "organization_id": org_id,
                "total_applications": stats["total_applications"],
                "successful_applications": stats["successful_applications"],
                "success_rate": stats["success_rate"],
                "total_funding": stats["total_funding"],
            }
            for org_id, stats in sorted_orgs[:10]  # Top 10
        ]

    def export_report(
        self, report_data: Dict[str, Any], format: str = "json", output_file: Optional[str] = None
    ) -> str:
        """Export a report to various formats."""
        if format.lower() == "json":
            output = json.dumps(report_data, indent=2, default=str)
        elif format.lower() == "text":
            output = self._format_report_as_text(report_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)

        return output

    def _format_report_as_text(self, report_data: Dict[str, Any]) -> str:
        """Format a report as human-readable text."""
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append("GRANT AI REPORT")
        lines.append(f"Generated: {report_data.get('generated_at', 'Unknown')}")
        lines.append(f"Report Type: {report_data.get('report_type', 'Unknown')}")
        lines.append("=" * 60)
        lines.append("")

        # Summary section
        if "summary" in report_data:
            lines.append("SUMMARY:")
            for key, value in report_data["summary"].items():
                if isinstance(value, float):
                    lines.append(f"  {key.replace('_', ' ').title()}: {value:.2f}")
                else:
                    lines.append(f"  {key.replace('_', ' ').title()}: {value}")
            lines.append("")

        # Metrics section
        if "metrics" in report_data:
            lines.append("METRICS:")
            for key, value in report_data["metrics"].items():
                if isinstance(value, float):
                    lines.append(f"  {key.replace('_', ' ').title()}: {value:.2f}")
                else:
                    lines.append(f"  {key.replace('_', ' ').title()}: {value}")
            lines.append("")

        # Applications section
        if "applications" in report_data:
            lines.append("APPLICATIONS:")
            for app in report_data["applications"][:10]:  # Show first 10
                lines.append(f"  {app.get('application_id', 'Unknown')}")
                lines.append(f"    Status: {app.get('status', 'Unknown')}")
                lines.append(f"    Completion: {app.get('completion_percentage', 0):.1f}%")
                if app.get("funding_amount"):
                    lines.append(f"    Funding: ${app.get('funding_amount', 0):,.2f}")
                lines.append("")

        return "\n".join(lines)
