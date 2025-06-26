#!/usr/bin/env python3
"""
Test script for the reporting functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_reporting():
    """Test the reporting system."""
    try:
        from grant_ai.services.report_generator import ReportGenerator
        
        print("🚀 Testing Grant AI Reporting System")
        print("=" * 50)
        
        # Initialize report generator
        generator = ReportGenerator()
        
        # Calculate metrics
        print("\n📊 Calculating metrics...")
        metrics = generator.calculate_metrics()
        
        print(f"✅ Found {metrics.total_applications} applications")
        print(f"   Success Rate: {metrics.success_rate:.1f}%")
        print(f"   Overdue: {metrics.overdue_count}")
        print(f"   Due Soon: {metrics.due_soon_count}")
        
        if metrics.total_applications > 0:
            # Generate Excel report
            print("\n📊 Generating Excel report...")
            excel_path = generator.generate_excel_report()
            print(f"✅ Excel report saved: {excel_path}")
            
            # Generate HTML report
            print("\n🌐 Generating HTML report...")
            html_path = generator.generate_html_report()
            print(f"✅ HTML report saved: {html_path}")
            
            # Test PDF generation
            try:
                print("\n📄 Testing PDF generation...")
                pdf_path = generator.generate_pdf_report()
                print(f"✅ PDF report saved: {pdf_path}")
            except (ImportError, OSError) as e:
                print(f"⚠️  PDF generation failed: {e}")
            
            # Generate organization-specific report
            print("\n🏢 Testing organization-specific reporting...")
            coda_excel = generator.generate_excel_report("CODA")
            print(f"✅ CODA report saved: {coda_excel}")
            
        else:
            print("⚠️  No applications found. Create some test applications "
                  "first.")
            print("💡 Run: python scripts/demo_application_tracking.py")
        
        print("\n🎉 Reporting test complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
        return False
    except (RuntimeError, ValueError, OSError) as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_reporting()
    sys.exit(0 if success else 1)
