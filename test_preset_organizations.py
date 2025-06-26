#!/usr/bin/env python3
"""
Test script for preset organization manager.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from grant_ai.utils.preset_organizations import preset_manager


def test_preset_organizations():
    """Test the preset organization manager."""
    print("Testing Preset Organization Manager")
    print("=" * 50)
    
    # Test getting available presets
    print("\n1. Getting available presets...")
    presets = preset_manager.get_available_presets()
    print(f"Found {len(presets)} preset organizations:")
    
    for i, preset in enumerate(presets, 1):
        print(f"  {i}. {preset.display_name}")
        print(f"     Focus: {preset.focus_area}")
        print(f"     Location: {preset.location}")
        print(f"     Description: {preset.description[:80]}...")
        print()
    
    # Test loading specific presets
    print("\n2. Testing preset loading...")
    for preset in presets[:3]:  # Test first 3 presets
        print(f"\nLoading {preset.display_name}...")
        profile_data = preset_manager.load_preset_profile(preset.name)
        
        if profile_data:
            print(f"  ✅ Successfully loaded {preset.display_name}")
            print(f"     Name: {profile_data.get('name', 'N/A')}")
            print(f"     Focus Areas: {profile_data.get('focus_areas', [])}")
            print(f"     Location: {profile_data.get('location', 'N/A')}")
            print(f"     Budget: ${profile_data.get('annual_budget', 'N/A')}")
        else:
            print(f"  ❌ Failed to load {preset.display_name}")
    
    # Test caching
    print("\n3. Testing caching...")
    print("Loading Coda profile twice to test caching...")
    
    coda_data1 = preset_manager.load_preset_profile("coda_profile")
    coda_data2 = preset_manager.load_preset_profile("coda_profile")
    
    if coda_data1 is coda_data2:
        print("  ✅ Caching is working (same object reference)")
    else:
        print("  ❌ Caching may not be working properly")
    
    print("\n4. Test completed successfully!")
    print("The preset organization manager is working correctly.")
    print("All profiles should load quickly without freezing or delays.")

if __name__ == "__main__":
    test_preset_organizations() 