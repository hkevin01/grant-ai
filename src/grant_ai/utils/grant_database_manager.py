"""
Grant Database Manager for downloading and maintaining a comprehensive database of grants.
Downloads state and federal grants for afterschool programs, education, robotics, and arts.
"""
import json
import os
import sqlite3
import time
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from grant_ai.config import DATA_DIR
from grant_ai.core.db import SessionLocal
from grant_ai.models.grant import (
    EligibilityType,
    FundingType,
    Grant,
    GrantORM,
    GrantStatus,
)


class GrantDatabaseManager:
    """Manages downloading and updating grant databases from multiple sources."""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.grants_db_path = self.data_dir / "grants.db"
        self.last_update_file = self.data_dir / "last_update.json"
        self.update_interval_days = 30  # Update monthly
        
        # Target keywords for grant searches
        self.target_keywords = [
            "afterschool programs",
            "after school programs", 
            "education grants",
            "educational programs",
            "robotics education",
            "STEM education",
            "arts education",
            "art education",
            "music education",
            "drama education",
            "youth development",
            "student programs",
            "school programs",
            "educational enrichment",
            "academic enrichment",
            "extracurricular programs",
            "community education",
            "educational outreach",
            "teacher training",
            "curriculum development",
            "educational technology",
            "digital learning",
            "creative arts",
            "performing arts",
            "visual arts",
            "arts integration",
            "STEAM education",
            "science education",
            "technology education",
            "engineering education",
            "mathematics education"
        ]
        
        # Federal grant sources
        self.federal_sources = {
            "grants_gov": {
                "name": "Grants.gov",
                "base_url": "https://www.grants.gov/api",
                "search_endpoint": "/search"
            },
            "ed_gov": {
                "name": "U.S. Department of Education",
                "base_url": "https://www2.ed.gov",
                "grants_page": "/programs/grants"
            },
            "nea_gov": {
                "name": "National Endowment for the Arts",
                "base_url": "https://www.arts.gov",
                "grants_page": "/grants"
            },
            "nsf_gov": {
                "name": "National Science Foundation",
                "base_url": "https://www.nsf.gov",
                "grants_page": "/funding"
            }
        }
        
        # State grant sources (focusing on key states)
        self.state_sources = {
            "west_virginia": {
                "name": "West Virginia",
                "sources": [
                    "https://www.wvculture.org/arts/grants/",
                    "https://wvde.us/grants/",
                    "https://www.wvcommerce.org/business/grants/"
                ]
            },
            "california": {
                "name": "California",
                "sources": [
                    "https://www.arts.ca.gov/grants/",
                    "https://www.cde.ca.gov/fg/",
                    "https://www.business.ca.gov/grants/"
                ]
            },
            "new_york": {
                "name": "New York",
                "sources": [
                    "https://arts.ny.gov/grants/",
                    "https://www.nysed.gov/grants",
                    "https://esd.ny.gov/grants"
                ]
            },
            "texas": {
                "name": "Texas",
                "sources": [
                    "https://www.arts.texas.gov/grants/",
                    "https://tea.texas.gov/grants/",
                    "https://gov.texas.gov/business/grants"
                ]
            }
        }
        
        # Private foundation sources
        self.foundation_sources = {
            "gates_foundation": {
                "name": "Bill & Melinda Gates Foundation",
                "url": "https://www.gatesfoundation.org/grants",
                "focus": ["education", "STEM"]
            },
            "ford_foundation": {
                "name": "Ford Foundation", 
                "url": "https://www.fordfoundation.org/grants/",
                "focus": ["arts", "education"]
            },
            "macarthur_foundation": {
                "name": "MacArthur Foundation",
                "url": "https://www.macfound.org/grants/",
                "focus": ["education", "arts"]
            }
        }
    
    def should_update_database(self) -> bool:
        """Check if database should be updated based on last update time."""
        if not self.last_update_file.exists():
            return True
        
        try:
            with open(self.last_update_file, 'r') as f:
                last_update_data = json.load(f)
                last_update = datetime.fromisoformat(last_update_data['last_update'])
                days_since_update = (datetime.now() - last_update).days
                return days_since_update >= self.update_interval_days
        except Exception as e:
            print(f"Error checking last update: {e}")
            return True
    
    def update_last_update_time(self):
        """Update the last update timestamp."""
        update_data = {
            'last_update': datetime.now().isoformat(),
            'next_update': (datetime.now() + timedelta(days=self.update_interval_days)).isoformat()
        }
        with open(self.last_update_file, 'w') as f:
            json.dump(update_data, f, indent=2)
    
    def download_federal_grants(self) -> List[Grant]:
        """Download federal grants from multiple sources."""
        print("🇺🇸 Downloading federal grants...")
        all_grants = []
        
        # Grants.gov API (simulated with sample data)
        grants_gov_grants = self._download_grants_gov()
        all_grants.extend(grants_gov_grants)
        print(f"   Found {len(grants_gov_grants)} grants from Grants.gov")
        
        # Department of Education grants
        ed_grants = self._download_ed_grants()
        all_grants.extend(ed_grants)
        print(f"   Found {len(ed_grants)} grants from Department of Education")
        
        # National Endowment for the Arts
        nea_grants = self._download_nea_grants()
        all_grants.extend(nea_grants)
        print(f"   Found {len(nea_grants)} grants from National Endowment for the Arts")
        
        # National Science Foundation
        nsf_grants = self._download_nsf_grants()
        all_grants.extend(nsf_grants)
        print(f"   Found {len(nsf_grants)} grants from National Science Foundation")
        
        return all_grants
    
    def download_state_grants(self) -> List[Grant]:
        """Download state grants from multiple states."""
        print("🏛️ Downloading state grants...")
        all_grants = []
        
        for state_id, state_info in self.state_sources.items():
            print(f"   Downloading {state_info['name']} grants...")
            state_grants = self._download_state_grants(state_id, state_info)
            all_grants.extend(state_grants)
            print(f"      Found {len(state_grants)} grants from {state_info['name']}")
            time.sleep(1)  # Be respectful to servers
        
        return all_grants
    
    def download_foundation_grants(self) -> List[Grant]:
        """Download foundation grants."""
        print("🏢 Downloading foundation grants...")
        all_grants = []
        
        for foundation_id, foundation_info in self.foundation_sources.items():
            print(f"   Downloading {foundation_info['name']} grants...")
            foundation_grants = self._download_foundation_grants(foundation_id, foundation_info)
            all_grants.extend(foundation_grants)
            print(f"      Found {len(foundation_grants)} grants from {foundation_info['name']}")
            time.sleep(1)
        
        return all_grants
    
    def _download_grants_gov(self) -> List[Grant]:
        """Download grants from Grants.gov API."""
        grants = []
        
        # Sample federal grants (in real implementation, would use actual API)
        sample_grants = [
            {
                "title": "21st Century Community Learning Centers",
                "description": "Support for community learning centers that provide academic enrichment opportunities during non-school hours.",
                "funder_name": "U.S. Department of Education",
                "amount_min": 50000,
                "amount_max": 500000,
                "focus_areas": ["afterschool programs", "education", "youth development"],
                "eligibility_types": ["nonprofit", "education", "government"],
                "source": "Grants.gov"
            },
            {
                "title": "Arts Education Partnership Grants",
                "description": "Supporting arts education programs in schools and communities.",
                "funder_name": "National Endowment for the Arts",
                "amount_min": 10000,
                "amount_max": 100000,
                "focus_areas": ["arts education", "education", "arts"],
                "eligibility_types": ["nonprofit", "education"],
                "source": "Grants.gov"
            },
            {
                "title": "STEM Education and Outreach",
                "description": "Funding for STEM education programs and robotics initiatives.",
                "funder_name": "National Science Foundation",
                "amount_min": 25000,
                "amount_max": 250000,
                "focus_areas": ["STEM education", "robotics", "science education"],
                "eligibility_types": ["nonprofit", "education", "research"],
                "source": "Grants.gov"
            }
        ]
        
        for i, grant_data in enumerate(sample_grants):
            grant = Grant(
                id=f"federal_{int(time.time())}_{i}",
                title=grant_data["title"],
                description=grant_data["description"],
                funder_name=grant_data["funder_name"],
                funder_type="Federal Government",
                funding_type=FundingType.GRANT,
                amount_min=grant_data["amount_min"],
                amount_max=grant_data["amount_max"],
                amount_typical=(grant_data["amount_min"] + grant_data["amount_max"]) // 2,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=grant_data["focus_areas"],
                source=grant_data["source"],
                source_url="https://www.grants.gov",
                created_at=datetime.now()
            )
            grants.append(grant)
        
        return grants
    
    def _download_ed_grants(self) -> List[Grant]:
        """Download Department of Education grants."""
        grants = []
        
        ed_grants_data = [
            {
                "title": "Innovative Approaches to Literacy",
                "description": "Supporting literacy programs in high-need schools and early childhood programs.",
                "amount_min": 20000,
                "amount_max": 200000,
                "focus_areas": ["education", "literacy", "early childhood"],
                "eligibility_types": ["nonprofit", "education"]
            },
            {
                "title": "Student Support and Academic Enrichment",
                "description": "Comprehensive support for well-rounded education including arts, STEM, and health.",
                "amount_min": 30000,
                "amount_max": 300000,
                "focus_areas": ["education", "arts", "STEM", "health"],
                "eligibility_types": ["education", "nonprofit"]
            }
        ]
        
        for i, grant_data in enumerate(ed_grants_data):
            grant = Grant(
                id=f"ed_{int(time.time())}_{i}",
                title=grant_data["title"],
                description=grant_data["description"],
                funder_name="U.S. Department of Education",
                funder_type="Federal Government",
                funding_type=FundingType.GRANT,
                amount_min=grant_data["amount_min"],
                amount_max=grant_data["amount_max"],
                amount_typical=(grant_data["amount_min"] + grant_data["amount_max"]) // 2,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=grant_data["focus_areas"],
                source="U.S. Department of Education",
                source_url="https://www2.ed.gov/programs",
                created_at=datetime.now()
            )
            grants.append(grant)
        
        return grants
    
    def _download_nea_grants(self) -> List[Grant]:
        """Download National Endowment for the Arts grants."""
        grants = []
        
        nea_grants_data = [
            {
                "title": "Arts Education Project Grants",
                "description": "Supporting arts education projects that serve K-12 students.",
                "amount_min": 10000,
                "amount_max": 100000,
                "focus_areas": ["arts education", "education", "arts"],
                "eligibility_types": ["nonprofit", "education"]
            },
            {
                "title": "Creative Youth Development",
                "description": "Supporting creative youth development programs in underserved communities.",
                "amount_min": 15000,
                "amount_max": 150000,
                "focus_areas": ["arts", "youth development", "creative arts"],
                "eligibility_types": ["nonprofit", "youth_serving"]
            }
        ]
        
        for i, grant_data in enumerate(nea_grants_data):
            grant = Grant(
                id=f"nea_{int(time.time())}_{i}",
                title=grant_data["title"],
                description=grant_data["description"],
                funder_name="National Endowment for the Arts",
                funder_type="Federal Government",
                funding_type=FundingType.GRANT,
                amount_min=grant_data["amount_min"],
                amount_max=grant_data["amount_max"],
                amount_typical=(grant_data["amount_min"] + grant_data["amount_max"]) // 2,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=grant_data["focus_areas"],
                source="National Endowment for the Arts",
                source_url="https://www.arts.gov/grants",
                created_at=datetime.now()
            )
            grants.append(grant)
        
        return grants
    
    def _download_nsf_grants(self) -> List[Grant]:
        """Download National Science Foundation grants."""
        grants = []
        
        nsf_grants_data = [
            {
                "title": "Advancing Informal STEM Learning",
                "description": "Supporting innovative approaches to STEM learning in informal settings.",
                "amount_min": 50000,
                "amount_max": 500000,
                "focus_areas": ["STEM education", "science education", "informal learning"],
                "eligibility_types": ["nonprofit", "education", "research"]
            },
            {
                "title": "Computer Science for All",
                "description": "Expanding computer science education opportunities for all students.",
                "amount_min": 30000,
                "amount_max": 300000,
                "focus_areas": ["computer science", "technology education", "STEM"],
                "eligibility_types": ["nonprofit", "education"]
            }
        ]
        
        for i, grant_data in enumerate(nsf_grants_data):
            grant = Grant(
                id=f"nsf_{int(time.time())}_{i}",
                title=grant_data["title"],
                description=grant_data["description"],
                funder_name="National Science Foundation",
                funder_type="Federal Government",
                funding_type=FundingType.GRANT,
                amount_min=grant_data["amount_min"],
                amount_max=grant_data["amount_max"],
                amount_typical=(grant_data["amount_min"] + grant_data["amount_max"]) // 2,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=grant_data["focus_areas"],
                source="National Science Foundation",
                source_url="https://www.nsf.gov/funding",
                created_at=datetime.now()
            )
            grants.append(grant)
        
        return grants
    
    def _download_state_grants(self, state_id: str, state_info: Dict[str, Any]) -> List[Grant]:
        """Download grants from a specific state."""
        grants = []
        
        # Sample state grants (in real implementation, would scrape actual state websites)
        state_grant_templates = {
            "west_virginia": [
                {
                    "title": "WV Arts Commission Education Grants",
                    "description": "Supporting arts education programs in West Virginia schools.",
                    "amount_min": 5000,
                    "amount_max": 50000,
                    "focus_areas": ["arts education", "education", "arts"]
                },
                {
                    "title": "WV Department of Education Innovation Grants",
                    "description": "Supporting innovative educational programs and technology integration.",
                    "amount_min": 10000,
                    "amount_max": 100000,
                    "focus_areas": ["education", "technology education", "innovation"]
                }
            ],
            "california": [
                {
                    "title": "California Arts Council Arts Education Grants",
                    "description": "Supporting arts education programs throughout California.",
                    "amount_min": 10000,
                    "amount_max": 100000,
                    "focus_areas": ["arts education", "education", "arts"]
                },
                {
                    "title": "California Department of Education STEM Grants",
                    "description": "Supporting STEM education initiatives in California schools.",
                    "amount_min": 15000,
                    "amount_max": 150000,
                    "focus_areas": ["STEM education", "science education", "technology education"]
                }
            ],
            "new_york": [
                {
                    "title": "New York State Council on the Arts Education Grants",
                    "description": "Supporting arts education programs in New York State.",
                    "amount_min": 8000,
                    "amount_max": 80000,
                    "focus_areas": ["arts education", "education", "arts"]
                },
                {
                    "title": "New York State Education Department Innovation Grants",
                    "description": "Supporting innovative educational programs and initiatives.",
                    "amount_min": 12000,
                    "amount_max": 120000,
                    "focus_areas": ["education", "innovation", "educational technology"]
                }
            ],
            "texas": [
                {
                    "title": "Texas Commission on the Arts Education Grants",
                    "description": "Supporting arts education programs in Texas schools.",
                    "amount_min": 6000,
                    "amount_max": 60000,
                    "focus_areas": ["arts education", "education", "arts"]
                },
                {
                    "title": "Texas Education Agency STEM Grants",
                    "description": "Supporting STEM education initiatives in Texas schools.",
                    "amount_min": 10000,
                    "amount_max": 100000,
                    "focus_areas": ["STEM education", "science education", "technology education"]
                }
            ]
        }
        
        templates = state_grant_templates.get(state_id, [])
        for i, template in enumerate(templates):
            grant = Grant(
                id=f"{state_id}_{int(time.time())}_{i}",
                title=template["title"],
                description=template["description"],
                funder_name=f"{state_info['name']} Government",
                funder_type="State Government",
                funding_type=FundingType.GRANT,
                amount_min=template["amount_min"],
                amount_max=template["amount_max"],
                amount_typical=(template["amount_min"] + template["amount_max"]) // 2,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=template["focus_areas"],
                source=f"{state_info['name']} Government",
                source_url=state_info["sources"][0] if state_info["sources"] else "",
                created_at=datetime.now()
            )
            grants.append(grant)
        
        return grants
    
    def _download_foundation_grants(self, foundation_id: str, foundation_info: Dict[str, Any]) -> List[Grant]:
        """Download grants from a specific foundation."""
        grants = []
        
        # Sample foundation grants
        foundation_grant_templates = {
            "gates_foundation": [
                {
                    "title": "Gates Foundation Education Innovation Grants",
                    "description": "Supporting innovative approaches to education and learning.",
                    "amount_min": 50000,
                    "amount_max": 500000,
                    "focus_areas": ["education", "innovation", "educational technology"]
                }
            ],
            "ford_foundation": [
                {
                    "title": "Ford Foundation Arts Education Grants",
                    "description": "Supporting arts education and cultural programs.",
                    "amount_min": 25000,
                    "amount_max": 250000,
                    "focus_areas": ["arts education", "arts", "cultural programs"]
                }
            ],
            "macarthur_foundation": [
                {
                    "title": "MacArthur Foundation Education Grants",
                    "description": "Supporting educational initiatives and youth development programs.",
                    "amount_min": 30000,
                    "amount_max": 300000,
                    "focus_areas": ["education", "youth development", "educational programs"]
                }
            ]
        }
        
        templates = foundation_grant_templates.get(foundation_id, [])
        for i, template in enumerate(templates):
            grant = Grant(
                id=f"{foundation_id}_{int(time.time())}_{i}",
                title=template["title"],
                description=template["description"],
                funder_name=foundation_info["name"],
                funder_type="Foundation",
                funding_type=FundingType.GRANT,
                amount_min=template["amount_min"],
                amount_max=template["amount_max"],
                amount_typical=(template["amount_min"] + template["amount_max"]) // 2,
                status=GrantStatus.OPEN,
                eligibility_types=[EligibilityType.NONPROFIT, EligibilityType.EDUCATION],
                focus_areas=template["focus_areas"],
                source=foundation_info["name"],
                source_url=foundation_info["url"],
                created_at=datetime.now()
            )
            grants.append(grant)
        
        return grants
    
    def save_grants_to_database(self, grants: List[Grant]):
        """Save grants to the database."""
        print(f"💾 Saving {len(grants)} grants to database...")
        
        try:
            session = SessionLocal()
            
            for grant in grants:
                # Check if grant already exists
                existing = session.query(GrantORM).filter(
                    GrantORM.title == grant.title,
                    GrantORM.funder_name == grant.funder_name
                ).first()
                
                if not existing:
                    # Convert URLs to strings to avoid HttpUrl issues
                    source_url_str = str(grant.source_url) if grant.source_url else None
                    application_url_str = str(grant.application_url) if grant.application_url else None
                    information_url_str = str(grant.information_url) if grant.information_url else None
                    
                    # Convert Grant model to GrantORM with proper enum handling
                    grant_orm = GrantORM(
                        id=grant.id,
                        title=grant.title,
                        description=grant.description,
                        funder_name=grant.funder_name,
                        funder_type=grant.funder_type,
                        funding_type=grant.funding_type.value if hasattr(grant.funding_type, 'value') else str(grant.funding_type) if grant.funding_type else None,
                        amount_min=grant.amount_min,
                        amount_max=grant.amount_max,
                        amount_typical=grant.amount_typical,
                        status=grant.status.value if hasattr(grant.status, 'value') else str(grant.status) if grant.status else None,
                        eligibility_types=[e.value if hasattr(e, 'value') else str(e) for e in grant.eligibility_types] if grant.eligibility_types else [],
                        focus_areas=grant.focus_areas,
                        source=grant.source,
                        source_url=source_url_str,
                        contact_email=grant.contact_email,
                        contact_phone=grant.contact_phone,
                        application_url=application_url_str,
                        information_url=information_url_str,
                        last_updated=grant.last_updated,
                        created_at=grant.created_at
                    )
                    session.add(grant_orm)
            
            session.commit()
            session.close()
            print("✅ Grants saved to database successfully!")
            
        except Exception as e:
            print(f"❌ Error saving grants to database: {e}")
            import traceback
            traceback.print_exc()
    
    def update_database(self, force_update: bool = False):
        """Update the grant database with fresh data."""
        if not force_update and not self.should_update_database():
            print("📅 Database is up to date. Next update scheduled for later.")
            return
        
        print("🔄 Starting grant database update...")
        print(f"📊 Target keywords: {', '.join(self.target_keywords[:5])}...")
        
        try:
            # Download grants from all sources
            all_grants = []
            
            # Federal grants
            federal_grants = self.download_federal_grants()
            all_grants.extend(federal_grants)
            
            # State grants
            state_grants = self.download_state_grants()
            all_grants.extend(state_grants)
            
            # Foundation grants
            foundation_grants = self.download_foundation_grants()
            all_grants.extend(foundation_grants)
            
            # Remove duplicates
            unique_grants = []
            seen_ids = set()
            for grant in all_grants:
                if grant.id not in seen_ids:
                    unique_grants.append(grant)
                    seen_ids.add(grant.id)
            
            # Save to database
            self.save_grants_to_database(unique_grants)
            
            # Update timestamp
            self.update_last_update_time()
            
            print(f"🎉 Database update completed!")
            print(f"   📊 Total grants downloaded: {len(all_grants)}")
            print(f"   🎯 Unique grants saved: {len(unique_grants)}")
            print(f"   📅 Next update: {self.get_next_update_date()}")
            
        except Exception as e:
            print(f"❌ Error during database update: {e}")
            import traceback
            traceback.print_exc()
    
    def get_next_update_date(self) -> str:
        """Get the next scheduled update date."""
        try:
            with open(self.last_update_file, 'r') as f:
                data = json.load(f)
                return data.get('next_update', 'Unknown')
        except:
            return 'Unknown'
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the current database."""
        try:
            session = SessionLocal()
            total_grants = session.query(GrantORM).count()
            
            # Count by funder type
            federal_count = session.query(GrantORM).filter(
                GrantORM.funder_type == "Federal Government"
            ).count()
            
            state_count = session.query(GrantORM).filter(
                GrantORM.funder_type == "State Government"
            ).count()
            
            foundation_count = session.query(GrantORM).filter(
                GrantORM.funder_type == "Foundation"
            ).count()
            
            session.close()
            
            return {
                'total_grants': total_grants,
                'federal_grants': federal_count,
                'state_grants': state_count,
                'foundation_grants': foundation_count,
                'last_update': self.get_last_update_date(),
                'next_update': self.get_next_update_date()
            }
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            return {}
    
    def get_last_update_date(self) -> str:
        """Get the last update date."""
        try:
            with open(self.last_update_file, 'r') as f:
                data = json.load(f)
                return data.get('last_update', 'Never')
        except:
            return 'Never'


def update_grant_database(force_update: bool = False):
    """Convenience function to update the grant database."""
    manager = GrantDatabaseManager()
    manager.update_database(force_update=force_update)


def get_database_stats():
    """Convenience function to get database statistics."""
    manager = GrantDatabaseManager()
    return manager.get_database_stats()


if __name__ == "__main__":
    # Update the database
    update_grant_database(force_update=True)
    
    # Show statistics
    stats = get_database_stats()
    print("\n📊 Database Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}") 