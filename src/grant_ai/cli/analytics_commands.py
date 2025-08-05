"""
CLI commands for advanced grant analytics features.

This module provides command-line interfaces for the analytics dashboard,
predictive success scoring, and competitive analysis features.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from grant_ai.ai.grant_success_predictor import GrantSuccessPredictor
from grant_ai.analytics.competitive_analysis import CompetitiveAnalysisEngine
from grant_ai.analytics.grant_analytics_dashboard import GrantAnalyticsDashboard
from grant_ai.models.organization import OrganizationProfile


@click.group()
def analytics():
    """Advanced analytics features for grant research."""


@analytics.command()
@click.option('--data-dir', default='data',
              help='Data directory containing grant and application data')
@click.option('--org-profile', required=True,
              help='Path to organization profile JSON file')
@click.option('--output-dir', default='reports',
              help='Output directory for dashboard reports')
@click.option('--format', 'output_format', default='html',
              type=click.Choice(['html', 'pdf', 'json']),
              help='Output format for dashboard')
def dashboard(data_dir: str, org_profile: str, output_dir: str,
              output_format: str):
    """Generate comprehensive grant analytics dashboard."""
    try:
        click.echo("🎨 Generating Grant Analytics Dashboard...")

        # Load organization profile
        with open(org_profile, 'r', encoding='utf-8') as f:
            org_data = json.load(f)
        organization = OrganizationProfile(**org_data)

        # Initialize dashboard
        dashboard = GrantAnalyticsDashboard(data_dir=data_dir)

        # Load and process data
        click.echo("📊 Loading application and grant data...")
        dashboard.load_applications_data()
        dashboard.load_grants_data()

        # Generate analytics
        click.echo("🔍 Calculating analytics metrics...")
        metrics = dashboard.calculate_dashboard_metrics(organization)

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate dashboard
        if output_format == 'html':
            output_path = dashboard.generate_html_dashboard(
                metrics, f"{output_dir}/dashboard.html"
            )
        elif output_format == 'pdf':
            output_path = dashboard.generate_pdf_dashboard(
                metrics, f"{output_dir}/dashboard.pdf"
            )
        else:  # json
            output_path = f"{output_dir}/dashboard_data.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metrics.__dict__, f, indent=2, default=str)

        click.echo(f"✅ Dashboard generated: {output_path}")

        # Display key metrics
        click.echo("\n📈 Key Metrics Summary:")
        click.echo(f"   Total Applications: {metrics.total_applications}")
        click.echo(f"   Success Rate: {metrics.success_rate:.1%}")
        total_requested = metrics.total_funding_requested
        click.echo(f"   Total Funding Requested: ${total_requested:,.2f}")
        total_awarded = metrics.total_funding_awarded
        click.echo(f"   Total Funding Awarded: ${total_awarded:,.2f}")
        click.echo(f"   ROI: {metrics.roi_percentage:.1f}%")

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.ClickException(str(e))


@analytics.command()
@click.option('--data-dir', default='data',
              help='Data directory containing training data')
@click.option('--org-profile', required=True,
              help='Path to organization profile JSON file')
@click.option('--grant-file', required=True,
              help='Path to grant JSON file to score')
@click.option('--model-path', default=None,
              help='Path to pre-trained model (optional)')
@click.option('--confidence-threshold', default=0.7,
              help='Minimum confidence threshold for predictions')
def predict_success(data_dir: str, org_profile: str, grant_file: str,
                    model_path: Optional[str], confidence_threshold: float):
    """Predict grant application success probability."""
    try:
        click.echo("🔮 Predicting Grant Application Success...")

        # Load organization profile
        with open(org_profile, 'r', encoding='utf-8') as f:
            org_data = json.load(f)
        organization = OrganizationProfile(**org_data)

        # Load grant data
        with open(grant_file, 'r', encoding='utf-8') as f:
            grant_data = json.load(f)

        # Initialize predictor
        predictor = GrantSuccessPredictor(data_dir=data_dir)

        # Load or train model
        if model_path and Path(model_path).exists():
            click.echo(f"📥 Loading pre-trained model from {model_path}")
            predictor.load_model(model_path)
        else:
            click.echo("🏋️ Training new model with available data...")
            predictor.train_model()

        # Make prediction
        click.echo("🎯 Making success prediction...")
        prediction = predictor.predict_success(grant_data, organization)

        # Display results
        click.echo("\n🎲 Success Prediction Results:")
        success_prob = prediction.success_probability
        click.echo(f"   Success Probability: {success_prob:.1%}")
        confidence = prediction.confidence_score
        click.echo(f"   Confidence Score: {confidence:.3f}")
        click.echo(f"   Risk Level: {prediction.risk_level}")
        click.echo(f"   Predicted Outcome: {prediction.predicted_outcome}")

        # Show key factors
        if prediction.key_factors:
            click.echo("\n🔑 Key Success Factors:")
            for factor in prediction.key_factors[:5]:
                click.echo(f"   • {factor}")

        # Show recommendation
        if prediction.recommendation:
            click.echo(f"\n💡 Recommendation: {prediction.recommendation}")

        # Confidence check
        if confidence < confidence_threshold:
            msg = (f"\n⚠️  Warning: Prediction confidence "
                   f"({confidence:.3f}) is below threshold "
                   f"({confidence_threshold:.3f})")
            click.echo(msg)

    except (OSError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.ClickException(str(e))


@analytics.command()
@click.option('--data-dir', default='data',
              help='Data directory containing historical grant data')
@click.option('--training-data',
              help='Path to training data JSON file')
@click.option('--output-model', default='models/success_predictor.pkl',
              help='Output path for trained model')
@click.option('--test-size', default=0.2,
              help='Fraction of data to use for testing')
def train_success_model(data_dir: str, training_data: Optional[str],
                        output_model: str, test_size: float):
    """Train the grant success prediction model."""
    try:
        click.echo("🏋️ Training Grant Success Prediction Model...")

        # Initialize predictor
        predictor = GrantSuccessPredictor(data_dir=data_dir)

        # Load training data if specified
        if training_data:
            click.echo(f"📥 Loading training data from {training_data}")
            predictor.load_training_data(training_data)

        # Train model
        click.echo("🧠 Training machine learning model...")
        metrics = predictor.train_model(test_size=test_size)

        # Create output directory
        Path(output_model).parent.mkdir(parents=True, exist_ok=True)

        # Save model
        click.echo(f"💾 Saving model to {output_model}")
        predictor.save_model(output_model)

        # Display training results
        click.echo("\n📊 Training Results:")
        click.echo(f"   Accuracy: {metrics['accuracy']:.3f}")
        click.echo(f"   Precision: {metrics['precision']:.3f}")
        click.echo(f"   Recall: {metrics['recall']:.3f}")
        click.echo(f"   Cross-validation Score: {metrics['cv_score']:.3f}")

        feature_importance = metrics.get('feature_importance', {})
        if feature_importance:
            click.echo("\n🎯 Top Feature Importance:")
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for feature, importance in sorted_features[:5]:
                click.echo(f"   {feature}: {importance:.3f}")

    except (OSError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.ClickException(str(e))


@analytics.command()
@click.option('--data-dir', default='data',
              help='Data directory containing market data')
@click.option('--org-profile', required=True,
              help='Path to organization profile JSON file')
@click.option('--output-report', default='reports/competitive_analysis.json',
              help='Output path for competitive analysis report')
@click.option('--include-opportunities/--no-opportunities', default=True,
              help='Include opportunity analysis in report')
@click.option('--min-confidence', default=0.6,
              help='Minimum confidence for opportunity recommendations')
def analyze_competition(data_dir: str, org_profile: str, output_report: str,
                        include_opportunities: bool, min_confidence: float):
    """Analyze competitive landscape and identify opportunities."""
    try:
        click.echo("🔍 Analyzing Competitive Landscape...")

        # Load organization profile
        with open(org_profile, 'r', encoding='utf-8') as f:
            org_data = json.load(f)
        organization = OrganizationProfile(**org_data)

        # Initialize competitive analysis engine
        engine = CompetitiveAnalysisEngine(data_dir=data_dir)

        # Perform competitive analysis
        click.echo("📊 Analyzing competitive landscape...")
        analysis_results = engine.analyze_competitive_landscape(
            organization=organization,
            focus_areas=organization.focus_areas
        )

        # Filter opportunities by confidence if requested
        if include_opportunities and 'opportunities' in analysis_results:
            high_conf_opportunities = [
                opp for opp in analysis_results['opportunities']
                if getattr(opp, 'success_probability', 0) >= min_confidence
            ]
            analysis_results['high_confidence_opportunities'] = (
                high_conf_opportunities
            )

        # Create output directory
        Path(output_report).parent.mkdir(parents=True, exist_ok=True)

        # Export results
        click.echo(f"💾 Saving analysis to {output_report}")
        export_path = engine.export_competitive_analysis(
            analysis_results, output_report
        )

        # Display summary
        competitors = analysis_results.get('competitors', [])
        opportunities = analysis_results.get('opportunities', [])

        click.echo("\n🏆 Competitive Analysis Summary:")
        click.echo(f"   Competitors Identified: {len(competitors)}")

        if competitors:
            top_competitor = competitors[0]
            comp_name = top_competitor.organization_name
            comp_rate = top_competitor.success_rate
            msg = (f"   Top Competitor: {comp_name} "
                   f"(Success Rate: {comp_rate:.1%})")
            click.echo(msg)

        if include_opportunities:
            click.echo(f"   Opportunities Found: {len(opportunities)}")

            high_conf_count = len(analysis_results.get(
                'high_confidence_opportunities', []
            ))
            click.echo(f"   High Confidence Opportunities: {high_conf_count}")

        # Show top opportunities
        if opportunities:
            click.echo("\n🎯 Top Opportunities:")
            for i, opp in enumerate(opportunities[:3], 1):
                opp_desc = getattr(opp, 'description', 'Unknown')
                opp_prob = getattr(opp, 'success_probability', 0)
                msg = (f"   {i}. {opp_desc} "
                       f"(Success Probability: {opp_prob:.1%})")
                click.echo(msg)

        click.echo(f"\n📋 Full report available at: {export_path}")

    except (OSError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.ClickException(str(e))


@analytics.command()
@click.option('--data-dir', default='data',
              help='Data directory containing analytics data')
@click.option('--org-profile', required=True,
              help='Path to organization profile JSON file')
@click.option('--output-dir', default='reports',
              help='Output directory for comprehensive report')
def comprehensive_report(data_dir: str, org_profile: str, output_dir: str):
    """Generate comprehensive analytics report with all features."""
    try:
        click.echo("📊 Generating Comprehensive Analytics Report...")

        # Load organization profile
        with open(org_profile, 'r', encoding='utf-8') as f:
            org_data = json.load(f)
        organization = OrganizationProfile(**org_data)

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # 1. Generate Dashboard Analytics
        click.echo("🎨 Generating dashboard analytics...")
        dashboard = GrantAnalyticsDashboard(data_dir=data_dir)
        dashboard.load_applications_data()
        dashboard.load_grants_data()
        metrics = dashboard.calculate_dashboard_metrics(organization)

        dashboard_path = f"{output_dir}/dashboard.html"
        dashboard.generate_html_dashboard(metrics, dashboard_path)

        # 2. Run Competitive Analysis
        click.echo("🔍 Running competitive analysis...")
        engine = CompetitiveAnalysisEngine(data_dir=data_dir)
        competitive_results = engine.analyze_competitive_landscape(
            organization=organization,
            focus_areas=organization.focus_areas
        )

        competitive_path = f"{output_dir}/competitive_analysis.json"
        engine.export_competitive_analysis(
            competitive_results, competitive_path
        )

        # 3. Generate Success Predictions (if model available)
        click.echo("🔮 Generating success predictions...")
        predictor = GrantSuccessPredictor(data_dir=data_dir)

        # Try to load existing model or train new one
        try:
            predictor.train_model()
            prediction_summary = {
                'model_trained': True,
                'training_metrics': 'Available in model logs'
            }
        except Exception as e:
            prediction_summary = {
                'model_trained': False,
                'error': str(e)
            }

        # 4. Create summary report
        click.echo("📋 Creating summary report...")
        summary_report = {
            'organization': {
                'name': organization.name,
                'focus_areas': organization.focus_areas
            },
            'report_generated': datetime.now().isoformat(),
            'dashboard_metrics': {
                'total_applications': metrics.total_applications,
                'success_rate': metrics.success_rate,
                'total_funding_requested': metrics.total_funding_requested,
                'total_funding_awarded': metrics.total_funding_awarded,
                'roi_percentage': metrics.roi_percentage
            },
            'competitive_analysis': {
                'competitors_found': len(
                    competitive_results.get('competitors', [])
                ),
                'opportunities_identified': len(
                    competitive_results.get('opportunities', [])
                )
            },
            'success_prediction': prediction_summary,
            'file_locations': {
                'dashboard': dashboard_path,
                'competitive_analysis': competitive_path,
                'summary': f"{output_dir}/summary_report.json"
            }
        }

        summary_path = f"{output_dir}/summary_report.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_report, f, indent=2, default=str)

        click.echo("\n🎉 Comprehensive Report Generated!")
        click.echo(f"📁 Report Location: {output_dir}")
        click.echo(f"📊 Dashboard: {dashboard_path}")
        click.echo(f"🔍 Competitive Analysis: {competitive_path}")
        click.echo(f"📋 Summary Report: {summary_path}")

        # Display key insights
        click.echo("\n💡 Key Insights:")
        click.echo(f"   Success Rate: {metrics.success_rate:.1%}")
        click.echo(f"   ROI: {metrics.roi_percentage:.1f}%")
        competitors = competitive_results.get('competitors', [])
        click.echo(f"   Competitors Analyzed: {len(competitors)}")
        opportunities = competitive_results.get('opportunities', [])
        click.echo(f"   Opportunities Found: {len(opportunities)}")

    except (OSError, json.JSONDecodeError, KeyError) as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.ClickException(str(e))


@analytics.command()
def demo():
    """Run a demonstration of all analytics features."""
    try:
        click.echo("🚀 Grant-AI Advanced Analytics Demo")
        click.echo("=" * 50)

        # Create sample data for demo (if needed)
        click.echo("📊 Demo 1: Analytics Dashboard")
        click.echo("-" * 30)
        click.echo("The analytics dashboard provides:")
        click.echo("   • Grant success rate analysis")
        click.echo("   • Application timeline tracking")
        click.echo("   • Funding trends visualization")
        click.echo("   • ROI analysis and projections")
        click.echo("   • Interactive charts and reports")

        click.echo("\n🔮 Demo 2: Success Prediction")
        click.echo("-" * 30)
        click.echo("The success predictor offers:")
        click.echo("   • ML-based success probability scoring")
        click.echo("   • Organization profile analysis")
        click.echo("   • Grant history pattern recognition")
        click.echo("   • Application quality assessment")
        click.echo("   • Risk level categorization")

        click.echo("\n🔍 Demo 3: Competitive Analysis")
        click.echo("-" * 30)
        click.echo("The competitive analysis provides:")
        click.echo("   • Competitor landscape mapping")
        click.echo("   • Success pattern identification")
        click.echo("   • Market opportunity discovery")
        click.echo("   • Strategic recommendations")
        click.echo("   • Market intelligence reports")

        click.echo("\n✅ Demo completed successfully!")
        click.echo("\nTo use these features:")
        click.echo("  grant-ai analytics dashboard --org-profile org.json")
        click.echo("  grant-ai analytics predict-success "
                   "--org-profile org.json --grant-file grant.json")
        click.echo("  grant-ai analytics analyze-competition "
                   "--org-profile org.json")
        click.echo("  grant-ai analytics comprehensive-report "
                   "--org-profile org.json")

    except (OSError, RuntimeError) as e:
        click.echo(f"Demo error: {e}", err=True)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    analytics()
