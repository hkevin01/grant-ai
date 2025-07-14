#!/usr/bin/env python3
"""
Demo script showing foundation database capabilities
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Run foundation database demo."""
    print("🏛️  Foundation Database Demo")
    print("=" * 50)
    
    try:
        from grant_ai.core.db import init_db
        from grant_ai.models.organization import (
            FocusArea,
            OrganizationProfile,
            ProgramType,
        )
        from grant_ai.services.foundation_service import foundation_service

        # Initialize database
        init_db()
        
        # Demo 1: Show all foundations
        print("\n1. 📋 All Foundations in Database:")
        foundations = foundation_service.get_all_foundations()
        for i, foundation in enumerate(foundations[:5], 1):  # Show first 5
            print(f"   {i}. {foundation.name}")
            print(f"      Focus: {', '.join(foundation.focus_areas[:2])}")
            if foundation.grant_range_min and foundation.grant_range_max:
                min_amt = foundation.grant_range_min
                max_amt = foundation.grant_range_max
                print(f"      Range: ${min_amt:,} - ${max_amt:,}")
        
        if len(foundations) > 5:
            print(f"   ... and {len(foundations) - 5} more")
        
        # Demo 2: Search foundations
        print("\n2. 🔍 Search for 'education' foundations:")
        education_foundations = foundation_service.search_foundations("education")
        for foundation in education_foundations[:3]:
            print(f"   • {foundation.name}")
            print(f"     Focus: {', '.join(foundation.focus_areas)}")
        
        # Demo 3: Grant range search
        print("\n3. 💰 Foundations offering $10K-$100K grants:")
        range_foundations = foundation_service.get_foundations_by_grant_range(10000, 100000)
        for foundation in range_foundations[:3]:
            min_amt = foundation.grant_range_min
            max_amt = foundation.grant_range_max
            print(f"   • {foundation.name}: ${min_amt:,} - ${max_amt:,}")
        
        # Demo 4: Organization matching
        print("\n4. 🎯 Matching foundations for CODA-like organization:")
        
        # Create sample CODA profile
        coda_profile = OrganizationProfile(
            name="CODA",
            description="Community organization focused on education programs in music, art, and robotics",
            focus_areas=[FocusArea.MUSIC_EDUCATION, FocusArea.ART_EDUCATION, FocusArea.ROBOTICS],
            program_types=[ProgramType.AFTER_SCHOOL, ProgramType.SUMMER_CAMPS],
            location="West Virginia",
            annual_budget=250000,
            preferred_grant_size=(10000, 100000),
            contact_name="Program Director",
            contact_email="info@coda.org",
            contact_phone="",
            website=None,
            ein=None,
            founded_year=None,
        )
        
        matches = foundation_service.match_foundations_for_organization(coda_profile)
        print(f"   Found {len(matches)} matching foundations:")
        
        for i, foundation in enumerate(matches[:3], 1):  # Top 3 matches
            score = getattr(foundation, 'match_score', 0)
            print(f"   {i}. {foundation.name} (Score: {score:.2f})")
            print(f"      Focus: {', '.join(foundation.focus_areas[:2])}")
            if foundation.integration_notes:
                print(f"      Notes: {foundation.integration_notes[:50]}...")
        
        # Demo 5: Database statistics
        print("\n5. 📊 Database Statistics:")
        stats = foundation_service.get_foundation_statistics()
        print(f"   Total foundations: {stats['total_foundations']}")
        print(f"   Total historical grants: {stats['total_historical_grants']}")
        print(f"   Total grant amount: ${stats['total_grant_amount']:,}")
        
        print("\n   Foundation types:")
        for ftype, count in stats['foundation_types'].items():
            print(f"     {ftype}: {count}")
        
        print("\n✅ Foundation database demo completed successfully!")
        print("\n💡 Next steps:")
        print("   • Use './run.sh setup-foundations' to populate database")
        print("   • Try 'grant-ai foundations --help' for CLI commands")
        print("   • Integrate with GUI for visual foundation management")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure to run from the project root directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
