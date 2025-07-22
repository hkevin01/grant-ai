"""Data models for foundations and donors."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Boolean, Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import declarative_base

from grant_ai.core.db import Base


class FoundationType(str, Enum):
    """Enumeration of foundation types."""
    PRIVATE = "private"
    CORPORATE = "corporate"
    COMMUNITY = "community"
    OPERATING = "operating"
    GOVERNMENT = "government"
    FAMILY = "family"


class ApplicationProcess(str, Enum):
    """Enumeration of application processes."""
    ONLINE_APPLICATION = "online_application"
    LETTER_OF_INQUIRY = "letter_of_inquiry"
    INVITATION_ONLY = "invitation_only"
    DIRECT_CONTACT = "direct_contact"
    ROLLING_DEADLINE = "rolling_deadline"
    SPECIFIC_DEADLINES = "specific_deadlines"


class GeographicScope(str, Enum):
    """Enumeration of geographic scopes."""
    LOCAL = "local"
    STATE = "state"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"


class Foundation(BaseModel):
    """Pydantic model for foundation data."""
    id: Optional[str] = None
    name: str = Field(..., description="Foundation name")
    website: Optional[HttpUrl] = Field(None, description="Foundation website")
    grant_portal: Optional[HttpUrl] = Field(None, description="Grant application portal")
    
    # Contact Information
    contact_email: Optional[str] = Field(None, description="Primary contact email")
    contact_phone: Optional[str] = Field(None, description="Primary contact phone")
    contact_address: Optional[str] = Field(None, description="Physical address")
    
    # Foundation Details
    foundation_type: FoundationType = Field(..., description="Type of foundation")
    focus_areas: List[str] = Field(default_factory=list, description="Primary focus areas")
    geographic_focus: List[str] = Field(default_factory=list, description="Geographic areas served")
    geographic_scope: GeographicScope = Field(..., description="Overall geographic scope")
    
    # Grant Information
    grant_range_min: Optional[int] = Field(None, description="Minimum grant amount")
    grant_range_max: Optional[int] = Field(None, description="Maximum grant amount")
    typical_grant_amount: Optional[int] = Field(None, description="Typical grant amount")
    application_process: ApplicationProcess = Field(..., description="How to apply")
    
    # Programs and Opportunities
    key_programs: List[str] = Field(default_factory=list, description="Key funding programs")
    current_opportunities: List[str] = Field(default_factory=list, description="Current open opportunities")
    
    # Additional Information
    description: Optional[str] = Field(None, description="Foundation description")
    mission_statement: Optional[str] = Field(None, description="Foundation mission")
    integration_notes: Optional[str] = Field(None, description="Notes for Grant AI integration")
    
    # Relationship Tracking
    last_contact_date: Optional[date] = Field(None, description="Last contact with foundation")
    relationship_status: Optional[str] = Field(None, description="Current relationship status")
    success_rate: Optional[float] = Field(None, description="Grant success rate with this foundation")
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    verified_date: Optional[date] = Field(None, description="Last verification of foundation info")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class HistoricalGrant(BaseModel):
    """Model for tracking historical grants from foundations."""
    id: Optional[str] = None
    foundation_id: str = Field(..., description="Foundation ID")
    foundation_name: str = Field(..., description="Foundation name")
    organization_name: str = Field(..., description="Recipient organization")
    grant_amount: int = Field(..., description="Grant amount")
    grant_date: date = Field(..., description="Date grant was awarded")
    grant_purpose: str = Field(..., description="Purpose of the grant")
    program_name: Optional[str] = Field(None, description="Foundation program name")
    duration_months: Optional[int] = Field(None, description="Grant duration in months")
    
    # Success Metrics
    application_date: Optional[date] = Field(None, description="Application submission date")
    decision_date: Optional[date] = Field(None, description="Decision notification date")
    success: bool = Field(True, description="Whether grant was successful")
    
    # Notes
    notes: Optional[str] = Field(None, description="Additional notes about the grant")
    lessons_learned: Optional[str] = Field(None, description="Lessons learned from this grant")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class FoundationContact(BaseModel):
    """Model for foundation contact history."""
    id: Optional[str] = None
    foundation_id: str = Field(..., description="Foundation ID")
    contact_date: date = Field(..., description="Date of contact")
    contact_type: str = Field(..., description="Type of contact (email, phone, meeting)")
    contact_person: Optional[str] = Field(None, description="Person contacted")
    purpose: str = Field(..., description="Purpose of contact")
    outcome: Optional[str] = Field(None, description="Outcome of contact")
    follow_up_required: bool = Field(False, description="Whether follow-up is needed")
    follow_up_date: Optional[date] = Field(None, description="Scheduled follow-up date")
    notes: Optional[str] = Field(None, description="Contact notes")
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# SQLAlchemy models for database storage
class FoundationDB(Base):
    """SQLAlchemy model for foundations."""
    __tablename__ = "foundations"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    website = Column(String)
    grant_portal = Column(String)
    
    # Contact Information
    contact_email = Column(String)
    contact_phone = Column(String)
    contact_address = Column(Text)
    
    # Foundation Details
    foundation_type = Column(String, nullable=False)
    focus_areas = Column(SQLiteJSON)
    geographic_focus = Column(SQLiteJSON)
    geographic_scope = Column(String, nullable=False)
    
    # Grant Information
    grant_range_min = Column(Integer)
    grant_range_max = Column(Integer)
    typical_grant_amount = Column(Integer)
    application_process = Column(String, nullable=False)
    
    # Programs and Opportunities
    key_programs = Column(SQLiteJSON)
    current_opportunities = Column(SQLiteJSON)
    
    # Additional Information
    description = Column(Text)
    mission_statement = Column(Text)
    integration_notes = Column(Text)
    
    # Relationship Tracking
    last_contact_date = Column(Date)
    relationship_status = Column(String)
    success_rate = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_date = Column(Date)


class HistoricalGrantDB(Base):
    """SQLAlchemy model for historical grants."""
    __tablename__ = "historical_grants"
    
    id = Column(String, primary_key=True)
    foundation_id = Column(String, nullable=False, index=True)
    foundation_name = Column(String, nullable=False)
    organization_name = Column(String, nullable=False, index=True)
    grant_amount = Column(Integer, nullable=False)
    grant_date = Column(Date, nullable=False)
    grant_purpose = Column(Text, nullable=False)
    program_name = Column(String)
    duration_months = Column(Integer)
    
    # Success Metrics
    application_date = Column(Date)
    decision_date = Column(Date)
    success = Column(Boolean, default=True)
    
    # Notes
    notes = Column(Text)
    lessons_learned = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FoundationContactDB(Base):
    """SQLAlchemy model for foundation contacts."""
    __tablename__ = "foundation_contacts"
    
    id = Column(Integer, primary_key=True)
    foundation_id = Column(Integer)
    contact_name = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    contact_date = Column(Date)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
