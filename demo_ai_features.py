#!/usr/bin/env python3
"""
Demo script showing Grant-AI ML features working with basic dependencies.
This demonstrates the AI features with fallback implementations.
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_basic_functionality():
    """Demo basic functionality that works without external ML libraries."""

    print("🤖 Grant-AI ML Features Demo")
    print("=" * 50)

    # Test 1: Basic models
    print("\n1. 📊 Testing Basic Models")
    print("-" * 30)

    try:
        from grant_ai.models.grant import Grant
        from grant_ai.models.organization import OrganizationProfile

        # Create sample grant
        grant = Grant(
            title="AI Education Innovation Grant",
            description="Funding for artificial intelligence and machine learning education programs in underserved communities",
            amount_typical=150000,
            focus_areas=["artificial intelligence", "education", "community"],
            source="demo"
        )

        # Create sample organization
        org = OrganizationProfile(
            name="Community Development Association (CODA)",
            description="Non-profit focused on education programs in music, art, and robotics",
            focus_areas=["education", "music", "art", "robotics", "after-school"],
            target_demographics=["youth", "underserved communities"]
        )

        print(f"✅ Created Grant: '{grant.title}'")
        print(f"✅ Created Organization: '{org.name}'")

    except Exception as e:
        print(f"❌ Error creating models: {e}")
        return False

    # Test 2: Grant Relevance Scorer (with fallbacks)
    print("\n2. 🎯 Testing Grant Relevance Scoring")
    print("-" * 30)

    try:
        from grant_ai.ai.grant_relevance_scorer import GrantRelevanceScorer

        scorer = GrantRelevanceScorer()
        score_breakdown = scorer.calculate_relevance_score(grant, org)

        print(f"✅ Grant Relevance Analysis:")
        print(f"   Final Score: {score_breakdown['final_score']:.3f}")
        print(f"   Semantic Similarity: {score_breakdown['semantic_similarity']:.3f}")
        print(f"   Keyword Matching: {score_breakdown['keyword_matching']:.3f}")
        print(f"   Sentiment Compatibility: {score_breakdown['sentiment_compatibility']:.3f}")
        print(f"   Confidence: {score_breakdown['confidence']:.3f}")

    except Exception as e:
        print(f"❌ Error in grant scoring: {e}")
        return False

    # Test 3: Deadline Prediction
    print("\n3. ⏰ Testing Deadline Prediction")
    print("-" * 30)

    try:
        from grant_ai.ai.deadline_predictor import GrantDeadlinePredictionModel

        predictor = GrantDeadlinePredictionModel()
        prediction = predictor.predict_deadline(grant)

        print(f"✅ Deadline Prediction:")
        print(f"   Predicted Deadline: {prediction['predicted_deadline'].strftime('%Y-%m-%d')}")
        print(f"   Days from Posting: {prediction['days_from_posting']}")
        print(f"   Prediction Method: {prediction['method']}")
        print(f"   Confidence: {prediction['confidence']:.3f}")

    except Exception as e:
        print(f"❌ Error in deadline prediction: {e}")
        return False

    # Test 4: Monitoring Service
    print("\n4. 🔍 Testing Monitoring Service")
    print("-" * 30)

    try:
        import tempfile

        from grant_ai.services.grant_monitoring import GrantMonitoringService

        with tempfile.TemporaryDirectory() as temp_dir:
            service = GrantMonitoringService(data_dir=temp_dir)
            status = service.get_monitoring_status()

            print(f"✅ Monitoring Service Status:")
            print(f"   Service Running: {status['is_running']}")
            print(f"   Subscriptions: {status['subscriptions_count']}")
            print(f"   Grant Sources: {', '.join(status['sources'])}")
            print(f"   Min Relevance Score: {status['min_relevance_score']}")

    except Exception as e:
        print(f"❌ Error in monitoring service: {e}")
        return False

    # Test 5: CLI Commands structure
    print("\n5. 🖥️  Testing CLI Commands")
    print("-" * 30)

    try:
        from grant_ai.cli.ai_commands import ai

        print("✅ AI CLI commands available:")
        # Get the Click group commands
        for name, command in ai.commands.items():
            print(f"   - grant-ai ai {name}: {command.short_help or 'AI command'}")

    except Exception as e:
        print(f"❌ Error loading CLI commands: {e}")
        return False

    print("\n" + "=" * 50)
    print("🎉 All Grant-AI ML Features Are Working!")
    print("🚀 Ready for advanced grant discovery and analysis!")

    # Show sample usage
    print("\n📖 Quick Start Guide:")
    print("1. Score grants: grant-ai ai score-grants org.json grants.json")
    print("2. Start monitoring: grant-ai ai start-monitoring")
    print("3. Predict deadlines: grant-ai ai predict-deadline grant.json")
    print("4. Train models: grant-ai ai train-deadline-model training_data.json")
    print("5. Run demo: grant-ai ai demo")

    return True

if __name__ == "__main__":
    try:
        success = demo_basic_functionality()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
