#!/usr/bin/env python3
"""
Script to populate the foundation database from donors.md
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_foundation_data():
    """Set up foundation data files for Grant AI."""
    print("Setting up Foundation Data Files")
    print("=" * 40)
    
    # Create foundation data directory
    foundation_dir = Path("data/foundations")
    foundation_dir.mkdir(parents=True, exist_ok=True)
    
    # Foundation data from donors.md document
    foundations_data = [
        {
            "id": "gates_foundation",
            "name": "Bill & Melinda Gates Foundation",
            "website": "https://www.gatesfoundation.org/",
            "foundation_type": "private",
            "focus_areas": ["global health", "education", "poverty alleviation"],
            "geographic_scope": "international",
            "geographic_focus": ["global", "united states"],
            "grant_range_min": 100000,
            "grant_range_max": 50000000,
            "application_process": "invitation_only",
            "key_programs": ["Education Innovation", "Global Health Discovery"],
            "integration_notes": "Health, education, and development projects"
        },
        {
            "id": "benedum_foundation",
            "name": "Claude Worthington Benedum Foundation",
            "website": "https://benedum.org/",
            "contact_email": "info@benedum.org",
            "contact_phone": "(412) 288-0360",
            "foundation_type": "private",
            "focus_areas": ["education", "economic development", "community development"],
            "geographic_scope": "regional",
            "geographic_focus": ["west virginia", "southwestern pennsylvania"],
            "grant_range_min": 10000,
            "grant_range_max": 500000,
            "application_process": "letter_of_inquiry",
            "key_programs": ["Education Excellence", "Economic Development"],
            "integration_notes": "Ideal for WV/PA organizations like CODA"
        },
        {
            "id": "united_way_cwv",
            "name": "United Way of Central West Virginia",
            "website": "https://www.unitedwaycwv.org/",
            "contact_email": "info@unitedwaycwv.org",
            "contact_phone": "(304) 340-3557",
            "foundation_type": "community",
            "focus_areas": ["education", "health", "financial stability"],
            "geographic_scope": "regional",
            "geographic_focus": ["central west virginia"],
            "grant_range_min": 1000,
            "grant_range_max": 25000,
            "application_process": "specific_deadlines",
            "key_programs": ["Community Impact", "Education", "Health"],
            "integration_notes": "Great for social service programs"
        },
        {
            "id": "nsf",
            "name": "National Science Foundation",
            "website": "https://www.nsf.gov/",
            "foundation_type": "government",
            "focus_areas": ["STEM education", "research", "innovation"],
            "geographic_scope": "national",
            "geographic_focus": ["united states"],
            "grant_range_min": 50000,
            "grant_range_max": 5000000,
            "application_process": "online_application",
            "key_programs": ["Education and Human Resources", "Computer Science"],
            "integration_notes": "Perfect for STEM/robotics programs"
        },
        {
            "id": "wv_community_foundation",
            "name": "WV Community Foundation",
            "website": "https://www.wvcommunityfoundation.org/",
            "contact_email": "info@wvcommunityfoundation.org",
            "contact_phone": "(304) 346-3036",
            "foundation_type": "community",
            "focus_areas": ["community development", "education", "health"],
            "geographic_scope": "state",
            "geographic_focus": ["west virginia"],
            "grant_range_min": 1000,
            "grant_range_max": 50000,
            "application_process": "online_application",
            "key_programs": ["Community Development", "Education"],
            "integration_notes": "Excellent for local WV projects"
        }
    ]
    
    # Save each foundation as a separate file
    saved_count = 0
    for foundation in foundations_data:
        try:
            foundation_file = foundation_dir / f"{foundation['id']}.json"
            with open(foundation_file, 'w') as f:
                json.dump(foundation, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved: {foundation['name']}")
            saved_count += 1
        except Exception as e:
            print(f"❌ Error saving {foundation['name']}: {e}")
    
    # Create foundation index file
    try:
        index_file = foundation_dir / "index.json"
        index_data = {
            "foundations": [f["id"] for f in foundations_data],
            "count": len(foundations_data),
            "last_updated": "2025-07-06"
        }
        with open(index_file, 'w') as f:
            json.dump(index_data, f, indent=2)
        print(f"✅ Created foundation index with {len(foundations_data)} foundations")
    except Exception as e:
        print(f"❌ Error creating index: {e}")
    
    # Create historical grants data
    create_historical_grants_data()
    
    print(f"\n📊 Foundation data setup complete!")
    print(f"✅ {saved_count} foundations saved to data/foundations/")
    print(f"✅ Foundation matching data ready")
    return saved_count


def create_historical_grants_data():
    """Create historical grants data for CODA."""
    print("\nCreating Historical Grant Data")
    print("-" * 30)
    
    grants_dir = Path("data/grants/historical")
    grants_dir.mkdir(parents=True, exist_ok=True)
    
    historical_grants = [
        {
            "id": "benedum_2023_music",
            "foundation_id": "benedum_foundation",
            "foundation_name": "Claude Worthington Benedum Foundation",
            "organization_name": "Coda Mountain Academy",
            "grant_amount": 15000,
            "grant_date": "2023-06-15",
            "grant_purpose": "Music education equipment",
            "program_name": "Education Excellence",
            "success": True,
            "notes": "Purchase of musical instruments and audio equipment"
        },
        {
            "id": "united_way_2022_camps",
            "foundation_id": "united_way_cwv",
            "foundation_name": "United Way of Central West Virginia",
            "organization_name": "Coda Mountain Academy",
            "grant_amount": 8000,
            "grant_date": "2022-08-01",
            "grant_purpose": "Summer camp scholarships",
            "program_name": "Community Impact",
            "success": True,
            "notes": "Scholarships for underserved youth summer camps"
        },
        {
            "id": "business_coalition_2024_robotics",
            "foundation_id": "local_business_coalition",
            "foundation_name": "Local Business Coalition",
            "organization_name": "Coda Mountain Academy",
            "grant_amount": 5000,
            "grant_date": "2024-03-20",
            "grant_purpose": "Robotics competition team",
            "program_name": "Corporate Sponsorship",
            "success": True,
            "notes": "Corporate sponsorship for competitive robotics team"
        }
    ]
    
    grants_file = grants_dir / "coda_grants.json"
    try:
        with open(grants_file, 'w') as f:
            json.dump(historical_grants, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(historical_grants)} historical grants")
    except Exception as e:
        print(f"❌ Error saving historical grants: {e}")


def test_foundation_matching():
    """Test foundation matching functionality."""
    print("\nTesting Foundation Matching")
    print("=" * 30)
    
    # Load foundation data
    foundation_dir = Path("data/foundations")
    if not foundation_dir.exists():
        print("❌ Foundation data not found. Run setup first.")
        return False
    
    # Load CODA profile for testing
    profiles_dir = Path("data/profiles")
    coda_file = profiles_dir / "coda_profile.json"
    
    if not coda_file.exists():
        print("⚠️ CODA profile not found, creating sample for testing...")
        coda_profile = {
            "name": "Coda Mountain Academy",
            "description": "Arts and STEM education for youth",
            "focus_areas": ["education", "art_education", "robotics"],
            "location": "Fayetteville, West Virginia",
            "preferred_grant_size": [10000, 100000]
        }
    else:
        with open(coda_file, 'r') as f:
            coda_profile = json.load(f)
    
    # Simple matching algorithm
    print(f"🎯 Finding matches for: {coda_profile['name']}")
    
    matches = []
    for foundation_file in foundation_dir.glob("*.json"):
        if foundation_file.name == "index.json":
            continue
            
        try:
            with open(foundation_file, 'r') as f:
                foundation = json.load(f)
            
            score = calculate_match_score(foundation, coda_profile)
            if score > 0.2:  # Minimum threshold
                foundation['match_score'] = score
                matches.append(foundation)
        except Exception as e:
            print(f"⚠️ Error processing {foundation_file}: {e}")
    
    # Sort by match score
    matches.sort(key=lambda f: f.get('match_score', 0), reverse=True)
    
    print(f"\n📊 Found {len(matches)} matching foundations:")
    for i, foundation in enumerate(matches[:5], 1):  # Top 5
        score = foundation.get('match_score', 0)
        print(f"{i}. {foundation['name']} (Score: {score:.2f})")
        print(f"   Focus: {', '.join(foundation['focus_areas'][:2])}")
        if foundation.get('grant_range_min') and foundation.get('grant_range_max'):
            print(f"   Range: ${foundation['grant_range_min']:,} - ${foundation['grant_range_max']:,}")
        print()
    
    return len(matches) > 0


def calculate_match_score(foundation, organization):
    """Calculate a simple match score between foundation and organization."""
    score = 0.0
    
    # Focus area matching
    org_focus = [fa.lower() for fa in organization.get('focus_areas', [])]
    foundation_focus = [fa.lower() for fa in foundation.get('focus_areas', [])]
    
    focus_matches = sum(1 for fa in foundation_focus 
                       if any(of in fa or fa in of for of in org_focus))
    if foundation_focus:
        score += 0.4 * (focus_matches / len(foundation_focus))
    
    # Geographic matching
    org_location = organization.get('location', '').lower()
    foundation_geo = [gf.lower() for gf in foundation.get('geographic_focus', [])]
    
    if ('west virginia' in org_location and 
        any('west virginia' in geo for geo in foundation_geo)):
        score += 0.3
    elif foundation.get('geographic_scope') in ['national', 'international']:
        score += 0.2
    
    # Grant size matching
    org_range = organization.get('preferred_grant_size', [0, 0])
    foundation_min = foundation.get('grant_range_min', 0)
    foundation_max = foundation.get('grant_range_max', 999999999)
    
    if org_range and len(org_range) == 2:
        org_min, org_max = org_range
        if org_max >= foundation_min and org_min <= foundation_max:
            score += 0.3
    
    return min(score, 1.0)


if __name__ == "__main__":
    print("Foundation Database Setup")
    print("=" * 50)
    
    try:
        # Setup foundation data
        count = setup_foundation_data()
        
        if count > 0:
            # Test matching
            success = test_foundation_matching()
            
            if success:
                print("\n🎉 Foundation database setup complete!")
                print(f"✅ {count} foundations configured")
                print("✅ Historical grants data created")
                print("✅ Foundation matching tested")
                print("\nUsage:")
                print("  ./run.sh test-foundations    # Test the foundation system")
                print("  ./run.sh match-foundations   # Find matches for organizations")
            else:
                print("\n⚠️ Foundation setup completed but matching test failed")
        else:
            print("❌ No foundations were configured")
            
    except Exception as e:
        print(f"❌ Error setting up foundation database: {e}")
        import traceback
        traceback.print_exc()
