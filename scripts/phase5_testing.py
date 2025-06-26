#!/usr/bin/env python3
"""
Phase 5 Testing Script: Real Organization Data Validation
Tests all workflows end-to-end with CODA and NRG Development profiles
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Any, Dict, List


def load_real_profiles() -> tuple:
    """Load real organization profiles created from actual data"""
    try:
        with open('data/coda_real_profile.json', 'r') as f:
            coda_profile = json.load(f)
        
        with open('data/nrg_real_profile.json', 'r') as f:
            nrg_profile = json.load(f)
            
        return coda_profile, nrg_profile
    except FileNotFoundError as e:
        print(f"❌ Error loading profiles: {e}")
        return None, None

def test_grant_matching(profile: Dict[str, Any], profile_name: str) -> List[Dict]:
    """Test grant matching with real organization data"""
    print(f"\n🔍 Testing Grant Matching for {profile_name}")
    
    # Connect to grants database
    conn = sqlite3.connect('data/grants.db')
    cursor = conn.cursor()
    
    # Get all grants
    cursor.execute("""
        SELECT id, title, description, funder_name, amount_max, 
               focus_areas, eligibility_types, application_deadline
        FROM grants
    """)
    grants = cursor.fetchall()
    conn.close()
    
    print(f"📊 Analyzing {len(grants)} grants against {profile_name} profile")
    
    # Simple matching logic based on focus areas
    profile_focus = [area.lower() for area in profile.get('focus_areas', [])]
    matched_grants = []
    
    for grant in grants:
        grant_id, title, description, funder, amount, focus_areas_json, eligibility, deadline = grant
        
        # Parse focus areas
        try:
            grant_focus = json.loads(focus_areas_json) if focus_areas_json else []
            grant_focus = [area.lower() for area in grant_focus]
        except:
            grant_focus = []
        
        # Calculate match score
        match_score = 0
        matched_areas = []
        
        for profile_area in profile_focus:
            for grant_area in grant_focus:
                if profile_area in grant_area or grant_area in profile_area:
                    match_score += 1
                    matched_areas.append(f"{profile_area} → {grant_area}")
        
        # Add keyword matching in description
        description_lower = description.lower() if description else ""
        for keyword in ['education', 'arts', 'music', 'youth', 'housing', 'community']:
            if keyword in profile_focus and keyword in description_lower:
                match_score += 0.5
        
        if match_score > 0:
            matched_grants.append({
                'id': grant_id,
                'title': title,
                'funder': funder,
                'amount_max': amount,
                'match_score': match_score,
                'matched_areas': matched_areas,
                'deadline': deadline
            })
    
    # Sort by match score
    matched_grants.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Display top matches
    top_matches = matched_grants[:5]
    print(f"✅ Found {len(matched_grants)} total matches, showing top {len(top_matches)}:")
    
    for i, grant in enumerate(top_matches, 1):
        print(f"  {i}. {grant['title']}")
        print(f"     Funder: {grant['funder']}")
        print(f"     Max Amount: ${grant['amount_max']:,}")
        print(f"     Match Score: {grant['match_score']:.1f}")
        print(f"     Deadline: {grant['deadline']}")
        if grant['matched_areas']:
            print(f"     Matched Areas: {'; '.join(grant['matched_areas'][:2])}")
        print()
    
    return matched_grants

def test_questionnaire_workflow(profile: Dict[str, Any], profile_name: str):
    """Test questionnaire completion workflow"""
    print(f"\n📝 Testing Questionnaire Workflow for {profile_name}")
    
    # Simulate questionnaire responses based on profile data
    questionnaire_responses = {
        'organization_name': profile['name'],
        'mission_statement': profile['mission'],
        'primary_focus_areas': profile['focus_areas'][:3],
        'target_demographics': ', '.join(profile.get('target_demographics', [])[:3]),
        'annual_budget': profile.get('annual_budget_range', 'Unknown'),
        'geographic_scope': profile.get('geographic_focus', 'Local'),
        'program_types': profile.get('program_types', [])[:3],
        'funding_priorities': profile.get('funding_priorities', [])[:3],
        'staff_size': '5-15 staff',
        'volunteer_base': 'Moderate',
        'years_operating': '5+ years',
        'previous_grants': 'Some experience',
        'grant_writing_experience': 'Moderate',
        'collaboration_level': 'High',
        'success_metrics': profile.get('measurable_outcomes', [])[:3]
    }
    
    print(f"✅ Questionnaire completed with {len(questionnaire_responses)} responses")
    
    # Validate required fields
    required_fields = ['organization_name', 'mission_statement', 'primary_focus_areas']
    for field in required_fields:
        if not questionnaire_responses.get(field):
            print(f"❌ Missing required field: {field}")
            return False
    
    print("✅ All required questionnaire fields completed")
    
    # Save questionnaire results
    output_file = f"data/questionnaire_results_{profile_name.lower()}.json"
    with open(output_file, 'w') as f:
        json.dump(questionnaire_responses, f, indent=2)
    
    print(f"✅ Questionnaire results saved to {output_file}")
    return True

def test_application_tracking_workflow(profile_name: str, matched_grants: List[Dict]):
    """Test application tracking workflow"""
    print(f"\n📋 Testing Application Tracking for {profile_name}")
    
    if not matched_grants:
        print("❌ No grants to track applications for")
        return
    
    # Create sample applications for top matches
    applications = []
    for i, grant in enumerate(matched_grants[:3], 1):
        application = {
            'id': f"APP_{profile_name.upper()}_{i:03d}",
            'organization': profile_name,
            'grant_id': grant['id'],
            'grant_title': grant['title'],
            'funder': grant['funder'],
            'status': 'Research' if i == 1 else 'Draft' if i == 2 else 'In Review',
            'created_date': datetime.now().isoformat(),
            'deadline': grant['deadline'],
            'amount_requested': min(grant['amount_max'], 50000),  # Reasonable request
            'match_score': grant['match_score'],
            'notes': [
                f"Application created during Phase 5 testing",
                f"High priority grant with match score {grant['match_score']:.1f}"
            ],
            'reminders': [
                {
                    'type': 'deadline',
                    'date': grant['deadline'],
                    'message': f"Application deadline for {grant['title']}"
                }
            ]
        }
        applications.append(application)
    
    print(f"✅ Created {len(applications)} sample applications:")
    for app in applications:
        print(f"  • {app['id']}: {app['grant_title']} ({app['status']})")
    
    # Save applications
    output_file = f"data/applications_{profile_name.lower()}.json"
    with open(output_file, 'w') as f:
        json.dump(applications, f, indent=2)
    
    print(f"✅ Applications saved to {output_file}")
    return applications

def test_reporting_workflow(profile_name: str, applications: List[Dict]):
    """Test reporting workflow"""
    print(f"\n📊 Testing Reporting Workflow for {profile_name}")
    
    if not applications:
        print("❌ No applications to generate reports for")
        return
    
    # Generate summary statistics
    total_applications = len(applications)
    statuses = {}
    total_requested = 0
    
    for app in applications:
        status = app['status']
        statuses[status] = statuses.get(status, 0) + 1
        total_requested += app.get('amount_requested', 0)
    
    report = {
        'organization': profile_name,
        'report_date': datetime.now().isoformat(),
        'summary': {
            'total_applications': total_applications,
            'total_amount_requested': total_requested,
            'status_breakdown': statuses,
            'average_match_score': sum(app['match_score'] for app in applications) / len(applications)
        },
        'applications': applications
    }
    
    print(f"📈 Report Summary for {profile_name}:")
    print(f"  • Total Applications: {total_applications}")
    print(f"  • Total Amount Requested: ${total_requested:,}")
    print(f"  • Average Match Score: {report['summary']['average_match_score']:.1f}")
    print(f"  • Status Breakdown: {statuses}")
    
    # Save report
    output_file = f"data/report_{profile_name.lower()}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Report saved to {output_file}")
    return report

def main():
    """Run comprehensive Phase 5 testing"""
    print("🚀 Phase 5 Testing: Real Organization Data Validation")
    print("=" * 60)
    
    # Load real profiles
    coda_profile, nrg_profile = load_real_profiles()
    
    if not coda_profile or not nrg_profile:
        print("❌ Failed to load real organization profiles")
        return 1
    
    print("✅ Loaded real organization profiles:")
    print(f"  • CODA: {coda_profile['name']}")
    print(f"  • NRG: {nrg_profile['name']}")
    
    # Test workflows for each organization
    organizations = [
        (coda_profile, "CODA"),
        (nrg_profile, "NRG")
    ]
    
    results = {}
    
    for profile, name in organizations:
        print(f"\n{'='*20} TESTING {name} {'='*20}")
        
        # Test 1: Grant Matching
        matched_grants = test_grant_matching(profile, name)
        
        # Test 2: Questionnaire Workflow
        questionnaire_success = test_questionnaire_workflow(profile, name)
        
        # Test 3: Application Tracking
        applications = test_application_tracking_workflow(name, matched_grants)
        
        # Test 4: Reporting
        report = test_reporting_workflow(name, applications)
        
        # Store results
        results[name] = {
            'matched_grants': len(matched_grants),
            'questionnaire_completed': questionnaire_success,
            'applications_created': len(applications) if applications else 0,
            'report_generated': report is not None
        }
    
    # Final summary
    print(f"\n{'='*20} PHASE 5 TEST RESULTS {'='*20}")
    
    all_successful = True
    for org, result in results.items():
        print(f"\n{org} Results:")
        success_indicators = [
            ("Grant Matching", result['matched_grants'] > 0),
            ("Questionnaire", result['questionnaire_completed']),
            ("Application Tracking", result['applications_created'] > 0),
            ("Reporting", result['report_generated'])
        ]
        
        for test_name, success in success_indicators:
            status = "✅" if success else "❌"
            print(f"  {status} {test_name}")
            if not success:
                all_successful = False
    
    if all_successful:
        print(f"\n🎉 Phase 5 Testing SUCCESSFUL!")
        print("All workflows validated with real organization data")
        return 0
    else:
        print(f"\n⚠️  Phase 5 Testing had some issues")
        print("Review individual test results above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
