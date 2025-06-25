"""
SQLAlchemy model for grant applications (tracking).
"""
from datetime import date

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from grant_ai.db import Base


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    AWARDED = "awarded"
    REJECTED = "rejected"

class GrantApplication(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    organization_name = Column(String, nullable=False)
    grant_id = Column(String, ForeignKey("grants.id"), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    submitted_date = Column(Date, nullable=True)
    decision_date = Column(Date, nullable=True)
    notes = Column(String, default="")
    grant = relationship("GrantModel", backref="applications")
