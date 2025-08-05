"""
CLI commands for advanced AI grant features.
"""

import asyncio
import json
import logging

import click

from grant_ai.ai.deadline_predictor import GrantDeadlinePredictionModel
from grant_ai.ai.grant_relevance_scorer import GrantRelevanceScorer
from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile
from grant_ai.services.grant_monitoring import GrantMonitoringService
from grant_ai.utils.generate_sample_data import create_sample_organizations


@click.group()
def ai():
    """Advanced AI features for grant research."""


@ai.command()
@click.argument('organization_file', type=click.Path(exists=True))
@click.argument('grants_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for scored grants')
@click.option('--min-score', default=0.5, help='Minimum relevance score')
def score_grants(
    organization_file: str,
    grants_file: str,
    output: str,
    min_score: float
):
    """Score grants for relevance to an organization using AI."""
    try:
        # Load organization profile
        with open(organization_file, 'r', encoding='utf-8') as f:
            org_data = json.load(f)
        organization = OrganizationProfile(**org_data)

        # Load grants
        with open(grants_file, 'r', encoding='utf-8') as f:
            grants_data = json.load(f)
        grants = [Grant(**grant_data) for grant_data in grants_data]

        # Initialize scorer
        scorer = GrantRelevanceScorer()

        # Score grants
        click.echo(f"Scoring {len(grants)} grants for {organization.name}...")
        results = scorer.batch_score_grants(grants, organization)

        # Filter by minimum score
        relevant_results = [
            (grant, score_breakdown)
            for grant, score_breakdown in results
            if score_breakdown['final_score'] >= min_score
        ]

        click.echo(
            f"Found {len(relevant_results)} grants above "
            f"threshold {min_score}"
        )

        # Display top results
        for i, (grant, score_breakdown) in enumerate(relevant_results[:10], 1):
            click.echo(f"\n{i}. {grant.title}")
            score = score_breakdown['final_score']
            click.echo(f"   Relevance Score: {score:.3f}")

            semantic = score_breakdown['semantic_similarity']
            click.echo(f"   Semantic Similarity: {semantic:.3f}")

            keyword = score_breakdown['keyword_matching']
            click.echo(f"   Keyword Matching: {keyword:.3f}")

            sentiment = score_breakdown['sentiment_compatibility']
            click.echo(f"   Sentiment: {sentiment:.3f}")

            confidence = score_breakdown['confidence']
            click.echo(f"   Confidence: {confidence:.3f}")

        # Save results if output specified
        if output:
            output_data = []
            for grant, score_breakdown in relevant_results:
                grant_dict = grant.dict()
                grant_dict['score_breakdown'] = score_breakdown
                output_data.append(grant_dict)

            with open(output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, default=str)

            click.echo(f"\nResults saved to {output}")

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.ClickException(str(e))


@ai.command()
@click.option('--data-dir', default='data',
              help='Data directory for monitoring')
@click.option('--min-score', default=0.6,
              help='Minimum relevance score for notifications')
def start_monitoring(data_dir: str, min_score: float):
    """Start real-time grant monitoring service."""
    async def run_monitoring():
        try:
            # Initialize monitoring service
            service = GrantMonitoringService(data_dir, min_score)

            click.echo("Starting grant monitoring service...")
            click.echo(f"Data directory: {data_dir}")
            click.echo(f"Minimum relevance score: {min_score}")
            click.echo("Press Ctrl+C to stop monitoring")

            # Start monitoring
            await service.start_monitoring()

        except KeyboardInterrupt:
            click.echo("\nMonitoring service stopped by user")
        except (OSError, RuntimeError) as e:
            click.echo(f"Error in monitoring service: {e}", err=True)

    # Run the async monitoring service
    asyncio.run(run_monitoring())


@ai.command()
@click.argument('organization_name')
@click.option('--email', help='Email address for notifications')
@click.option('--webhook', help='Webhook URL for notifications')
def add_subscription(organization_name: str, email: str, webhook: str):
    """Add organization subscription to monitoring service."""
    try:
        # Load sample organizations to find the one requested
        sample_orgs = create_sample_organizations()
        organization = None

        for org in sample_orgs:
            if org.name.lower() == organization_name.lower():
                organization = org
                break

        if not organization:
            msg = (f"Organization '{organization_name}' "
                   f"not found in sample data")
            click.echo(msg)
            click.echo("Available organizations:")
            for org in sample_orgs:
                click.echo(f"  - {org.name}")
            return

        # Create notification settings
        settings = {
            'console_enabled': True,
            'email_enabled': bool(email),
            'webhook_enabled': bool(webhook)
        }

        if email:
            settings['email_address'] = email
        if webhook:
            settings['webhook_url'] = webhook

        # Initialize service and add subscription
        service = GrantMonitoringService()
        success = service.add_subscription(organization, settings)

        if success:
            click.echo(f"✓ Added subscription for {organization.name}")
            if email:
                click.echo(f"  Email notifications: {email}")
            if webhook:
                click.echo(f"  Webhook notifications: {webhook}")
        else:
            click.echo("Failed to add subscription", err=True)

    except (OSError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)


@ai.command()
@click.argument('grant_file', type=click.Path(exists=True))
@click.option('--confidence-threshold', default=0.7,
              help='Confidence threshold for ML prediction')
def predict_deadline(grant_file: str, confidence_threshold: float):
    """Predict application deadline for a grant."""
    try:
        # Load grant
        with open(grant_file, 'r', encoding='utf-8') as f:
            grant_data = json.load(f)
        grant = Grant(**grant_data)

        # Initialize predictor
        predictor = GrantDeadlinePredictionModel()

        # Make prediction
        click.echo(f"Predicting deadline for: {grant.title}")
        prediction = predictor.predict_deadline(grant, confidence_threshold)

        click.echo("\nPrediction Results:")
        click.echo(f"  Predicted Deadline: {prediction['predicted_deadline']}")
        click.echo(f"  Days from Posting: {prediction['days_from_posting']}")
        click.echo(f"  Confidence: {prediction['confidence']:.2f}")
        click.echo(f"  Method: {prediction['method']}")
        click.echo(f"  Reasoning: {prediction['reasoning']}")

        if 'fallback_prediction' in prediction:
            fallback = prediction['fallback_prediction']
            click.echo("\nFallback Prediction:")
            click.echo(f"  Deadline: {fallback['predicted_deadline']}")
            click.echo(f"  Confidence: {fallback['confidence']:.2f}")

    except (OSError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.ClickException(str(e))


@ai.command()
@click.argument('training_data_file', type=click.Path(exists=True))
def train_deadline_model(training_data_file: str):
    """Train the deadline prediction model with historical data."""
    try:
        # Load training data
        with open(training_data_file, 'r', encoding='utf-8') as f:
            training_data = json.load(f)

        grants = [Grant(**grant_data) for grant_data in training_data]

        # Initialize and train model
        predictor = GrantDeadlinePredictionModel()

        click.echo(f"Training deadline model with {len(grants)} grants...")
        metrics = predictor.train_model(grants)

        if 'error' in metrics:
            click.echo(f"Training failed: {metrics['error']}", err=True)
            return

        click.echo("\nTraining Results:")
        click.echo(f"  Training samples: {metrics['training_samples']}")
        click.echo(f"  Test samples: {metrics['test_samples']}")
        click.echo(f"  Test MAE: {metrics['test_mae']:.2f} days")
        click.echo(f"  Test RMSE: {metrics['test_rmse']:.2f} days")

        click.echo("\nModel saved successfully!")

    except (OSError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"Error: {e}", err=True)
        raise click.ClickException(str(e))


@ai.command()
def demo():
    """Run a demonstration of all AI features."""
    try:
        click.echo("🚀 Grant AI - Advanced Features Demo")
        click.echo("=" * 50)

        # Create sample data
        organizations = create_sample_organizations()
        coda = organizations[0]  # CODA organization

        # Demo 1: Grant Relevance Scoring
        click.echo("\n1. 📊 Grant Relevance Scoring Demo")
        click.echo("-" * 30)

        # Create sample grants
        sample_grants = [
            Grant(
                title="Music Education Innovation Grant",
                description=("Funding for innovative music education programs "
                             "in underserved communities"),
                amount_typical=75000,
                focus_areas=["music", "education", "community"],
                source="demo"
            ),
            Grant(
                title="Advanced AI Research Fellowship",
                description=("Research fellowship for artificial intelligence "
                             "applications in healthcare"),
                amount_typical=150000,
                focus_areas=["artificial intelligence", "research",
                            "healthcare"],
                source="demo"
            ),
            Grant(
                title="Youth Arts Program Support",
                description=("Support for after-school arts programs "
                             "targeting at-risk youth"),
                amount_typical=50000,
                focus_areas=["arts", "youth", "after-school"],
                source="demo"
            )
        ]

        scorer = GrantRelevanceScorer()

        for grant in sample_grants:
            score_breakdown = scorer.calculate_relevance_score(grant, coda)
            click.echo(f"\nGrant: {grant.title}")
            score = score_breakdown['final_score']
            semantic = score_breakdown['semantic_similarity']
            keyword = score_breakdown['keyword_matching']

            click.echo(f"  Relevance Score: {score:.3f}")
            click.echo(f"  Semantic Similarity: {semantic:.3f}")
            click.echo(f"  Keyword Match: {keyword:.3f}")

        # Demo 2: Deadline Prediction
        click.echo("\n\n2. ⏰ Deadline Prediction Demo")
        click.echo("-" * 30)

        predictor = GrantDeadlinePredictionModel()

        for grant in sample_grants:
            prediction = predictor.predict_deadline(grant)
            click.echo(f"\nGrant: {grant.title}")
            deadline = prediction['predicted_deadline'].strftime('%Y-%m-%d')
            click.echo(f"  Predicted Deadline: {deadline}")
            click.echo(f"  Days from now: {prediction['days_from_posting']}")
            click.echo(f"  Method: {prediction['method']}")

        # Demo 3: Monitoring Service Status
        click.echo("\n\n3. 🔍 Monitoring Service Demo")
        click.echo("-" * 30)

        service = GrantMonitoringService()
        status = service.get_monitoring_status()

        status_text = 'Running' if status['is_running'] else 'Stopped'
        click.echo(f"Service Status: {status_text}")
        click.echo(f"Subscriptions: {status['subscriptions_count']}")
        click.echo(f"Grant Sources: {', '.join(status['sources'])}")
        click.echo(f"Min Relevance Score: {status['min_relevance_score']}")

        click.echo("\n✅ Demo completed successfully!")
        click.echo("\nTo run individual features:")
        click.echo("  grant-ai ai score-grants [org_file] [grants_file]")
        click.echo("  grant-ai ai start-monitoring")
        click.echo("  grant-ai ai predict-deadline [grant_file]")

    except (OSError, RuntimeError) as e:
        click.echo(f"Demo error: {e}", err=True)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    ai()
