"""
Unit tests for TrackingManager.
"""
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from grant_ai.models.application_tracking import (
    ApplicationReminder,
    ApplicationStatus,
    ApplicationTracking,
)
from grant_ai.utils.tracking_manager import TrackingManager


class TestTrackingManager:
    """Test cases for TrackingManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create a TrackingManager instance."""
        return TrackingManager(applications_dir=temp_dir)
    
    @pytest.fixture
    def sample_tracking(self):
        """Create a sample application tracking for testing."""
        tracking = ApplicationTracking(
            id="test_tracking",
            application_id="test_app",
            organization_id="test_org",
            grant_id="test_grant",
            current_status=ApplicationStatus.DRAFT,
            assigned_to="test_user",
            grant_deadline=datetime.now() + timedelta(days=30),
            award_date=datetime.now() + timedelta(days=60),
            funding_amount=50000,
        )
        
        # Add initial event
        tracking.add_event(
            event_type="created",
            status_to=ApplicationStatus.DRAFT,
            description="Application created",
            created_by="test_user"
        )
        
        return tracking
    
    def test_create_tracking(self, manager):
        """Test creating a new application tracking."""
        tracking = manager.create_tracking(
            application_id="test_app",
            organization_id="test_org",
            grant_id="test_grant",
            assigned_to="test_user"
        )
        
        assert tracking.application_id == "test_app"
        assert tracking.organization_id == "test_org"
        assert tracking.grant_id == "test_grant"
        assert tracking.current_status == ApplicationStatus.DRAFT
        assert len(tracking.events) == 1
        assert tracking.events[0].event_type == "created"
    
    def test_save_and_load_tracking(self, manager, sample_tracking):
        """Test saving and loading tracking."""
        # Save tracking
        success = manager.save_tracking(sample_tracking)
        assert success is True
        
        # Load tracking
        loaded = manager.load_tracking(sample_tracking.application_id)
        assert loaded is not None
        assert loaded.id == sample_tracking.id
        assert loaded.application_id == sample_tracking.application_id
        assert loaded.current_status == sample_tracking.current_status
        assert len(loaded.events) == len(sample_tracking.events)
    
    def test_load_nonexistent_tracking(self, manager):
        """Test loading tracking that doesn't exist."""
        loaded = manager.load_tracking("nonexistent")
        assert loaded is None
    
    def test_list_tracking(self, manager, sample_tracking):
        """Test listing tracking entries."""
        # Initially no tracking
        tracking_list = manager.list_tracking()
        assert len(tracking_list) == 0
        
        # Save tracking
        manager.save_tracking(sample_tracking)
        
        # Now should have one tracking
        tracking_list = manager.list_tracking()
        assert len(tracking_list) == 1
        assert tracking_list[0].id == sample_tracking.id
        
        # Test filtering by organization
        tracking_list = manager.list_tracking("test_org")
        assert len(tracking_list) == 1
        
        tracking_list = manager.list_tracking("other_org")
        assert len(tracking_list) == 0
    
    def test_update_status(self, manager, sample_tracking):
        """Test updating tracking status."""
        # Save tracking first
        manager.save_tracking(sample_tracking)
        
        # Update status
        success = manager.update_status(
            application_id=sample_tracking.application_id,
            new_status=ApplicationStatus.SUBMITTED,
            description="Application submitted",
            created_by="test_user"
        )
        assert success is True
        
        # Load and verify
        updated = manager.load_tracking(sample_tracking.application_id)
        assert updated.current_status == ApplicationStatus.SUBMITTED
        assert len(updated.events) == 2
        assert updated.events[1].event_type == "status_change"
        assert updated.events[1].description == "Application submitted"
    
    def test_update_status_nonexistent(self, manager):
        """Test updating status for nonexistent tracking."""
        success = manager.update_status(
            application_id="nonexistent",
            new_status=ApplicationStatus.SUBMITTED,
            created_by="test_user"
        )
        assert success is False
    
    def test_add_note(self, manager, sample_tracking):
        """Test adding a note to tracking."""
        # Save tracking first
        manager.save_tracking(sample_tracking)
        
        # Add note
        success = manager.add_note(
            application_id=sample_tracking.application_id,
            title="Test Note",
            content="This is a test note",
            created_by="test_user"
        )
        assert success is True
        
        # Load and verify
        updated = manager.load_tracking(sample_tracking.application_id)
        assert len(updated.notes) == 1
        assert updated.notes[0].title == "Test Note"
        assert updated.notes[0].content == "This is a test note"
    
    def test_add_note_nonexistent(self, manager):
        """Test adding note to nonexistent tracking."""
        success = manager.add_note(
            application_id="nonexistent",
            title="Test Note",
            content="Test content",
            created_by="test_user"
        )
        assert success is False
    
    def test_add_reminder(self, manager, sample_tracking):
        """Test adding a reminder to tracking."""
        # Save tracking first
        manager.save_tracking(sample_tracking)
        
        due_date = datetime.now() + timedelta(days=7)
        
        # Add reminder
        success = manager.add_reminder(
            application_id=sample_tracking.application_id,
            title="Test Reminder",
            due_date=due_date,
            description="Test reminder description",
            created_by="test_user"
        )
        assert success is True
        
        # Load and verify
        updated = manager.load_tracking(sample_tracking.application_id)
        assert len(updated.reminders) == 1
        assert updated.reminders[0].title == "Test Reminder"
        assert updated.reminders[0].due_date == due_date
    
    def test_add_reminder_nonexistent(self, manager):
        """Test adding reminder to nonexistent tracking."""
        success = manager.add_reminder(
            application_id="nonexistent",
            title="Test Reminder",
            due_date=datetime.now() + timedelta(days=7),
            created_by="test_user"
        )
        assert success is False
    
    def test_get_overdue_applications(self, manager, sample_tracking):
        """Test getting overdue applications."""
        # Create tracking with past deadline
        overdue_tracking = ApplicationTracking(
            id="overdue_tracking",
            application_id="overdue_app",
            organization_id="test_org",
            grant_id="test_grant",
            current_status=ApplicationStatus.DRAFT,
            assigned_to="test_user",
            grant_deadline=datetime.now() - timedelta(days=1),  # Past deadline
            award_date=datetime.now() + timedelta(days=30),
            funding_amount=None,
        )
        
        # Save both tracking entries
        manager.save_tracking(sample_tracking)
        manager.save_tracking(overdue_tracking)
        
        # Get overdue applications
        overdue = manager.get_overdue_applications()
        assert len(overdue) == 1
        assert overdue[0].application_id == "overdue_app"
    
    def test_get_applications_by_status(self, manager, sample_tracking):
        """Test getting applications by status."""
        # Save tracking
        manager.save_tracking(sample_tracking)
        
        # Get by status
        draft_apps = manager.get_applications_by_status(ApplicationStatus.DRAFT)
        assert len(draft_apps) == 1
        assert draft_apps[0].application_id == sample_tracking.application_id
        
        # Test different status
        submitted_apps = manager.get_applications_by_status(ApplicationStatus.SUBMITTED)
        assert len(submitted_apps) == 0
    
    def test_get_applications_due_soon(self, manager, sample_tracking):
        """Test getting applications due soon."""
        # Create tracking with upcoming deadline
        upcoming_tracking = ApplicationTracking(
            id="upcoming_tracking",
            application_id="upcoming_app",
            organization_id="test_org",
            grant_id="test_grant",
            current_status=ApplicationStatus.DRAFT,
            assigned_to="test_user",
            grant_deadline=datetime.now() + timedelta(days=5),  # Upcoming
            award_date=datetime.now() + timedelta(days=30),
            funding_amount=None,
        )
        
        # Save both tracking entries
        manager.save_tracking(sample_tracking)
        manager.save_tracking(upcoming_tracking)
        
        # Get applications due within 7 days
        due_soon = manager.get_applications_due_soon(days=7)
        assert len(due_soon) == 1
        assert due_soon[0].application_id == "upcoming_app"
    
    def test_get_application_summary(self, manager, sample_tracking):
        """Test getting application summary."""
        # Save tracking
        manager.save_tracking(sample_tracking)
        
        # Get summary
        summary = manager.get_application_summary(sample_tracking.application_id)
        
        assert summary is not None
        assert summary["application_id"] == sample_tracking.application_id
        assert summary["organization_id"] == sample_tracking.organization_id
        assert summary["current_status"] == ApplicationStatus.DRAFT.value
        assert summary["total_events"] == 1
        assert summary["total_notes"] == 0
        assert summary["pending_reminders"] == 0
    
    def test_get_organization_summary(self, manager, sample_tracking):
        """Test getting organization summary."""
        # Save tracking
        manager.save_tracking(sample_tracking)
        
        # Get summary
        summary = manager.get_organization_summary("test_org")
        
        assert summary is not None
        assert summary["organization_id"] == "test_org"
        assert summary["total_applications"] == 1
        assert summary["status_counts"]["draft"] == 1
        assert summary["overdue_applications"] == 0
        assert summary["due_soon_applications"] == 0 