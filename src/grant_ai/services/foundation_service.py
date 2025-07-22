"""Foundation database service for managing foundation and donor information."""

import json
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from grant_ai.core.db import get_session
from grant_ai.models.foundation import (
    ApplicationProcess,
    Foundation,
    FoundationContact,
    FoundationContactDB,
    FoundationDB,
    FoundationType,
    GeographicScope,
    HistoricalGrant,
    HistoricalGrantDB,
)
from grant_ai.models.organization import OrganizationProfile


class FoundationService:
    """Service for managing foundation and donor database."""
    
    def __init__(self):
        """Initialize the foundation service."""
        self.data_dir = Path("data/foundations")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.session = get_session()
    
    def add_foundation(self, foundation: Foundation) -> str:
        """Add a new foundation to the database."""
        if not foundation.id:
            foundation.id = str(uuid.uuid4())
        
        foundation.created_at = datetime.utcnow()
        foundation.updated_at = datetime.utcnow()
        
        with get_session() as session:
            # Handle enum values - check if they're already strings or need conversion
            foundation_type_val = (
                foundation.foundation_type.value 
                if hasattr(foundation.foundation_type, 'value') 
                else foundation.foundation_type
            )
            geographic_scope_val = (
                foundation.geographic_scope.value 
                if hasattr(foundation.geographic_scope, 'value') 
                else foundation.geographic_scope
            )
            application_process_val = (
                foundation.application_process.value 
                if hasattr(foundation.application_process, 'value') 
                else foundation.application_process
            )
            
            db_foundation = FoundationDB(
                id=foundation.id,
                name=foundation.name,
                website=str(foundation.website) if foundation.website else None,
                grant_portal=str(foundation.grant_portal) if foundation.grant_portal else None,
                contact_email=foundation.contact_email,
                contact_phone=foundation.contact_phone,
                contact_address=foundation.contact_address,
                foundation_type=foundation_type_val,
                focus_areas=foundation.focus_areas,
                geographic_focus=foundation.geographic_focus,
                geographic_scope=geographic_scope_val,
                grant_range_min=foundation.grant_range_min,
                grant_range_max=foundation.grant_range_max,
                typical_grant_amount=foundation.typical_grant_amount,
                application_process=application_process_val,
                key_programs=foundation.key_programs,
                current_opportunities=foundation.current_opportunities,
                description=foundation.description,
                mission_statement=foundation.mission_statement,
                integration_notes=foundation.integration_notes,
                last_contact_date=foundation.last_contact_date,
                relationship_status=foundation.relationship_status,
                success_rate=foundation.success_rate,
                verified_date=foundation.verified_date,
                created_at=foundation.created_at,
                updated_at=foundation.updated_at
            )
            session.add(db_foundation)
            session.commit()
        
        return foundation.id
    
    def get_foundation(self, foundation_id: str) -> Optional[Foundation]:
        """Get a foundation by ID."""
        with get_session() as session:
            db_foundation = session.query(FoundationDB).filter(
                FoundationDB.id == foundation_id
            ).first()
            
            if not db_foundation:
                return None
            
            return self._db_to_pydantic_foundation(db_foundation)
    
    def get_foundations_by_focus_area(self, focus_areas: List[str]) -> List[Foundation]:
        """Get foundations that match any of the given focus areas."""
        foundations = []
        
        with get_session() as session:
            db_foundations = session.query(FoundationDB).all()
            
            for db_foundation in db_foundations:
                foundation_focus_areas = db_foundation.focus_areas or []
                if any(area.lower() in [fa.lower() for fa in foundation_focus_areas] 
                       for area in focus_areas):
                    foundations.append(self._db_to_pydantic_foundation(db_foundation))
        
        return foundations
    
    def get_foundations_by_location(self, location: str) -> List[Foundation]:
        """Get foundations that fund in a specific location."""
        foundations = []
        
        with get_session() as session:
            db_foundations = session.query(FoundationDB).all()
            
            for db_foundation in db_foundations:
                geographic_focus = db_foundation.geographic_focus or []
                if (location.lower() in [gf.lower() for gf in geographic_focus] or
                    db_foundation.geographic_scope in ['national', 'international']):
                    foundations.append(self._db_to_pydantic_foundation(db_foundation))
        
        return foundations
    
    def match_foundations_for_organization(self, org: OrganizationProfile) -> List[Foundation]:
        """Find foundations that match an organization's profile."""
        matched_foundations = []
        
        # Get all foundations
        with get_session() as session:
            db_foundations = session.query(FoundationDB).all()
            
            for db_foundation in db_foundations:
                score = self._calculate_match_score(db_foundation, org)
                if score > 0.3:  # Minimum match threshold
                    foundation = self._db_to_pydantic_foundation(db_foundation)
                    # Add match score as a dynamic attribute (not stored in model)
                    foundation.match_score = score
                    matched_foundations.append(foundation)
        
        # Sort by match score (highest first)
        matched_foundations.sort(key=lambda f: getattr(f, 'match_score', 0), reverse=True)
        
        return matched_foundations
    
    def add_historical_grant(self, grant: HistoricalGrant) -> str:
        """Add a historical grant record."""
        if not grant.id:
            grant.id = str(uuid.uuid4())
        
        grant.created_at = datetime.utcnow()
        grant.updated_at = datetime.utcnow()
        
        with get_session() as session:
            db_grant = HistoricalGrantDB(
                id=grant.id,
                foundation_id=grant.foundation_id,
                foundation_name=grant.foundation_name,
                organization_name=grant.organization_name,
                grant_amount=grant.grant_amount,
                grant_date=grant.grant_date,
                grant_purpose=grant.grant_purpose,
                program_name=grant.program_name,
                duration_months=grant.duration_months,
                application_date=grant.application_date,
                decision_date=grant.decision_date,
                success=grant.success,
                notes=grant.notes,
                lessons_learned=grant.lessons_learned,
                created_at=grant.created_at,
                updated_at=grant.updated_at
            )
            session.add(db_grant)
            session.commit()
        
        return grant.id
    
    def add_foundation_contact(self, contact: FoundationContact) -> str:
        """Add a foundation contact record."""
        if not contact.id:
            contact.id = str(uuid.uuid4())
        
        contact.created_at = datetime.utcnow()
        contact.updated_at = datetime.utcnow()
        
        with get_session() as session:
            db_contact = FoundationContactDB(
                id=contact.id,
                foundation_id=contact.foundation_id,
                contact_date=contact.contact_date,
                contact_type=contact.contact_type,
                contact_person=contact.contact_person,
                purpose=contact.purpose,
                outcome=contact.outcome,
                follow_up_required=contact.follow_up_required,
                follow_up_date=contact.follow_up_date,
                notes=contact.notes,
                created_at=contact.created_at,
                updated_at=contact.updated_at
            )
            session.add(db_contact)
            session.commit()
        
        return contact.id
    
    def get_foundation_contacts(self, foundation_id: str) -> List[FoundationContact]:
        """Get all contacts for a foundation."""
        contacts = []
        
        with get_session() as session:
            db_contacts = session.query(FoundationContactDB).filter(
                FoundationContactDB.foundation_id == foundation_id
            ).order_by(FoundationContactDB.contact_date.desc()).all()
            
            for db_contact in db_contacts:
                contact = FoundationContact(
                    id=db_contact.id,
                    foundation_id=db_contact.foundation_id,
                    contact_date=db_contact.contact_date,
                    contact_type=db_contact.contact_type,
                    contact_person=db_contact.contact_person,
                    purpose=db_contact.purpose,
                    outcome=db_contact.outcome,
                    follow_up_required=db_contact.follow_up_required,
                    follow_up_date=db_contact.follow_up_date,
                    notes=db_contact.notes,
                    created_at=db_contact.created_at,
                    updated_at=db_contact.updated_at
                )
                contacts.append(contact)
        
        return contacts
    
    def load_foundations_from_donors_md(self, donors_file: Path) -> int:
        """Load foundations from the donors.md file."""
        if not donors_file.exists():
            return 0
        
        # This would parse the donors.md file and extract foundation information
        # For now, we'll create the foundations from the documented data
        foundations_data = self._parse_donors_md(donors_file)
        
        count = 0
        for foundation_data in foundations_data:
            foundation = Foundation(**foundation_data)
            self.add_foundation(foundation)
            count += 1
        
        return count
    
    def get_all_foundations(self) -> List[Foundation]:
        """Get all foundations in the database."""
        foundations = []
        
        with get_session() as session:
            db_foundations = session.query(FoundationDB).all()
            
            for db_foundation in db_foundations:
                foundation = self._db_to_pydantic_foundation(db_foundation)
                foundations.append(foundation)
        
        return foundations

    def search_foundations(self, query: str) -> List[Foundation]:
        """Search foundations by name, focus area, or other criteria."""
        foundations = []
        query_lower = query.lower()
        
        with get_session() as session:
            db_foundations = session.query(FoundationDB).all()
            
            for db_foundation in db_foundations:
                # Search in name, focus areas, and description
                name_match = query_lower in db_foundation.name.lower()
                focus_match = any(
                    query_lower in fa.lower()
                    for fa in (db_foundation.focus_areas or [])
                )
                desc_match = (
                    db_foundation.description and
                    query_lower in db_foundation.description.lower()
                )
                
                if name_match or focus_match or desc_match:
                    foundation = self._db_to_pydantic_foundation(db_foundation)
                    foundations.append(foundation)
        
        return foundations

    def get_foundations_by_grant_range(
        self, min_amount: int, max_amount: int
    ) -> List[Foundation]:
        """Get foundations that offer grants within a specific range."""
        foundations = []
        
        with get_session() as session:
            db_foundations = session.query(FoundationDB).all()
            
            for db_foundation in db_foundations:
                has_range = (
                    db_foundation.grant_range_min and
                    db_foundation.grant_range_max
                )
                range_overlap = (
                    max_amount >= db_foundation.grant_range_min and
                    min_amount <= db_foundation.grant_range_max
                )
                
                if has_range and range_overlap:
                    foundation = self._db_to_pydantic_foundation(db_foundation)
                    foundations.append(foundation)
        
        return foundations

    def update_foundation_relationship(
        self,
        foundation_id: str,
        relationship_status: str,
        success_rate: Optional[float] = None
    ) -> bool:
        """Update foundation relationship tracking."""
        try:
            with get_session() as session:
                db_foundation = session.query(FoundationDB).filter(
                    FoundationDB.id == foundation_id
                ).first()
                
                if not db_foundation:
                    return False
                
                db_foundation.relationship_status = relationship_status
                db_foundation.last_contact_date = date.today()
                if success_rate is not None:
                    db_foundation.success_rate = success_rate
                db_foundation.updated_at = datetime.utcnow()
                
                session.commit()
                return True
        except Exception:
            return False

    def get_historical_grants_for_organization(
        self, organization_name: str
    ) -> List[HistoricalGrant]:
        """Get all historical grants for a specific organization."""
        grants = []
        
        with get_session() as session:
            db_grants = session.query(HistoricalGrantDB).filter(
                HistoricalGrantDB.organization_name.ilike(
                    f"%{organization_name}%"
                )
            ).order_by(HistoricalGrantDB.grant_date.desc()).all()
            
            for db_grant in db_grants:
                grant = HistoricalGrant(
                    id=db_grant.id,
                    foundation_id=db_grant.foundation_id,
                    foundation_name=db_grant.foundation_name,
                    organization_name=db_grant.organization_name,
                    grant_amount=db_grant.grant_amount,
                    grant_date=db_grant.grant_date,
                    grant_purpose=db_grant.grant_purpose,
                    program_name=db_grant.program_name,
                    duration_months=db_grant.duration_months,
                    application_date=db_grant.application_date,
                    decision_date=db_grant.decision_date,
                    success=db_grant.success,
                    notes=db_grant.notes,
                    lessons_learned=db_grant.lessons_learned,
                    created_at=db_grant.created_at,
                    updated_at=db_grant.updated_at
                )
                grants.append(grant)
        
        return grants

    def get_foundation_statistics(self) -> Dict[str, Any]:
        """Get statistics about the foundation database."""
        stats = {
            "total_foundations": 0,
            "foundation_types": {},
            "geographic_scopes": {},
            "average_grant_min": 0,
            "average_grant_max": 0,
            "total_historical_grants": 0,
            "total_grant_amount": 0
        }
        
        with get_session() as session:
            # Foundation statistics
            db_foundations = session.query(FoundationDB).all()
            stats["total_foundations"] = len(db_foundations)
            
            grant_mins = []
            grant_maxs = []
            
            for db_foundation in db_foundations:
                # Foundation types
                ftype = db_foundation.foundation_type
                current_count = stats["foundation_types"].get(ftype, 0)
                stats["foundation_types"][ftype] = current_count + 1
                
                # Geographic scopes
                scope = db_foundation.geographic_scope
                current_count = stats["geographic_scopes"].get(scope, 0)
                stats["geographic_scopes"][scope] = current_count + 1
                
                # Grant ranges
                if db_foundation.grant_range_min:
                    grant_mins.append(db_foundation.grant_range_min)
                if db_foundation.grant_range_max:
                    grant_maxs.append(db_foundation.grant_range_max)
            
            if grant_mins:
                stats["average_grant_min"] = sum(grant_mins) // len(grant_mins)
            if grant_maxs:
                stats["average_grant_max"] = sum(grant_maxs) // len(grant_maxs)
            
            # Historical grant statistics
            db_grants = session.query(HistoricalGrantDB).all()
            stats["total_historical_grants"] = len(db_grants)
            total_amount = sum(g.grant_amount for g in db_grants)
            stats["total_grant_amount"] = total_amount
        
        return stats

    def get_upcoming_deadlines(self) -> List[Dict[str, Any]]:
        """Get upcoming foundation deadlines and follow-ups."""
        deadlines = []
        
        with get_session() as session:
            # Get follow-up contacts that are due
            upcoming_contacts = session.query(FoundationContactDB).filter(
                FoundationContactDB.follow_up_required.is_(True),
                FoundationContactDB.follow_up_date <= date.today()
            ).all()
            
            for contact in upcoming_contacts:
                foundation = session.query(FoundationDB).filter(
                    FoundationDB.id == contact.foundation_id
                ).first()
                
                if foundation:
                    deadlines.append({
                        "type": "follow_up",
                        "foundation_name": foundation.name,
                        "foundation_id": foundation.id,
                        "contact_date": contact.follow_up_date,
                        "purpose": contact.purpose,
                        "notes": contact.notes
                    })
        
        return deadlines

    def generate_foundation_report(self, foundation_id: str) -> Dict[str, Any]:
        """Generate a comprehensive report for a specific foundation."""
        with get_session() as session:
            db_foundation = session.query(FoundationDB).filter(
                FoundationDB.id == foundation_id
            ).first()
            
            if not db_foundation:
                return {}
            
            foundation = self._db_to_pydantic_foundation(db_foundation)
            
            # Get historical grants
            db_grants = session.query(HistoricalGrantDB).filter(
                HistoricalGrantDB.foundation_id == foundation_id
            ).all()
            
            # Get contact history
            db_contacts = session.query(FoundationContactDB).filter(
                FoundationContactDB.foundation_id == foundation_id
            ).order_by(FoundationContactDB.contact_date.desc()).all()
            
            return {
                "foundation": foundation.model_dump(),
                "historical_grants": [
                    {
                        "organization": g.organization_name,
                        "amount": g.grant_amount,
                        "date": g.grant_date.isoformat(),
                        "purpose": g.grant_purpose,
                        "success": g.success
                    } for g in db_grants
                ],
                "contact_history": [
                    {
                        "date": c.contact_date.isoformat(),
                        "type": c.contact_type,
                        "purpose": c.purpose,
                        "outcome": c.outcome
                    } for c in db_contacts
                ],
                "statistics": {
                    "total_grants": len(db_grants),
                    "total_amount": sum(g.grant_amount for g in db_grants),
                    "success_rate": len([g for g in db_grants if g.success]) / len(db_grants) if db_grants else 0,
                    "last_contact": db_contacts[0].contact_date.isoformat() if db_contacts else None
                }
            }

    def _calculate_match_score(self, db_foundation: FoundationDB, org: OrganizationProfile) -> float:
        """Calculate match score between foundation and organization."""
        score = 0.0
        
        # Focus area matching (40% of score)
        foundation_focus = [fa.lower() for fa in (db_foundation.focus_areas or [])]
        org_focus = [str(fa).lower() for fa in org.focus_areas]
        
        focus_matches = sum(1 for fa in foundation_focus if any(of in fa or fa in of for of in org_focus))
        if foundation_focus:
            score += 0.4 * (focus_matches / len(foundation_focus))
        
        # Geographic matching (30% of score)
        foundation_geo = [gf.lower() for gf in (db_foundation.geographic_focus or [])]
        if (org.location.lower() in foundation_geo or 
            db_foundation.geographic_scope in ['national', 'international'] or
            any(geo in org.location.lower() for geo in foundation_geo)):
            score += 0.3
        
        # Grant amount matching (20% of score)
        if (org.preferred_grant_size and 
            db_foundation.grant_range_min and 
            db_foundation.grant_range_max):
            org_min, org_max = org.preferred_grant_size
            foundation_min = db_foundation.grant_range_min
            foundation_max = db_foundation.grant_range_max
            
            # Check if there's overlap in grant ranges
            if org_max >= foundation_min and org_min <= foundation_max:
                score += 0.2
        
        # Success rate bonus (10% of score)
        if db_foundation.success_rate and db_foundation.success_rate > 0.2:
            score += 0.1 * min(db_foundation.success_rate, 1.0)
        
        return min(score, 1.0)
    
    def _db_to_pydantic_foundation(self, db_foundation: FoundationDB) -> Foundation:
        """Convert database model to Pydantic model."""
        return Foundation(
            id=db_foundation.id,
            name=db_foundation.name,
            website=db_foundation.website,
            grant_portal=db_foundation.grant_portal,
            contact_email=db_foundation.contact_email,
            contact_phone=db_foundation.contact_phone,
            contact_address=db_foundation.contact_address,
            foundation_type=db_foundation.foundation_type,  # String, not enum
            focus_areas=db_foundation.focus_areas or [],
            geographic_focus=db_foundation.geographic_focus or [],
            geographic_scope=db_foundation.geographic_scope,  # String, not enum
            grant_range_min=db_foundation.grant_range_min,
            grant_range_max=db_foundation.grant_range_max,
            typical_grant_amount=db_foundation.typical_grant_amount,
            application_process=db_foundation.application_process,  # String, not enum
            key_programs=db_foundation.key_programs or [],
            current_opportunities=db_foundation.current_opportunities or [],
            description=db_foundation.description,
            mission_statement=db_foundation.mission_statement,
            integration_notes=db_foundation.integration_notes,
            last_contact_date=db_foundation.last_contact_date,
            relationship_status=db_foundation.relationship_status,
            success_rate=db_foundation.success_rate,
            created_at=db_foundation.created_at,
            updated_at=db_foundation.updated_at,
            verified_date=db_foundation.verified_date
        )
    
    def _parse_donors_md(self, donors_file: Path) -> List[Dict]:
        """Parse the donors.md file to extract foundation data."""
        # This is a simplified parser - in practice, you'd want more robust markdown parsing
        foundations = []
        
        # Foundation data extracted from the document
        foundations_data = [
            {
                "name": "Bill & Melinda Gates Foundation",
                "website": "https://www.gatesfoundation.org/",
                "foundation_type": FoundationType.PRIVATE,
                "focus_areas": ["global health", "education", "poverty alleviation"],
                "geographic_scope": GeographicScope.INTERNATIONAL,
                "geographic_focus": ["global", "united states"],
                "grant_range_min": 100000,
                "grant_range_max": 50000000,
                "application_process": ApplicationProcess.INVITATION_ONLY,
                "key_programs": ["Education Innovation", "Global Health Discovery", "Agricultural Development"],
                "integration_notes": "Add to proposal classifier for health, education, and development projects"
            },
            {
                "name": "Ford Foundation",
                "website": "https://www.fordfoundation.org/",
                "contact_email": "grants@fordfoundation.org",
                "foundation_type": FoundationType.PRIVATE,
                "focus_areas": ["social justice", "inequality", "democracy"],
                "geographic_scope": GeographicScope.INTERNATIONAL,
                "geographic_focus": ["united states", "international"],
                "grant_range_min": 25000,
                "grant_range_max": 5000000,
                "application_process": ApplicationProcess.LETTER_OF_INQUIRY,
                "key_programs": ["Future of Work", "Civic Engagement and Government", "Art and Culture"],
                "integration_notes": "Excellent for community development and social justice projects"
            },
            {
                "name": "Claude Worthington Benedum Foundation",
                "website": "https://benedum.org/",
                "contact_email": "info@benedum.org",
                "contact_phone": "(412) 288-0360",
                "foundation_type": FoundationType.PRIVATE,
                "focus_areas": ["education", "economic development", "community development"],
                "geographic_scope": GeographicScope.REGIONAL,
                "geographic_focus": ["west virginia", "southwestern pennsylvania"],
                "grant_range_min": 10000,
                "grant_range_max": 500000,
                "application_process": ApplicationProcess.LETTER_OF_INQUIRY,
                "key_programs": ["Education Excellence", "Economic Development", "Community Development"],
                "integration_notes": "Ideal for CODA-type organizations in WV/PA region"
            },
            {
                "name": "United Way of Central West Virginia",
                "website": "https://www.unitedwaycwv.org/",
                "contact_email": "info@unitedwaycwv.org",
                "contact_phone": "(304) 340-3557",
                "foundation_type": FoundationType.COMMUNITY,
                "focus_areas": ["education", "health", "financial stability"],
                "geographic_scope": GeographicScope.REGIONAL,
                "geographic_focus": ["central west virginia"],
                "grant_range_min": 1000,
                "grant_range_max": 25000,
                "application_process": ApplicationProcess.SPECIFIC_DEADLINES,
                "key_programs": ["Community Impact", "Education", "Health"],
                "integration_notes": "Great for social service programs"
            },
            {
                "name": "National Science Foundation",
                "website": "https://www.nsf.gov/",
                "foundation_type": FoundationType.GOVERNMENT,
                "focus_areas": ["STEM education", "research", "innovation"],
                "geographic_scope": GeographicScope.NATIONAL,
                "geographic_focus": ["united states"],
                "grant_range_min": 50000,
                "grant_range_max": 5000000,
                "application_process": ApplicationProcess.ONLINE_APPLICATION,
                "key_programs": ["Education and Human Resources", "Computer and Information Science", "Engineering Directorate"],
                "integration_notes": "Perfect for STEM/robotics programs like CODA"
            }
        ]
        
        return foundations_data


# Global instance
foundation_service = FoundationService()
