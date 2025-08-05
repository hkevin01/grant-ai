"""
Comprehensive Grant Analytics Dashboard

This module provides advanced visualization and analytics for grant
success rates, application timelines, funding trends, and ROI analysis
with interactive charts.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.dates import DateFormatter

from grant_ai.analytics.success_tracking import SuccessRateAnalytics
from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile


@dataclass
class DashboardMetrics:
    """Container for dashboard analytics metrics."""
    total_applications: int = 0
    success_rate: float = 0.0
    total_funding_requested: float = 0.0
    total_funding_awarded: float = 0.0
    average_processing_time: float = 0.0
    roi_percentage: float = 0.0
    applications_by_status: Dict[str, int] = None
    funding_trends: List[Dict] = None
    timeline_analytics: Dict[str, Any] = None

    def __post_init__(self):
        if self.applications_by_status is None:
            self.applications_by_status = {}
        if self.funding_trends is None:
            self.funding_trends = []
        if self.timeline_analytics is None:
            self.timeline_analytics = {}


class GrantAnalyticsDashboard:
    """Advanced analytics dashboard with interactive visualizations."""

    def __init__(self, data_dir: str = "data"):
        """Initialize dashboard with data directory."""
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        self.success_tracker = SuccessRateAnalytics()

        # Set up matplotlib style for professional charts
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")

        self.logger.info("Grant Analytics Dashboard initialized")

    def generate_comprehensive_metrics(
        self,
        applications: List[Dict],
        grants: List[Grant],
        organization: Optional[OrganizationProfile] = None
    ) -> DashboardMetrics:
        """Generate comprehensive metrics for dashboard."""
        try:
            metrics = DashboardMetrics()

            # Basic counts and rates
            metrics.total_applications = len(applications)

            if applications:
                successful_apps = [
                    app for app in applications
                    if app.get('status') in ['awarded', 'approved', 'funded']
                ]
                success_count = len(successful_apps)
                metrics.success_rate = success_count / len(applications) * 100

                # Financial metrics
                metrics.total_funding_requested = sum(
                    app.get('amount_requested', 0) for app in applications
                )
                metrics.total_funding_awarded = sum(
                    app.get('amount_awarded', 0) for app in successful_apps
                )

                # ROI calculation
                if metrics.total_funding_requested > 0:
                    metrics.roi_percentage = (
                        metrics.total_funding_awarded / metrics.total_funding_requested
                    ) * 100

                # Status breakdown
                status_counts = {}
                for app in applications:
                    status = app.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                metrics.applications_by_status = status_counts

                # Processing time analysis
                processing_times = []
                for app in applications:
                    if app.get('submission_date') and app.get('decision_date'):
                        submission = datetime.fromisoformat(str(app['submission_date']))
                        decision = datetime.fromisoformat(str(app['decision_date']))
                        processing_times.append((decision - submission).days)

                if processing_times:
                    metrics.average_processing_time = np.mean(processing_times)

                # Generate funding trends
                metrics.funding_trends = self._analyze_funding_trends(applications)

                # Timeline analytics
                metrics.timeline_analytics = self._analyze_application_timeline(applications)

            self.logger.info(f"Generated metrics for {metrics.total_applications} applications")
            return metrics

        except Exception as e:
            self.logger.error(f"Error generating dashboard metrics: {e}")
            return DashboardMetrics()

    def _analyze_funding_trends(self, applications: List[Dict]) -> List[Dict]:
        """Analyze funding trends over time."""
        try:
            trends = []

            # Group by year and month
            monthly_data = {}
            for app in applications:
                if app.get('submission_date'):
                    date = datetime.fromisoformat(str(app['submission_date']))
                    month_key = f"{date.year}-{date.month:02d}"

                    if month_key not in monthly_data:
                        monthly_data[month_key] = {
                            'date': month_key,
                            'applications': 0,
                            'awarded': 0,
                            'total_requested': 0,
                            'total_awarded': 0
                        }

                    monthly_data[month_key]['applications'] += 1
                    monthly_data[month_key]['total_requested'] += app.get('amount_requested', 0)

                    if app.get('status') in ['awarded', 'approved', 'funded']:
                        monthly_data[month_key]['awarded'] += 1
                        monthly_data[month_key]['total_awarded'] += app.get('amount_awarded', 0)

            # Convert to list and calculate success rates
            for month_key, data in sorted(monthly_data.items()):
                data['success_rate'] = (
                    data['awarded'] / data['applications'] * 100
                    if data['applications'] > 0 else 0
                )
                trends.append(data)

            return trends

        except Exception as e:
            self.logger.error(f"Error analyzing funding trends: {e}")
            return []

    def _analyze_application_timeline(self, applications: List[Dict]) -> Dict[str, Any]:
        """Analyze application timeline patterns."""
        try:
            timeline_data = {
                'monthly_submissions': {},
                'seasonal_patterns': {},
                'deadline_distribution': {},
                'processing_time_trends': []
            }

            for app in applications:
                if app.get('submission_date'):
                    date = datetime.fromisoformat(str(app['submission_date']))
                    month = date.strftime('%B')
                    season = self._get_season(date.month)

                    # Monthly submissions
                    timeline_data['monthly_submissions'][month] = (
                        timeline_data['monthly_submissions'].get(month, 0) + 1
                    )

                    # Seasonal patterns
                    timeline_data['seasonal_patterns'][season] = (
                        timeline_data['seasonal_patterns'].get(season, 0) + 1
                    )

                    # Processing time if available
                    if app.get('decision_date'):
                        decision_date = datetime.fromisoformat(str(app['decision_date']))
                        processing_days = (decision_date - date).days
                        timeline_data['processing_time_trends'].append({
                            'date': date.isoformat(),
                            'processing_days': processing_days,
                            'status': app.get('status', 'unknown')
                        })

            return timeline_data

        except Exception as e:
            self.logger.error(f"Error analyzing timeline: {e}")
            return {}

    def _get_season(self, month: int) -> str:
        """Get season from month number."""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'

    def create_success_rate_chart(
        self,
        metrics: DashboardMetrics,
        output_path: Optional[str] = None
    ) -> str:
        """Create success rate visualization chart."""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Grant Success Analytics Dashboard', fontsize=16, fontweight='bold')

            # 1. Overall Success Rate Gauge
            self._create_gauge_chart(ax1, metrics.success_rate, "Success Rate", "%")

            # 2. Applications by Status
            if metrics.applications_by_status:
                statuses = list(metrics.applications_by_status.keys())
                counts = list(metrics.applications_by_status.values())
                colors = sns.color_palette("husl", len(statuses))

                ax2.pie(counts, labels=statuses, autopct='%1.1f%%', colors=colors)
                ax2.set_title('Applications by Status')

            # 3. Funding Trends Over Time
            if metrics.funding_trends:
                trend_df = pd.DataFrame(metrics.funding_trends)

                # Line plot for success rate over time
                ax3.plot(trend_df['date'], trend_df['success_rate'],
                        marker='o', linewidth=2, markersize=6)
                ax3.set_title('Success Rate Trend')
                ax3.set_xlabel('Month')
                ax3.set_ylabel('Success Rate (%)')
                ax3.tick_params(axis='x', rotation=45)
                ax3.grid(True, alpha=0.3)

            # 4. ROI Analysis
            roi_data = {
                'Requested': metrics.total_funding_requested,
                'Awarded': metrics.total_funding_awarded,
                'Gap': metrics.total_funding_requested - metrics.total_funding_awarded
            }

            bars = ax4.bar(roi_data.keys(), roi_data.values(),
                          color=['lightcoral', 'lightgreen', 'lightgray'])
            ax4.set_title(f'Funding Analysis (ROI: {metrics.roi_percentage:.1f}%)')
            ax4.set_ylabel('Amount ($)')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}', ha='center', va='bottom')

            plt.tight_layout()

            # Save or return path
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Success rate chart saved to {output_path}")
                return output_path
            else:
                output_path = str(self.data_dir / f"success_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                return output_path

        except Exception as e:
            self.logger.error(f"Error creating success rate chart: {e}")
            return ""

    def _create_gauge_chart(self, ax, value: float, title: str, unit: str):
        """Create a gauge chart for a single metric."""
        # Simple gauge using a pie chart
        remaining = 100 - value
        colors = ['#2ecc71' if value >= 50 else '#e74c3c', '#ecf0f1']

        wedges, texts = ax.pie([value, remaining], colors=colors, startangle=90, counterclock=False)

        # Add center circle to make it look like a gauge
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        ax.add_artist(centre_circle)

        # Add value text in center
        ax.text(0, 0, f'{value:.1f}{unit}', ha='center', va='center',
                fontsize=14, fontweight='bold')
        ax.text(0, -0.3, title, ha='center', va='center', fontsize=12)

        ax.set_aspect('equal')

    def create_timeline_analytics_chart(
        self,
        metrics: DashboardMetrics,
        output_path: Optional[str] = None
    ) -> str:
        """Create timeline analytics visualization."""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Application Timeline Analytics', fontsize=16, fontweight='bold')

            timeline_data = metrics.timeline_analytics

            # 1. Monthly Submission Pattern
            if timeline_data.get('monthly_submissions'):
                months = list(timeline_data['monthly_submissions'].keys())
                counts = list(timeline_data['monthly_submissions'].values())

                ax1.bar(months, counts, color='skyblue')
                ax1.set_title('Applications by Month')
                ax1.set_xlabel('Month')
                ax1.set_ylabel('Number of Applications')
                ax1.tick_params(axis='x', rotation=45)

            # 2. Seasonal Distribution
            if timeline_data.get('seasonal_patterns'):
                seasons = list(timeline_data['seasonal_patterns'].keys())
                counts = list(timeline_data['seasonal_patterns'].values())

                ax2.pie(counts, labels=seasons, autopct='%1.1f%%',
                       colors=sns.color_palette("Set2"))
                ax2.set_title('Seasonal Application Patterns')

            # 3. Processing Time Trends
            if timeline_data.get('processing_time_trends'):
                df = pd.DataFrame(timeline_data['processing_time_trends'])
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')

                # Scatter plot with trend line
                ax3.scatter(df['date'], df['processing_days'], alpha=0.6)

                # Add trend line
                if len(df) > 1:
                    z = np.polyfit(mdates.date2num(df['date']), df['processing_days'], 1)
                    p = np.poly1d(z)
                    ax3.plot(df['date'], p(mdates.date2num(df['date'])),
                            "r--", alpha=0.8, linewidth=2)

                ax3.set_title('Processing Time Trends')
                ax3.set_xlabel('Application Date')
                ax3.set_ylabel('Processing Days')
                ax3.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
                plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)

            # 4. Average Processing Time by Status
            if timeline_data.get('processing_time_trends'):
                df = pd.DataFrame(timeline_data['processing_time_trends'])
                status_times = df.groupby('status')['processing_days'].mean()

                ax4.bar(status_times.index, status_times.values,
                       color=sns.color_palette("viridis", len(status_times)))
                ax4.set_title('Avg Processing Time by Status')
                ax4.set_xlabel('Application Status')
                ax4.set_ylabel('Days')
                ax4.tick_params(axis='x', rotation=45)

            plt.tight_layout()

            # Save chart
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Timeline chart saved to {output_path}")
                return output_path
            else:
                output_path = str(self.data_dir / f"timeline_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                return output_path

        except Exception as e:
            self.logger.error(f"Error creating timeline chart: {e}")
            return ""

    def create_funding_trends_chart(
        self,
        metrics: DashboardMetrics,
        output_path: Optional[str] = None
    ) -> str:
        """Create funding trends visualization."""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Funding Trends Analysis', fontsize=16, fontweight='bold')

            if metrics.funding_trends:
                df = pd.DataFrame(metrics.funding_trends)

                # 1. Monthly Application Volume
                ax1.plot(df['date'], df['applications'], marker='o', linewidth=2, color='blue')
                ax1.set_title('Monthly Application Volume')
                ax1.set_xlabel('Month')
                ax1.set_ylabel('Number of Applications')
                ax1.tick_params(axis='x', rotation=45)
                ax1.grid(True, alpha=0.3)

                # 2. Success Rate Trend
                ax2.plot(df['date'], df['success_rate'], marker='s', linewidth=2, color='green')
                ax2.set_title('Success Rate Trend')
                ax2.set_xlabel('Month')
                ax2.set_ylabel('Success Rate (%)')
                ax2.tick_params(axis='x', rotation=45)
                ax2.grid(True, alpha=0.3)

                # 3. Funding Requested vs Awarded
                x = range(len(df))
                width = 0.35

                ax3.bar([i - width/2 for i in x], df['total_requested'],
                       width, label='Requested', color='lightcoral', alpha=0.8)
                ax3.bar([i + width/2 for i in x], df['total_awarded'],
                       width, label='Awarded', color='lightgreen', alpha=0.8)

                ax3.set_title('Funding Requested vs Awarded by Month')
                ax3.set_xlabel('Month')
                ax3.set_ylabel('Amount ($)')
                ax3.set_xticks(x)
                ax3.set_xticklabels(df['date'], rotation=45)
                ax3.legend()

                # 4. Cumulative Funding Over Time
                df['cumulative_awarded'] = df['total_awarded'].cumsum()
                ax4.fill_between(df['date'], df['cumulative_awarded'], alpha=0.6, color='gold')
                ax4.plot(df['date'], df['cumulative_awarded'], marker='o', linewidth=2, color='orange')
                ax4.set_title('Cumulative Funding Awarded')
                ax4.set_xlabel('Month')
                ax4.set_ylabel('Cumulative Amount ($)')
                ax4.tick_params(axis='x', rotation=45)
                ax4.grid(True, alpha=0.3)

            plt.tight_layout()

            # Save chart
            if output_path:
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Funding trends chart saved to {output_path}")
                return output_path
            else:
                output_path = str(self.data_dir / f"funding_trends_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()
                return output_path

        except Exception as e:
            self.logger.error(f"Error creating funding trends chart: {e}")
            return ""

    def generate_interactive_html_dashboard(
        self,
        metrics: DashboardMetrics,
        organization_name: str = "Organization",
        output_path: Optional[str] = None
    ) -> str:
        """Generate an interactive HTML dashboard."""
        try:
            # Create charts
            success_chart = self.create_success_rate_chart(metrics)
            timeline_chart = self.create_timeline_analytics_chart(metrics)
            funding_chart = self.create_funding_trends_chart(metrics)

            # Convert images to base64 for embedding
            import base64

            def image_to_base64(image_path: str) -> str:
                try:
                    with open(image_path, "rb") as img_file:
                        return base64.b64encode(img_file.read()).decode()
                except:
                    return ""

            success_b64 = image_to_base64(success_chart)
            timeline_b64 = image_to_base64(timeline_chart)
            funding_b64 = image_to_base64(funding_chart)

            # Generate HTML
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Grant Analytics Dashboard - {organization_name}</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    .container {{
                        max-width: 1400px;
                        margin: 0 auto;
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 2.5em;
                        font-weight: 300;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        opacity: 0.9;
                        font-size: 1.1em;
                    }}
                    .metrics-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        padding: 30px;
                        background: #f8f9fa;
                    }}
                    .metric-card {{
                        background: white;
                        padding: 25px;
                        border-radius: 10px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                        text-align: center;
                        border-left: 4px solid #3498db;
                        transition: transform 0.3s ease;
                    }}
                    .metric-card:hover {{
                        transform: translateY(-5px);
                    }}
                    .metric-value {{
                        font-size: 2.5em;
                        font-weight: bold;
                        color: #2c3e50;
                        margin-bottom: 10px;
                    }}
                    .metric-label {{
                        color: #7f8c8d;
                        font-size: 1.1em;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }}
                    .chart-section {{
                        padding: 30px;
                    }}
                    .chart-container {{
                        margin: 30px 0;
                        text-align: center;
                        background: white;
                        border-radius: 10px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .chart-title {{
                        background: #34495e;
                        color: white;
                        padding: 15px;
                        margin: 0;
                        font-size: 1.3em;
                        font-weight: 500;
                    }}
                    .chart-image {{
                        width: 100%;
                        height: auto;
                        display: block;
                    }}
                    .footer {{
                        background: #2c3e50;
                        color: white;
                        text-align: center;
                        padding: 20px;
                    }}
                    .generated-time {{
                        color: #bdc3c7;
                        font-size: 0.9em;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Grant Analytics Dashboard</h1>
                        <p>{organization_name} - Comprehensive Analytics Report</p>
                    </div>

                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{metrics.total_applications}</div>
                            <div class="metric-label">Total Applications</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.success_rate:.1f}%</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${metrics.total_funding_awarded:,.0f}</div>
                            <div class="metric-label">Total Awarded</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.roi_percentage:.1f}%</div>
                            <div class="metric-label">ROI</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics.average_processing_time:.1f}</div>
                            <div class="metric-label">Avg Processing Days</div>
                        </div>
                    </div>

                    <div class="chart-section">
                        <div class="chart-container">
                            <h2 class="chart-title">Success Rate & Performance Analytics</h2>
                            {f'<img src="data:image/png;base64,{success_b64}" class="chart-image" alt="Success Analytics">' if success_b64 else '<p>Chart not available</p>'}
                        </div>

                        <div class="chart-container">
                            <h2 class="chart-title">Application Timeline Analysis</h2>
                            {f'<img src="data:image/png;base64,{timeline_b64}" class="chart-image" alt="Timeline Analytics">' if timeline_b64 else '<p>Chart not available</p>'}
                        </div>

                        <div class="chart-container">
                            <h2 class="chart-title">Funding Trends & Patterns</h2>
                            {f'<img src="data:image/png;base64,{funding_b64}" class="chart-image" alt="Funding Trends">' if funding_b64 else '<p>Chart not available</p>'}
                        </div>
                    </div>

                    <div class="footer">
                        <p>Grant AI Analytics Dashboard</p>
                        <p class="generated-time">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Save HTML file
            if output_path:
                html_path = output_path
            else:
                html_path = str(self.data_dir / f"dashboard_{organization_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.logger.info(f"Interactive dashboard saved to {html_path}")
            return html_path

        except Exception as e:
            self.logger.error(f"Error generating HTML dashboard: {e}")
            return ""

    def export_metrics_to_json(
        self,
        metrics: DashboardMetrics,
        output_path: Optional[str] = None
    ) -> str:
        """Export metrics to JSON format."""
        try:
            metrics_dict = {
                'total_applications': metrics.total_applications,
                'success_rate': metrics.success_rate,
                'total_funding_requested': metrics.total_funding_requested,
                'total_funding_awarded': metrics.total_funding_awarded,
                'average_processing_time': metrics.average_processing_time,
                'roi_percentage': metrics.roi_percentage,
                'applications_by_status': metrics.applications_by_status,
                'funding_trends': metrics.funding_trends,
                'timeline_analytics': metrics.timeline_analytics,
                'generated_at': datetime.now().isoformat()
            }

            if output_path:
                json_path = output_path
            else:
                json_path = str(self.data_dir / f"analytics_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Metrics exported to {json_path}")
            return json_path

        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return ""
