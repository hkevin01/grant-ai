"""
Advanced Analytics Dashboard

Provides real-time analytics and visualizations for grant applications.
"""

from datetime import datetime, timedelta
from typing import Dict, List

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from grant_ai.ai.enhanced_matching import EnhancedGrantMatcher
from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile


class AnalyticsDashboard:
    """Advanced analytics dashboard for grant tracking and prediction."""

    def __init__(self):
        """Initialize the analytics dashboard."""
        self.matcher = EnhancedGrantMatcher()
    def summarize_grants(self, grants: List[dict]) -> Dict:
        """Summarize grant statistics for dashboard."""
        total = len(grants)
        by_type = {}
        for grant in grants:
            gtype = grant.get('funding_type', 'unknown')
            by_type[gtype] = by_type.get(gtype, 0) + 1
        return {'total_grants': total, 'by_type': by_type}
    def generate_report(self, grants: List[dict]) -> str:
        """Generate a text report for grants analytics."""
        summary = self.summarize_grants(grants)
        lines = [f"Total grants: {summary['total_grants']}"]
        for gtype, count in summary['by_type'].items():
            lines.append(f"{gtype}: {count}")
        return '\n'.join(lines)
    def generate_success_metrics(
        self,
        org: OrganizationProfile,
        applications: List[Dict]
    ) -> Dict:
        """Generate success metrics for an organization."""
        total = len(applications)
        if not total:
            return {
                'success_rate': 0,
                'average_amount': 0,
                'total_awarded': 0,
                'applications_count': 0
            }

        successful = sum(1 for app in applications if app['status'] == 'awarded')
        amounts = [
            app['amount'] for app in applications
            if app['status'] == 'awarded' and app['amount']
        ]

        return {
            'success_rate': successful / total if total > 0 else 0,
            'average_amount': sum(amounts) / len(amounts) if amounts else 0,
            'total_awarded': sum(amounts),
            'applications_count': total
        }

    def create_trends_chart(
        self,
        applications: List[Dict],
        days: int = 180
    ) -> go.Figure:
        """Create trends chart showing application success over time."""
        # Convert to DataFrame
        df = pd.DataFrame(applications)
        df['date'] = pd.to_datetime(df['submission_date'])
        df['month'] = df['date'].dt.to_period('M')

        # Filter for specified time range
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df['date'] >= cutoff]

        # Create success rate by month
        monthly = df.groupby('month').agg({
            'id': 'count',
            'status': lambda x: sum(x == 'awarded') / len(x)
        }).reset_index()

        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                'Monthly Applications',
                'Success Rate Trend'
            )
        )

        # Add application count bar chart
        fig.add_trace(
            go.Bar(
                x=monthly['month'].astype(str),
                y=monthly['id'],
                name='Applications'
            ),
            row=1, col=1
        )

        # Add success rate line
        fig.add_trace(
            go.Scatter(
                x=monthly['month'].astype(str),
                y=monthly['status'],
                name='Success Rate',
                mode='lines+markers'
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=600,
            title_text='Grant Application Trends',
            showlegend=True
        )

        return fig

    def create_focus_area_chart(
        self,
        applications: List[Dict]
    ) -> go.Figure:
        """Create chart showing success by focus area."""
        # Gather focus area data
        focus_areas = {}
        for app in applications:
            for area in app.get('focus_areas', []):
                if area not in focus_areas:
                    focus_areas[area] = {'total': 0, 'success': 0}
                focus_areas[area]['total'] += 1
                if app['status'] == 'awarded':
                    focus_areas[area]['success'] += 1

        # Calculate success rates
        labels = list(focus_areas.keys())
        success_rates = [
            focus_areas[area]['success'] / focus_areas[area]['total']
            for area in labels
        ]
        totals = [focus_areas[area]['total'] for area in labels]

        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                name='Total Applications',
                x=labels,
                y=totals,
                yaxis='y',
                offsetgroup=1
            ),
            go.Bar(
                name='Success Rate',
                x=labels,
                y=success_rates,
                yaxis='y2',
                offsetgroup=2
            )
        ])

        fig.update_layout(
            title_text='Application Success by Focus Area',
            yaxis=dict(title='Number of Applications'),
            yaxis2=dict(
                title='Success Rate',
                overlaying='y',
                side='right'
            ),
            barmode='group'
        )

        return fig

    def predict_grant_success(
        self,
        org: OrganizationProfile,
        grant: Grant
    ) -> Dict:
        """Predict success probability for a grant application."""
        prob, factors = self.matcher.predict_success_probability(grant, org)

        return {
            'probability': prob,
            'factors': factors,
            'recommendation': 'Apply' if prob >= 0.6 else 'Consider',
            'confidence': 'High' if prob >= 0.8 else 'Medium'
                         if prob >= 0.6 else 'Low'
        }

    def generate_recommendations(
        self,
        org: OrganizationProfile,
        applications: List[Dict]
    ) -> List[Dict]:
        """Generate recommendations for improving success rate."""
        metrics = self.generate_success_metrics(org, applications)

        recommendations = []

        # Success rate recommendations
        if metrics['success_rate'] < 0.3:
            recommendations.append({
                'type': 'success_rate',
                'message': 'Consider focusing on grants with higher match scores',
                'action': 'Review recent successful applications for patterns'
            })

        # Amount recommendations
        if metrics['average_amount'] < org.typical_grant_size * 0.5:
            recommendations.append({
                'type': 'grant_size',
                'message': 'Current grants are below target size',
                'action': 'Search for opportunities with larger award amounts'
            })

        # Volume recommendations
        monthly_apps = metrics['applications_count'] / 6  # Assuming 6 months
        if monthly_apps < 2:
            recommendations.append({
                'type': 'volume',
                'message': 'Consider increasing application volume',
                'action': 'Set goal of 2-3 applications per month'
            })

        return recommendations
        return recommendations
