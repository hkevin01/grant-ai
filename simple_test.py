#!/usr/bin/env python3
"""
Simple test for the WV grant scraper.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import only what we need for testing
try:
    from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus
    from grant_ai.scrapers.wv_grants import WVGrantScraper
    print("✅ Successfully imported grant scraper")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_single_source():
    """Test scraping a single source."""
    print("🧪 Testing single source scraping...")
    
    scraper = WVGrantScraper()
    
    # Test WV Education source
    source_info = scraper.sources['wv_education']
    print(f"Testing source: {source_info['name']}")
    print(f"URL: {source_info['url']}")
    
    try:
        grants = scraper._scrape_education_source(source_info)
        print(f"✅ Found {len(grants)} grants from {source_info['name']}")
        
        for grant in grants[:3]:  # Show first 3
            print(f"  - {grant.title}")
            print(f"    Funder: {grant.funder_name}")
            print(f"    Amount: ${grant.amount_typical:,}")
            print()
            
    except Exception as e:
        print(f"❌ Error testing source: {e}")

def test_sample_generators():
    """Test the sample data generators."""
    print("🧪 Testing sample data generators...")
    
    scraper = WVGrantScraper()
    source_info = {'name': 'Test Source', 'url': 'http://example.com'}
    
    # Test each sample generator
    generators = [
        ('Arts', scraper._get_sample_arts_grants),
        ('Education', scraper._get_sample_education_grants),
        ('Federal', scraper._get_sample_federal_grants),
        ('STEM', scraper._get_sample_stem_grants),
        ('Community', scraper._get_sample_community_grants),
        ('Youth', scraper._get_sample_youth_grants),
        ('Generic', scraper._get_sample_generic_grants)
    ]
    
    for name, generator in generators:
        try:
            grants = generator(source_info)
            print(f"✅ {name}: {len(grants)} sample grants")
            if grants:
                print(f"    Example: {grants[0].title}")
        except Exception as e:
            print(f"❌ {name} generator error: {e}")

def test_source_availability():
    """Test which sources are reachable."""
    print("🧪 Testing source availability...")
    
    scraper = WVGrantScraper()
    
    reachable = 0
    total = len(scraper.sources)
    
    for source_id, source_info in scraper.sources.items():
        try:
            can_resolve = scraper._check_dns_resolution(source_info['url'])
            status = "✅ Reachable" if can_resolve else "❌ Unreachable"
            print(f"  {source_id}: {status}")
            if can_resolve:
                reachable += 1
        except Exception as e:
            print(f"  {source_id}: ❌ Error - {e}")
    
    print(f"\n📊 Source availability: {reachable}/{total} sources reachable")

if __name__ == "__main__":
    print("🚀 Grant Scraper Test Suite")
    print("=" * 40)
    
    test_sample_generators()
    print()
    test_source_availability()
    print()
    test_single_source()
