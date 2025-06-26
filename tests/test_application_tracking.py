"""
Tests for application tracking functionality.
"""
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from grant_ai.models.application_tracking import ApplicationStatus
from grant_ai.utils.tracking_manager import TrackingManager


@pytest.fixture
def temp_tracking_manager():
    """Create a tracking manager with temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield TrackingManager(applications_dir=Path(temp_dir))


def test_create_tracking(temp_tracking_manager):
    """Test creating a new application tracking record."""
    manager = temp_tracking_manager
    
    tracking = manager.create_tracking(
        application_id="APP_001",
        organization_id="CODA",
        grant_id="GRANT_123",
        assigned_to="Test User"
    )
    
    assert tracking.application_id == "APP_001"
    assert tracking.organization_id == "CODA"
    assert tracking.grant_id == "GRANT_123"
    assert tracking.assigned_to == "Test User"
    assert tracking.current_status == ApplicationStatus.DRAFT
    assert len(tracking.events) == 1
    assert tracking.events[0].event_type == "created"


def test_save_and_load_tracking(temp_tracking_manager):
    """Test saving and loading tracking records."""
    manager = temp_tracking_manager
    
    # Create and save tracking
    tracking = manager.create_tracking(
        application_id="APP_001",
        organization_id="CODA"
    )
    
    success = manager.save_tracking(tracking)
    assert success is True
    
    # Load tracking
    loaded_tracking = manager.load_tracking("APP_001")
    assert loaded_tracking is not None
    assert loaded_tracking.application_id == "APP_001"
    assert loaded_tracking.organization_id == "CODA"
    assert loaded_tracking.current_status == ApplicationStatus.DRAFT


def test_update_status(temp_tracking_manager):
    """Test updating application status."""
    manager = temp_tracking_manager
    
    # Create and save tracking
    tracking = manager.create_tracking(
        application_id="APP_001",
        organization_id="CODA"
    )
    manager.save_tracking(tracking)
    
    # Update status
    success = manager.update_status(
        application_id="APP_001",
        new_status=ApplicationStatus.SUBMITTED,
        description="Application submitted for review",
        created_by="Test User"
    )
    
    assert success is True
    
    # Verify status update
    updated_tracking = manager.load_tracking("APP_001")
    assert updated_tracking.current_status == ApplicationStatus.SUBMITTED
    assert len(updated_tracking.events) == 2
    
    # Check the status change event
    status_event = updated_tracking.events[-1]
    assert status_event.event_type == "status_change"
    assert status_event.status_to == ApplicationStatus.SUBMITTED.value
    assert status_event.description == "Application submitted for review"


def test_add_note(temp_tracking_manager):
    """Test adding notes to applications."""
    manager = temp_tracking_manager
    
    # Create and save tracking
    tracking = manager.create_tracking(
        application_id="APP_001",
        organization_id="CODA"
    )
    manager.save_tracking(tracking)
    
    # Add note
    success = manager.add_note(
        application_id="APP_001",
        title="Review Notes",
        content="Application looks promising, needs budget review.",
        created_by="Reviewer",
        is_internal=True
    )
    
    assert success is True
    
    # Verify note addition
    updated_tracking = manager.load_tracking("APP_001")
    assert len(updated_tracking.notes) == 1
    
    note = updated_tracking.notes[0]
    assert note.title == "Review Notes"
    assert note.content == "Application looks promising, needs budget review."
    assert note.created_by == "Reviewer"
    assert note.is_internal is True


def test_add_reminder(temp_tracking_manager):
    """Test adding reminders to applications."""
    manager = temp_tracking_manager
    
    # Create and save tracking
    tracking = manager.create_tracking(
        application_id="APP_001",
        organization_id="CODA"
    )
    manager.save_tracking(tracking)
    
    # Add reminder
    due_date = datetime.now() + timedelta(days=7)
    success = manager.add_reminder(
        application_id="APP_001",
        title="Follow up with reviewer",
        due_date=due_date,
        description="Check on application status",
        created_by="User",
        send_email=True,
        send_notification=True
    )
    
    assert success is True
    
    # Verify reminder addition
    updated_tracking = manager.load_tracking("APP_001")
    assert len(updated_tracking.reminders) == 1
    
    reminder = updated_tracking.reminders[0]
    assert reminder.title == "Follow up with reviewer"
    assert reminder.description == "Check on application status"
    assert reminder.created_by == "User"
    assert reminder.send_email is True
    assert reminder.send_notification is True


def test_list_tracking(temp_tracking_manager):
    """Test listing all tracking records."""
    manager = temp_tracking_manager
    
    # Create multiple tracking records
    for i in range(3):
        tracking = manager.create_tracking(
            application_id=f"APP_00{i+1}",
            organization_id="CODA" if i % 2 == 0 else "NRG"
        )
        manager.save_tracking(tracking)
    
    # List all tracking records
    all_tracking = manager.list_tracking()
    assert len(all_tracking) == 3
    
    # List tracking records for specific organization
    coda_tracking = manager.list_tracking(organization_id="CODA")
    assert len(coda_tracking) == 2  # APP_001 and APP_003
    
    nrg_tracking = manager.list_tracking(organization_id="NRG")
    assert len(nrg_tracking) == 1  # APP_002


def test_get_applications_by_status(temp_tracking_manager):
    """Test filtering applications by status."""
    manager = temp_tracking_manager
    
    # Create applications with different statuses
    for i in range(3):
        tracking = manager.create_tracking(
            application_id=f"APP_00{i+1}",
            organization_id="CODA"
        )
        manager.save_tracking(tracking)
        
        if i == 1:
            manager.update_status(
                application_id=f"APP_00{i+1}",
                new_status=ApplicationStatus.SUBMITTED,
                created_by="User"
            )
    
    # Test filtering
    draft_apps = manager.get_applications_by_status(ApplicationStatus.DRAFT)
    assert len(draft_apps) == 2
    
    submitted_apps = manager.get_applications_by_status(ApplicationStatus.SUBMITTED)
    assert len(submitted_apps) == 1


def test_get_application_summary(temp_tracking_manager):
    """Test getting application summary."""
    manager = temp_tracking_manager
    
    # Create and enhance tracking
    tracking = manager.create_tracking(
        application_id="APP_001",
        organization_id="CODA",
        grant_id="GRANT_123",
        assigned_to="Test User"
    )
    manager.save_tracking(tracking)
    
    # Add some activity
    manager.update_status(
        application_id="APP_001",
        new_status=ApplicationStatus.SUBMITTED,
        created_by="User"
    )
    
    manager.add_note(
        application_id="APP_001",
        title="Test Note",
        content="Test content",
        created_by="User"
    )
    
    # Get summary
    summary = manager.get_application_summary("APP_001")
    
    assert summary is not None
    assert summary["application_id"] == "APP_001"
    assert summary["organization_id"] == "CODA"
    assert summary["grant_id"] == "GRANT_123"
    assert summary["current_status"] == "submitted"
    assert summary["total_events"] == 2
    assert summary["total_notes"] == 1
    assert summary["assigned_to"] == "Test User"


def test_get_organization_summary(temp_tracking_manager):
    """Test getting organization summary."""
    manager = temp_tracking_manager
    
    # Create multiple applications for CODA
    for i in range(3):
        tracking = manager.create_tracking(
            application_id=f"APP_00{i+1}",
            organization_id="CODA"
        )
        manager.save_tracking(tracking)
        
        # Vary the statuses
        if i == 1:
            manager.update_status(
                application_id=f"APP_00{i+1}",
                new_status=ApplicationStatus.SUBMITTED,
                created_by="User"
            )
        elif i == 2:
            manager.update_status(
                application_id=f"APP_00{i+1}",
                new_status=ApplicationStatus.APPROVED,
                created_by="User"
            )
    
    # Get organization summary
    summary = manager.get_organization_summary("CODA")
    
    assert summary["organization_id"] == "CODA"
    assert summary["total_applications"] == 3
    assert summary["status_counts"]["draft"] == 1
    assert summary["status_counts"]["submitted"] == 1
    assert summary["status_counts"]["approved"] == 1


def test_nonexistent_application(temp_tracking_manager):
    """Test operations on nonexistent applications."""
    manager = temp_tracking_manager
    
    # Try to load nonexistent application
    tracking = manager.load_tracking("NONEXISTENT")
    assert tracking is None
    
    # Try to update status of nonexistent application
    success = manager.update_status(
        application_id="NONEXISTENT",
        new_status=ApplicationStatus.SUBMITTED,
        created_by="User"
    )
    assert success is False
    
    # Try to add note to nonexistent application
    success = manager.add_note(
        application_id="NONEXISTENT",
        title="Test",
        content="Test",
        created_by="User"
    )
    assert success is False


if __name__ == "__main__":
    pytest.main([__file__])
