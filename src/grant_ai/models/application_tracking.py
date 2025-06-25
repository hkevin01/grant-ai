"""
Application tracking models for managing grant application status and workflow.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ApplicationStatus(str, Enum):
    """Application status enumeration."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    AWARDED = "awarded"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


class ApplicationEvent(BaseModel):
    """Model representing an event in the application lifecycle."""
    
    id: str = Field(..., description="Unique event identifier")
    application_id: str = Field(..., description="ID of the application")
    event_type: str = Field(..., description="Type of event")
    status_from: Optional[str] = Field(None, description="Previous status")
    status_to: str = Field(..., description="New status")
    description: str = Field("", description="Event description")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field("", description="Who created the event")
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")


class ApplicationNote(BaseModel):
    """Model representing a note on an application."""
    
    id: str = Field(..., description="Unique note identifier")
    application_id: str = Field(..., description="ID of the application")
    title: str = Field("", description="Note title")
    content: str = Field(..., description="Note content")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field("", description="Who created the note")
    is_internal: bool = Field(True, description="Whether this is an internal note")


class ApplicationReminder(BaseModel):
    """Model representing a reminder for an application."""
    
    id: str = Field(..., description="Unique reminder identifier")
    application_id: str = Field(..., description="ID of the application")
    title: str = Field(..., description="Reminder title")
    description: str = Field("", description="Reminder description")
    due_date: datetime = Field(..., description="When the reminder is due")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field("", description="Who created the reminder")
    is_completed: bool = Field(False, description="Whether the reminder is completed")
    completed_at: Optional[datetime] = Field(None, description="When completed")
    
    # Reminder settings
    send_email: bool = Field(True, description="Send email reminder")
    send_notification: bool = Field(True, description="Send in-app notification")


class ApplicationTracking(BaseModel):
    """Model representing the tracking information for an application."""
    
    id: str = Field(..., description="Unique tracking identifier")
    application_id: str = Field(..., description="ID of the application")
    organization_id: str = Field(..., description="ID of the organization")
    grant_id: str = Field("", description="ID of the grant")
    
    # Current status
    current_status: ApplicationStatus = Field(ApplicationStatus.DRAFT, description="Current status")
    status_updated_at: datetime = Field(default_factory=datetime.now)
    
    # Timeline
    events: List[ApplicationEvent] = Field(default_factory=list, description="Application events")
    notes: List[ApplicationNote] = Field(default_factory=list, description="Application notes")
    reminders: List[ApplicationReminder] = Field(default_factory=list, description="Application reminders")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    assigned_to: Optional[str] = Field(None, description="Who is assigned to this application")
    
    # Grant-specific information
    grant_deadline: Optional[datetime] = Field(None, description="Grant application deadline")
    award_date: Optional[datetime] = Field(None, description="Expected award date")
    funding_amount: Optional[float] = Field(None, description="Requested funding amount")
    
    def add_event(self, event_type: str, status_to: ApplicationStatus, 
                  description: str = "", created_by: str = "", 
                  metadata: Optional[Dict[str, Any]] = None) -> ApplicationEvent:
        """Add an event to the application timeline."""
        event = ApplicationEvent(
            id=f"event_{self.application_id}_{len(self.events) + 1}",
            application_id=self.application_id,
            event_type=event_type,
            status_from=self.current_status.value,
            status_to=status_to.value,
            description=description,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        self.events.append(event)
        self.current_status = status_to
        self.status_updated_at = datetime.now()
        self.updated_at = datetime.now()
        
        return event
    
    def add_note(self, title: str, content: str, created_by: str, 
                 is_internal: bool = True) -> ApplicationNote:
        """Add a note to the application."""
        note = ApplicationNote(
            id=f"note_{self.application_id}_{len(self.notes) + 1}",
            application_id=self.application_id,
            title=title,
            content=content,
            created_by=created_by,
            is_internal=is_internal
        )
        
        self.notes.append(note)
        self.updated_at = datetime.now()
        
        return note
    
    def add_reminder(self, title: str, due_date: datetime, description: str = "",
                    created_by: str = "", send_email: bool = True, 
                    send_notification: bool = True) -> ApplicationReminder:
        """Add a reminder to the application."""
        reminder = ApplicationReminder(
            id=f"reminder_{self.application_id}_{len(self.reminders) + 1}",
            application_id=self.application_id,
            title=title,
            description=description,
            due_date=due_date,
            created_by=created_by,
            send_email=send_email,
            send_notification=send_notification
        )
        
        self.reminders.append(reminder)
        self.updated_at = datetime.now()
        
        return reminder
    
    def get_pending_reminders(self) -> List[ApplicationReminder]:
        """Get all pending (not completed) reminders."""
        return [r for r in self.reminders if not r.is_completed]
    
    def get_overdue_reminders(self) -> List[ApplicationReminder]:
        """Get all overdue reminders."""
        now = datetime.now()
        return [r for r in self.reminders if not r.is_completed and r.due_date < now]
    
    def get_recent_events(self, limit: int = 10) -> List[ApplicationEvent]:
        """Get the most recent events."""
        return sorted(self.events, key=lambda e: e.created_at, reverse=True)[:limit]
    
    def get_status_history(self) -> List[ApplicationEvent]:
        """Get all status change events."""
        return [e for e in self.events if e.event_type == "status_change"]
    
    def is_overdue(self) -> bool:
        """Check if the application is overdue."""
        if not self.grant_deadline:
            return False
        return datetime.now() > self.grant_deadline and self.current_status in [
            ApplicationStatus.DRAFT, ApplicationStatus.IN_PROGRESS
        ]
    
    def days_until_deadline(self) -> Optional[int]:
        """Get days until deadline (negative if overdue)."""
        if not self.grant_deadline:
            return None
        
        delta = self.grant_deadline - datetime.now()
        return delta.days
    
    def get_completion_percentage(self) -> float:
        """Get application completion percentage based on status."""
        status_percentages = {
            ApplicationStatus.DRAFT: 25.0,
            ApplicationStatus.IN_PROGRESS: 50.0,
            ApplicationStatus.SUBMITTED: 75.0,
            ApplicationStatus.UNDER_REVIEW: 80.0,
            ApplicationStatus.APPROVED: 90.0,
            ApplicationStatus.AWARDED: 100.0,
            ApplicationStatus.REJECTED: 100.0,
            ApplicationStatus.DECLINED: 100.0,
            ApplicationStatus.WITHDRAWN: 100.0
        }
        
        return status_percentages.get(self.current_status, 0.0) 