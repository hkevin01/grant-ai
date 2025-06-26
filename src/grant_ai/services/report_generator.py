"""
Reporting system for grant application analytics and visualization.

This module provides comprehensive reporting capabilities including:
- PDF and Excel report generation
- Application analytics and metrics
- Organization performance tracking
- Deadline and submission analysis
- Visual charts and graphs
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from io import BytesIO
import base64

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    )
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  ReportLab not available. PDF generation will be limited.")

from grant_ai.utils.tracking_manager import TrackingManager


@dataclass
class ReportMetrics:
    """Data class for report metrics."""
    total_applications: int
    by_status: Dict[str, int]
    by_organization: Dict[str, int]
    success_rate: float
    average_processing_time: float
    overdue_count: int
    due_soon_count: int
    funding_requested: float
    funding_awarded: float


class ReportGenerator:
    """Main class for generating application tracking reports."""
    
    def __init__(self, tracking_manager: Optional[TrackingManager] = None):
        """Initialize the report generator."""
        self.tracking_manager = tracking_manager or TrackingManager()
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def calculate_metrics(self, organization_id: Optional[str] = None) -> ReportMetrics:
        """Calculate key metrics for reporting."""
        applications = self.tracking_manager.list_tracking(organization_id)
        
        if not applications:
            return ReportMetrics(
                total_applications=0,
                by_status={},
                by_organization={},
                success_rate=0.0,
                average_processing_time=0.0,
                overdue_count=0,
                due_soon_count=0,
                funding_requested=0.0,
                funding_awarded=0.0
            )
        
        # Count by status
        status_counts = {}
        for app in applications:
            status = app.current_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by organization
        org_counts = {}
        for app in applications:
            org = app.organization_id
            org_counts[org] = org_counts.get(org, 0) + 1
        
        # Calculate success rate
        successful_statuses = {'approved', 'awarded'}
        completed_statuses = {'approved', 'awarded', 'rejected', 'declined'}
        
        successful_count = sum(
            status_counts.get(status, 0) for status in successful_statuses
        )
        completed_count = sum(
            status_counts.get(status, 0) for status in completed_statuses
        )
        
        success_rate = (successful_count / completed_count * 100) if completed_count > 0 else 0
        
        # Calculate average processing time
        processing_times = []
        for app in applications:
            if len(app.events) >= 2:
                created_event = min(app.events, key=lambda x: x.created_at)
                latest_event = max(app.events, key=lambda x: x.created_at)
                days_diff = (latest_event.created_at - created_event.created_at).days
                processing_times.append(days_diff)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        # Count overdue and due soon
        overdue_count = 0
        due_soon_count = 0
        
        for app in applications:
            if hasattr(app, 'is_overdue') and app.is_overdue():
                overdue_count += 1
            elif hasattr(app, 'days_until_deadline'):
                days_until = app.days_until_deadline()
                if days_until is not None and 0 <= days_until <= 7:
                    due_soon_count += 1
        
        # Calculate funding amounts
        funding_requested = sum(
            app.funding_amount or 0 for app in applications
        )
        
        funding_awarded = sum(
            app.funding_amount or 0 
            for app in applications 
            if app.current_status.value in successful_statuses
        )
        
        return ReportMetrics(
            total_applications=len(applications),
            by_status=status_counts,
            by_organization=org_counts,
            success_rate=success_rate,
            average_processing_time=avg_processing_time,
            overdue_count=overdue_count,
            due_soon_count=due_soon_count,
            funding_requested=funding_requested,
            funding_awarded=funding_awarded
        )
    
    def generate_charts(self, metrics: ReportMetrics, organization_id: Optional[str] = None) -> Dict[str, str]:
        """Generate charts and return base64 encoded images."""
        charts = {}
        
        # Chart 1: Applications by Status
        if metrics.by_status:
            fig, ax = plt.subplots(figsize=(10, 6))
            statuses = list(metrics.by_status.keys())
            counts = list(metrics.by_status.values())
            
            bars = ax.bar(statuses, counts)
            ax.set_title('Applications by Status', fontsize=16, fontweight='bold')
            ax.set_xlabel('Status')
            ax.set_ylabel('Number of Applications')
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            charts['status_chart'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        
        # Chart 2: Applications by Organization (if multiple orgs)
        if len(metrics.by_organization) > 1:
            fig, ax = plt.subplots(figsize=(10, 6))
            orgs = list(metrics.by_organization.keys())
            counts = list(metrics.by_organization.values())
            
            ax.pie(counts, labels=orgs, autopct='%1.1f%%', startangle=90)
            ax.set_title('Applications by Organization', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            charts['organization_chart'] = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        
        # Chart 3: Success Rate Visualization
        fig, ax = plt.subplots(figsize=(8, 6))
        
        success_data = ['Success Rate', 'Remaining']
        success_values = [metrics.success_rate, 100 - metrics.success_rate]
        colors_success = ['#2ecc71', '#ecf0f1']
        
        wedges, texts, autotexts = ax.pie(success_values, labels=success_data, 
                                         autopct='%1.1f%%', colors=colors_success,
                                         startangle=90)
        ax.set_title('Grant Application Success Rate', fontsize=16, fontweight='bold')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        charts['success_chart'] = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return charts
    
    def generate_excel_report(self, organization_id: Optional[str] = None) -> str:
        """Generate Excel report with multiple sheets."""
        metrics = self.calculate_metrics(organization_id)
        applications = self.tracking_manager.list_tracking(organization_id)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        org_suffix = f"_{organization_id}" if organization_id else "_all_orgs"
        filename = f"grant_report{org_suffix}_{timestamp}.xlsx"
        filepath = self.output_dir / filename
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            
            # Sheet 1: Summary Metrics
            summary_data = {
                'Metric': [
                    'Total Applications',
                    'Success Rate (%)',
                    'Average Processing Time (days)',
                    'Overdue Applications',
                    'Due Soon (7 days)',
                    'Total Funding Requested ($)',
                    'Total Funding Awarded ($)'
                ],
                'Value': [
                    metrics.total_applications,
                    f"{metrics.success_rate:.1f}%",
                    f"{metrics.average_processing_time:.1f}",
                    metrics.overdue_count,
                    metrics.due_soon_count,
                    f"${metrics.funding_requested:,.2f}",
                    f"${metrics.funding_awarded:,.2f}"
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: Applications by Status
            status_data = {
                'Status': list(metrics.by_status.keys()),
                'Count': list(metrics.by_status.values())
            }
            status_df = pd.DataFrame(status_data)
            status_df.to_excel(writer, sheet_name='By Status', index=False)
            
            # Sheet 3: Applications by Organization
            if metrics.by_organization:
                org_data = {
                    'Organization': list(metrics.by_organization.keys()),
                    'Count': list(metrics.by_organization.values())
                }
                org_df = pd.DataFrame(org_data)
                org_df.to_excel(writer, sheet_name='By Organization', index=False)
            
            # Sheet 4: Detailed Application List
            app_details = []
            for app in applications:
                details = {
                    'Application ID': app.application_id,
                    'Organization': app.organization_id,
                    'Grant ID': app.grant_id,
                    'Status': app.current_status.value.replace('_', ' ').title(),
                    'Created Date': app.created_at.strftime('%Y-%m-%d'),
                    'Last Updated': app.updated_at.strftime('%Y-%m-%d'),
                    'Assigned To': app.assigned_to or '',
                    'Funding Amount': app.funding_amount or 0,
                    'Events Count': len(app.events),
                    'Notes Count': len(app.notes),
                    'Reminders Count': len(app.reminders)
                }
                
                if hasattr(app, 'grant_deadline') and app.grant_deadline:
                    details['Deadline'] = app.grant_deadline.strftime('%Y-%m-%d')
                    if hasattr(app, 'days_until_deadline'):
                        days_until = app.days_until_deadline()
                        if days_until is not None:
                            if days_until < 0:
                                details['Days Until Deadline'] = f"Overdue by {abs(days_until)} days"
                            else:
                                details['Days Until Deadline'] = f"{days_until} days"
                        else:
                            details['Days Until Deadline'] = "N/A"
                else:
                    details['Deadline'] = ''
                    details['Days Until Deadline'] = 'N/A'
                
                app_details.append(details)
            
            if app_details:
                details_df = pd.DataFrame(app_details)
                details_df.to_excel(writer, sheet_name='Application Details', index=False)
        
        return str(filepath)
    
    def generate_pdf_report(self, organization_id: Optional[str] = None) -> str:
        """Generate PDF report with charts and metrics."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab is required for PDF generation. Install with: pip install reportlab")
        
        metrics = self.calculate_metrics(organization_id)
        charts = self.generate_charts(metrics, organization_id)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        org_suffix = f"_{organization_id}" if organization_id else "_all_orgs"
        filename = f"grant_report{org_suffix}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        title_text = "Grant Application Analytics Report"
        if organization_id:
            title_text += f" - {organization_id}"
        
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 20))
        
        # Report date
        date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        summary_text = f"""
        This report provides a comprehensive analysis of grant application activities.
        The analysis covers {metrics.total_applications} applications with a success rate of 
        {metrics.success_rate:.1f}%. The average processing time is {metrics.average_processing_time:.1f} days.
        Currently, {metrics.overdue_count} applications are overdue and {metrics.due_soon_count} 
        applications are due within the next 7 days.
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Key Metrics Table
        story.append(Paragraph("Key Performance Metrics", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Applications', str(metrics.total_applications)],
            ['Success Rate', f"{metrics.success_rate:.1f}%"],
            ['Average Processing Time', f"{metrics.average_processing_time:.1f} days"],
            ['Overdue Applications', str(metrics.overdue_count)],
            ['Due Soon (7 days)', str(metrics.due_soon_count)],
            ['Total Funding Requested', f"${metrics.funding_requested:,.2f}"],
            ['Total Funding Awarded', f"${metrics.funding_awarded:,.2f}"]
        ]
        
        metrics_table = Table(metrics_data)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 30))
        
        # Add charts if available
        if 'status_chart' in charts:
            story.append(Paragraph("Applications by Status", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Decode base64 image
            image_data = base64.b64decode(charts['status_chart'])
            image_buffer = BytesIO(image_data)
            
            # Add image to PDF
            img = Image(image_buffer, width=6*inch, height=3.6*inch)
            story.append(img)
            story.append(Spacer(1, 20))
        
        # Status breakdown table
        if metrics.by_status:
            story.append(Paragraph("Application Status Breakdown", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            status_data = [['Status', 'Count', 'Percentage']]
            total = sum(metrics.by_status.values())
            
            for status, count in metrics.by_status.items():
                percentage = (count / total * 100) if total > 0 else 0
                status_display = status.replace('_', ' ').title()
                status_data.append([status_display, str(count), f"{percentage:.1f}%"])
            
            status_table = Table(status_data)
            status_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(status_table)
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def generate_html_report(self, organization_id: Optional[str] = None) -> str:
        """Generate HTML report with interactive elements."""
        metrics = self.calculate_metrics(organization_id)
        charts = self.generate_charts(metrics, organization_id)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        org_suffix = f"_{organization_id}" if organization_id else "_all_orgs"
        filename = f"grant_report{org_suffix}_{timestamp}.html"
        filepath = self.output_dir / filename
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Grant Application Analytics Report</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #34495e;
                    border-left: 4px solid #3498db;
                    padding-left: 15px;
                    margin-top: 30px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .metric-value {{
                    font-size: 2em;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    opacity: 0.9;
                }}
                .chart-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .chart-container img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Grant Application Analytics Report</h1>
                {f"<p style='text-align: center; font-size: 1.2em; color: #7f8c8d;'>Organization: {organization_id}</p>" if organization_id else ""}
                <p style="text-align: center; color: #7f8c8d;">
                    Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
                
                <h2>📊 Key Performance Metrics</h2>
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
                        <div class="metric-value">{metrics.average_processing_time:.1f}</div>
                        <div class="metric-label">Avg Processing Days</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{metrics.overdue_count}</div>
                        <div class="metric-label">Overdue Applications</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${metrics.funding_requested:,.0f}</div>
                        <div class="metric-label">Total Requested</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${metrics.funding_awarded:,.0f}</div>
                        <div class="metric-label">Total Awarded</div>
                    </div>
                </div>
        """
        
        # Add charts
        if 'status_chart' in charts:
            html_content += f"""
                <h2>📈 Applications by Status</h2>
                <div class="chart-container">
                    <img src="data:image/png;base64,{charts['status_chart']}" alt="Applications by Status Chart">
                </div>
            """
        
        if 'organization_chart' in charts:
            html_content += f"""
                <h2>🏢 Applications by Organization</h2>
                <div class="chart-container">
                    <img src="data:image/png;base64,{charts['organization_chart']}" alt="Applications by Organization Chart">
                </div>
            """
        
        if 'success_chart' in charts:
            html_content += f"""
                <h2>🎯 Success Rate Analysis</h2>
                <div class="chart-container">
                    <img src="data:image/png;base64,{charts['success_chart']}" alt="Success Rate Chart">
                </div>
            """
        
        # Add status breakdown table
        if metrics.by_status:
            html_content += """
                <h2>📋 Status Breakdown</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            total = sum(metrics.by_status.values())
            for status, count in metrics.by_status.items():
                percentage = (count / total * 100) if total > 0 else 0
                status_display = status.replace('_', ' ').title()
                html_content += f"""
                        <tr>
                            <td>{status_display}</td>
                            <td>{count}</td>
                            <td>{percentage:.1f}%</td>
                        </tr>
                """
            
            html_content += """
                    </tbody>
                </table>
            """
        
        # Close HTML
        html_content += f"""
                <div class="footer">
                    <p>Report generated by Grant AI Application Tracking System</p>
                    <p>For more information, contact your system administrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)


def main():
    """Demo function for testing report generation."""
    print("🚀 Grant AI Reporting System Demo")
    print("=" * 50)
    
    # Initialize report generator
    generator = ReportGenerator()
    
    # Generate reports
    print("\n📊 Generating Excel Report...")
    excel_path = generator.generate_excel_report()
    print(f"✅ Excel report saved: {excel_path}")
    
    print("\n🌐 Generating HTML Report...")
    html_path = generator.generate_html_report()
    print(f"✅ HTML report saved: {html_path}")
    
    if REPORTLAB_AVAILABLE:
        print("\n📄 Generating PDF Report...")
        pdf_path = generator.generate_pdf_report()
        print(f"✅ PDF report saved: {pdf_path}")
    else:
        print("\n⚠️  PDF generation skipped (ReportLab not installed)")
    
    # Generate organization-specific report
    print("\n🏢 Generating CODA-specific report...")
    coda_excel = generator.generate_excel_report("CODA")
    print(f"✅ CODA Excel report saved: {coda_excel}")
    
    print("\n🎉 Report generation complete!")
    print("📁 All reports saved in: reports/")


if __name__ == "__main__":
    main()
