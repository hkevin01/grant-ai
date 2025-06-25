"""
Unit tests for ReportGenerator.
"""
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from grant_ai.models.application_tracking import ApplicationStatus, ApplicationTracking
from grant_ai.models.organization import FocusArea, OrganizationProfile, ProgramType
from grant_ai.utils.reporting import ReportGenerator


class TestReportGenerator:
    """Test cases for ReportGenerator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def report_generator(self, temp_dir):
        """Create a ReportGenerator instance."""
        return ReportGenerator()
    
    @pytest.fixture
    def sample_tracking(self):
        """Create sample tracking data for testing."""
        return [
            ApplicationTracking(
                id="tracking_1",
                application_id="app_1",
                organization_id="org_1",
                grant_id="grant_1",
                current_status=ApplicationStatus.APPROVED,
                assigned_to="test_user",
                grant_deadline=datetime.now() - timedelta(days=20),
                award_date=datetime.now() - timedelta(days=10),
                funding_amount=50000,
            ),
            ApplicationTracking(
                id="tracking_2",
                application_id="app_2",
                organization_id="org_1",
                grant_id="grant_2",
                current_status=ApplicationStatus.REJECTED,
                assigned_to="test_user",
                grant_deadline=datetime.now() - timedelta(days=50),
                award_date=datetime.now() - timedelta(days=40),
                funding_amount=None,
            ),
            ApplicationTracking(
                id="tracking_3",
                application_id="app_3",
                organization_id="org_2",
                grant_id="grant_3",
                current_status=ApplicationStatus.DRAFT,
                assigned_to="test_user",
                grant_deadline=datetime.now() + timedelta(days=20),
                award_date=datetime.now() + timedelta(days=30),
                funding_amount=None,
            )
        ]
    
    @pytest.fixture
    def sample_profiles(self):
        """Create sample organization profiles for testing."""
        return [
            OrganizationProfile(
                name="Test Org 1",
                description="First test organization",
                focus_areas=[FocusArea.EDUCATION],
                program_types=[ProgramType.AFTER_SCHOOL],
                target_demographics=["youth"],
                annual_budget=100000,
                location="City 1",
                contact_name="Contact 1",
                contact_email="contact1@example.com",
                website="https://org1.com",
                ein="12-3456789",
                founded_year=2020,
                preferred_grant_size=(10000, 50000),
                contact_phone="555-1111"
            ),
            OrganizationProfile(
                name="Test Org 2",
                description="Second test organization",
                focus_areas=[FocusArea.MUSIC_EDUCATION],
                program_types=[ProgramType.EDUCATIONAL_WORKSHOPS],
                target_demographics=["children"],
                annual_budget=75000,
                location="City 2",
                contact_name="Contact 2",
                contact_email="contact2@example.com",
                website="https://org2.com",
                ein="98-7654321",
                founded_year=2019,
                preferred_grant_size=(5000, 25000),
                contact_phone="555-2222"
            )
        ]
    
    def test_generate_organization_report(self, report_generator, sample_tracking):
        """Test generating organization report."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate report
        report = report_generator.generate_organization_report("org_1")
        
        assert report is not None
        assert report["organization_id"] == "org_1"
        assert "summary" in report
        assert "metrics" in report
        assert "applications" in report
        assert len(report["applications"]) == 2  # org_1 has 2 applications
    
    def test_generate_status_report(self, report_generator, sample_tracking):
        """Test generating status report."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate status report
        report = report_generator.generate_status_report()
        
        assert report is not None
        assert report["report_type"] == "status_report"
        assert "summary" in report
        assert "by_organization" in report
        assert "applications" in report
        assert len(report["applications"]) == 3  # total applications
    
    def test_generate_status_report_with_filter(self, report_generator, sample_tracking):
        """Test generating status report with status filter."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate status report for draft applications
        report = report_generator.generate_status_report(ApplicationStatus.DRAFT)
        
        assert report is not None
        assert report["status_filter"] == "draft"
        assert len(report["applications"]) == 1  # only 1 draft application
    
    def test_generate_timeline_report(self, report_generator, sample_tracking):
        """Test generating timeline report."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate timeline report
        report = report_generator.generate_timeline_report(days=30)
        
        assert report is not None
        assert report["report_type"] == "timeline_report"
        assert "summary" in report
        assert "events_by_date" in report
        assert "all_events" in report
    
    def test_generate_performance_report(self, report_generator, sample_tracking):
        """Test generating performance report."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate performance report
        report = report_generator.generate_performance_report()
        
        assert report is not None
        assert "metrics" in report
        assert "status_distribution" in report
        assert "completion_rates_by_status" in report
        assert "top_organizations" in report
    
    def test_export_report_json(self, report_generator, sample_tracking):
        """Test exporting report to JSON format."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate and export report
        report_data = report_generator.generate_organization_report("org_1")
        export_data = report_generator.export_report(report_data, "json")
        
        assert export_data is not None
        assert "org_1" in export_data
    
    def test_export_report_text(self, report_generator, sample_tracking):
        """Test exporting report to text format."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate and export report
        report_data = report_generator.generate_organization_report("org_1")
        export_data = report_generator.export_report(report_data, "text")
        
        assert export_data is not None
        assert "GRANT AI REPORT" in export_data
        assert "org_1" in export_data
    
    def test_export_report_csv(self, report_generator, sample_tracking):
        """Test exporting report to CSV format."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate and export report
        report_data = report_generator.generate_organization_report("org_1")
        
        # CSV format is not supported, should raise ValueError
        with pytest.raises(ValueError, match="Unsupported format: csv"):
            report_generator.export_report(report_data, "csv")
    
    def test_export_report_invalid_format(self, report_generator, sample_tracking):
        """Test exporting report with invalid format."""
        # Save sample data
        for tracking in sample_tracking:
            report_generator.tracking_manager.save_tracking(tracking)
        
        # Generate and export report
        report_data = report_generator.generate_organization_report("org_1")
        
        # Invalid format should raise ValueError
        with pytest.raises(ValueError, match="Unsupported format: invalid"):
            report_generator.export_report(report_data, "invalid") 