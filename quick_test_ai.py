#!/usr/bin/env python3
"""
Quick test script to verify AI features are working correctly.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all AI modules can be imported."""
    try:
        from grant_ai.ai.deadline_predictor import GrantDeadlinePredictionModel
        from grant_ai.ai.grant_relevance_scorer import GrantRelevanceScorer
        from grant_ai.services.grant_monitoring import GrantMonitoringService
        print("✅ All AI modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_models():
    """Test that basic model creation works."""
    try:
        from grant_ai.models.grant import Grant
        from grant_ai.models.organization import OrganizationProfile

        # Create test grant
        grant = Grant(
            title="Test Grant",
            description="Test description for AI research",
            amount_typical=100000,
            focus_areas=["ai", "research"],
            source="test"
        )

        # Create test organization
        org = OrganizationProfile(
            name="Test Organization",
            description="Test organization for AI",
            focus_areas=["artificial intelligence", "education"],
            target_demographics=["students"]
        )

        print("✅ Basic models created successfully")
        return True
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False

def test_grant_scorer():
    """Test grant relevance scoring."""
    try:
        from grant_ai.ai.grant_relevance_scorer import GrantRelevanceScorer
        from grant_ai.models.grant import Grant
        from grant_ai.models.organization import OrganizationProfile

        # Create scorer
        scorer = GrantRelevanceScorer()

        # Create test data
        grant = Grant(
            title="AI Education Grant",
            description="Funding for artificial intelligence education programs",
            amount_typical=100000,
            focus_areas=["ai", "education"],
            source="test"
        )

        org = OrganizationProfile(
            name="Test Organization",
            description="Education organization focused on AI",
            focus_areas=["artificial intelligence", "education"],
            target_demographics=["students"]
        )

        # Test scoring
        score_breakdown = scorer.calculate_relevance_score(grant, org)

        assert 'final_score' in score_breakdown
        assert 0 <= score_breakdown['final_score'] <= 1

        print(f"✅ Grant scoring works - Score: {score_breakdown['final_score']:.3f}")
        return True
    except Exception as e:
        print(f"❌ Grant scoring error: {e}")
        return False

def test_deadline_predictor():
    """Test deadline prediction."""
    try:
        from grant_ai.ai.deadline_predictor import GrantDeadlinePredictionModel
        from grant_ai.models.grant import Grant

        # Create predictor
        predictor = GrantDeadlinePredictionModel()

        # Create test grant
        grant = Grant(
            title="Research Grant",
            description="Basic research funding",
            amount_typical=50000,
            focus_areas=["research"],
            source="test"
        )

        # Test prediction
        prediction = predictor.predict_deadline(grant)

        assert 'predicted_deadline' in prediction
        assert 'confidence' in prediction
        assert 'method' in prediction

        print(f"✅ Deadline prediction works - Method: {prediction['method']}")
        return True
    except Exception as e:
        print(f"❌ Deadline prediction error: {e}")
        return False

def test_monitoring_service():
    """Test monitoring service creation."""
    try:
        from grant_ai.services.grant_monitoring import GrantMonitoringService

        # Create service
        with tempfile.TemporaryDirectory() as temp_dir:
            service = GrantMonitoringService(data_dir=temp_dir)

            # Test status
            status = service.get_monitoring_status()

            assert 'is_running' in status
            assert 'subscriptions_count' in status

            print("✅ Monitoring service works")
            return True
    except Exception as e:
        print(f"❌ Monitoring service error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Grant-AI ML Features")
    print("=" * 40)

    tests = [
        test_imports,
        test_models,
        test_grant_scorer,
        test_deadline_predictor,
        test_monitoring_service
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All AI features are working correctly!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
