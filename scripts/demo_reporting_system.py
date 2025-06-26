#!/usr/bin/env python3
"""
Comprehensive demonstration of the Grant AI Reporting System.

This script showcases the complete reporting functionality including:
- Excel, HTML, and PDF report generation
- Organization-specific and global reporting
- Key metrics calculation and visualization
- Integration with application tracking data
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """Run the comprehensive reporting demonstration."""
    print("🚀 Grant AI Reporting System - Comprehensive Demo")
    print("=" * 60)
    
    try:
        from grant_ai.services.report_generator import ReportGenerator
        from grant_ai.utils.tracking_manager import TrackingManager

        # Initialize components
        generator = ReportGenerator()
        
        print("\n📊 STEP 1: Analyzing Current Data")
        print("-" * 40)
        
        # Get overall metrics
        all_metrics = generator.calculate_metrics()
        print(f"📈 Total Applications: {all_metrics.total_applications}")
        print(f"🎯 Success Rate: {all_metrics.success_rate:.1f}%")
        print(f"⚠️ Overdue Applications: {all_metrics.overdue_count}")
        print(f"💰 Total Funding Requested: "
              f"${all_metrics.funding_requested:,.2f}")
        print(f"🏆 Total Funding Awarded: "
              f"${all_metrics.funding_awarded:,.2f}")
        
        # Show status breakdown
        print("\n📋 Application Status Breakdown:")
        for status, count in all_metrics.by_status.items():
            status_display = status.replace('_', ' ').title()
            percentage = (count / all_metrics.total_applications * 100) if all_metrics.total_applications > 0 else 0
            print(f"   • {status_display}: {count} ({percentage:.1f}%)")
        
        # Show organization breakdown
        if len(all_metrics.by_organization) > 1:
            print("\n🏢 Organization Breakdown:")
            for org, count in all_metrics.by_organization.items():
                percentage = (count / all_metrics.total_applications * 100) if all_metrics.total_applications > 0 else 0
                print(f"   • {org}: {count} ({percentage:.1f}%)")
        
        print("\n📊 STEP 2: Generating Comprehensive Reports")
        print("-" * 50)
        
        # Generate global reports
        print("\n🌐 Generating Global Reports...")
        
        # Excel report
        print("   📊 Excel Report...")
        excel_path = generator.generate_excel_report()
        print(f"   ✅ Saved: {excel_path}")
        
        # HTML report
        print("   🌐 HTML Report...")
        html_path = generator.generate_html_report()
        print(f"   ✅ Saved: {html_path}")
        
        # PDF report
        print("   📄 PDF Report...")
        try:
            pdf_path = generator.generate_pdf_report()
            print(f"   ✅ Saved: {pdf_path}")
        except ImportError as e:
            print(f"   ⚠️ PDF generation failed: {e}")
        
        print("\n🏢 STEP 3: Generating Organization-Specific Reports")
        print("-" * 55)
        
        # Generate reports for each organization
        organizations = list(all_metrics.by_organization.keys())
        
        for org in organizations[:2]:  # Limit to first 2 organizations for demo
            print(f"\n📋 Generating reports for {org}...")
            
            # Get organization-specific metrics
            org_metrics = generator.calculate_metrics(org)
            print(f"   📈 Applications: {org_metrics.total_applications}")
            print(f"   🎯 Success Rate: {org_metrics.success_rate:.1f}%")
            
            # Generate organization reports
            org_excel = generator.generate_excel_report(org)
            print(f"   ✅ Excel: {Path(org_excel).name}")
            
            org_html = generator.generate_html_report(org)
            print(f"   ✅ HTML: {Path(org_html).name}")
        
        print("\n📈 STEP 4: Analyzing Report Contents")
        print("-" * 40)
        
        # Demonstrate chart generation
        print("\n🎨 Testing Chart Generation...")
        charts = generator.generate_charts(all_metrics)
        
        if charts:
            print(f"   ✅ Generated {len(charts)} charts:")
            for chart_name in charts.keys():
                print(f"      • {chart_name}")
        else:
            print("   ⚠️ No charts generated (insufficient data)")
        
        print("\n📁 STEP 5: Report Directory Summary")
        print("-" * 40)
        
        # List all generated reports
        reports_dir = Path("reports")
        if reports_dir.exists():
            report_files = list(reports_dir.glob("*"))
            report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            print(f"\n📂 Reports Directory: {reports_dir.absolute()}")
            print(f"📄 Total Report Files: {len(report_files)}")
            
            print("\n🕒 Recent Reports (latest 5):")
            for report_file in report_files[:5]:
                file_size = report_file.stat().st_size
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024*1024):.1f} MB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.1f} KB"
                else:
                    size_str = f"{file_size} bytes"
                
                print(f"   📄 {report_file.name} ({size_str})")
        
        print("\n🎯 STEP 6: Reporting Capabilities Summary")
        print("-" * 45)
        
        print("\n✅ IMPLEMENTED FEATURES:")
        print("   📊 Excel Reports with Multiple Sheets")
        print("      • Summary metrics and KPIs")
        print("      • Application details and status breakdown")
        print("      • Organization-specific analysis")
        print()
        print("   🌐 HTML Reports with Interactive Elements")
        print("      • Responsive design with modern styling")
        print("      • Embedded charts and visualizations")
        print("      • Color-coded metrics and status indicators")
        print()
        print("   📄 PDF Reports with Professional Layout")
        print("      • Executive summary and key metrics")
        print("      • Charts and tables with proper formatting")
        print("      • Organization branding and styling")
        print()
        print("   📈 Advanced Analytics and Metrics")
        print("      • Success rate calculation and trending")
        print("      • Processing time analysis")
        print("      • Deadline monitoring and alerts")
        print("      • Funding analysis and ROI tracking")
        print()
        print("   🎨 Data Visualization")
        print("      • Status distribution charts")
        print("      • Organization comparison graphs")
        print("      • Success rate visualizations")
        print("      • Timeline and trend analysis")
        
        print("\n🚀 INTEGRATION FEATURES:")
        print("   🔗 Seamless PyQt GUI Integration")
        print("   📊 Real-time Metrics Updates")
        print("   🏢 Multi-Organization Support")
        print("   📱 Responsive and User-Friendly Interface")
        print("   🔄 Automatic Data Refresh")
        
        print("\n💡 USAGE EXAMPLES:")
        print("   • Monthly board reports with success metrics")
        print("   • Grant application pipeline analysis")
        print("   • Deadline monitoring and risk assessment")
        print("   • Organization performance comparison")
        print("   • Funding opportunity ROI analysis")
        
        print("\n🎉 REPORTING SYSTEM DEMO COMPLETE!")
        print("=" * 50)
        print("\nThe Grant AI Reporting System provides:")
        print("✅ Comprehensive analytics and metrics")
        print("✅ Multiple export formats (Excel, HTML, PDF)")
        print("✅ Professional-quality visualizations")
        print("✅ Organization-specific and global reporting")
        print("✅ Real-time data integration")
        print("✅ User-friendly GUI interface")
        
        print(f"\n📁 All reports available in: {reports_dir.absolute()}")
        print("💡 Open HTML reports in your browser for best experience!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("💡 Install required packages with:")
        print("   pip install pandas matplotlib seaborn reportlab openpyxl")
        return False
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
