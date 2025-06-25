"""
Migrate grant data from JSON files to the database using the new ORM model.
"""
import json
from datetime import date, datetime
from pathlib import Path

from grant_ai.core.db import SessionLocal
from grant_ai.models.grant import GrantORM


def parse_date(date_str):
    """Parse date string to Python date object."""
    if not date_str:
        return None
    try:
        if isinstance(date_str, str):
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        return date_str
    except (ValueError, TypeError):
        return None


def migrate_sample_grants():
    """Migrate sample grants from JSON to database."""
    session = SessionLocal()
    
    # Load sample grants from the data directory
    sample_grants_path = Path("data/grants/sample_grants.json")
    
    if not sample_grants_path.exists():
        print(f"❌ Sample grants file not found: {sample_grants_path}")
        return
    
    with open(sample_grants_path, "r") as f:
        grants_data = json.load(f)
    
    count = 0
    for grant_data in grants_data:
        # Check if grant already exists
        existing = session.query(GrantORM).filter_by(id=grant_data["id"]).first()
        if existing:
            print(f"⏭️  Grant {grant_data['id']} already exists, skipping...")
            continue
        
        # Convert Pydantic model to ORM model
        grant_orm = GrantORM(
            id=grant_data["id"],
            title=grant_data["title"],
            description=grant_data.get("description", ""),
            funder_name=grant_data["funder_name"],
            funder_type=grant_data.get("funder_type", ""),
            funding_type=grant_data.get("funding_type", "grant"),
            amount_min=grant_data.get("amount_min"),
            amount_max=grant_data.get("amount_max"),
            amount_typical=grant_data.get("amount_typical"),
            total_funding_available=grant_data.get("total_funding_available"),
            status=grant_data.get("status", "open"),
            application_deadline=parse_date(grant_data.get("application_deadline")),
            decision_date=parse_date(grant_data.get("decision_date")),
            funding_start_date=parse_date(grant_data.get("funding_start_date")),
            funding_duration_months=grant_data.get("funding_duration_months"),
            eligibility_types=grant_data.get("eligibility_types", []),
            focus_areas=grant_data.get("focus_areas", []),
            geographic_restrictions=grant_data.get("geographic_restrictions", []),
            application_requirements=grant_data.get("application_requirements", []),
            reporting_requirements=grant_data.get("reporting_requirements", []),
            matching_funds_required=grant_data.get("matching_funds_required", False),
            matching_percentage=grant_data.get("matching_percentage"),
            application_url=grant_data.get("application_url"),
            information_url=grant_data.get("information_url"),
            contact_email=grant_data.get("contact_email"),
            contact_phone=grant_data.get("contact_phone"),
            source=grant_data.get("source", ""),
            source_url=grant_data.get("source_url"),
            last_updated=datetime.now(),
            created_at=datetime.now(),
            relevance_score=grant_data.get("relevance_score"),
            match_reasons=grant_data.get("match_reasons", [])
        )
        
        session.add(grant_orm)
        count += 1
        print(f"✅ Added grant: {grant_data['title']}")
    
    session.commit()
    session.close()
    print(f"\n🎉 Successfully migrated {count} grants to database!")


if __name__ == "__main__":
    migrate_sample_grants() 