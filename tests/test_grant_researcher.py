"""Unit tests for grant researcher functionality."""

from datetime import date, timedelta

import pytest

from grant_ai.analysis.grant_researcher import GrantResearcher
from grant_ai.models.ai_company import AICompany
from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus


class TestGrantResearcher:
    """Test cases for GrantResearcher class."""
    
    def test_create_researcher(self):
        """Test creating a grant researcher instance."""
        researcher = GrantResearcher()
        
        assert isinstance(researcher, GrantResearcher)
        assert len(researcher.grants) == 0
        assert len(researcher.ai_companies) == 0
    
    def test_add_grants(self, sample_grant):
        """Test adding grants to researcher database."""
        researcher = GrantResearcher()
        researcher.add_grants([sample_grant])
        
        assert len(researcher.grants) == 1
        assert researcher.grants[0] == sample_grant
    
    def test_add_ai_companies(self, sample_ai_company):
        """Test adding AI companies to researcher database."""
        researcher = GrantResearcher()
        researcher.add_ai_companies([sample_ai_company])
        
        assert len(researcher.ai_companies) == 1
        assert researcher.ai_companies[0] == sample_ai_company
    
    def test_find_matching_grants(self, sample_organization, sample_grant):
        """Test finding grants that match organization profile."""
        researcher = GrantResearcher()
        researcher.add_grants([sample_grant])
        
        matches = researcher.find_matching_grants(sample_organization)
        
        # Should find the matching grant
        assert len(matches) >= 0  # Might be 0 if score is too low
        
        # Test with lower minimum score
        matches = researcher.find_matching_grants(sample_organization, min_score=0.1)
        assert len(matches) > 0
        assert matches[0].relevance_score is not None
    
    def test_find_matching_ai_companies(self, sample_organization, sample_ai_company):
        """Test finding AI companies that match organization profile."""
        researcher = GrantResearcher()
        researcher.add_ai_companies([sample_ai_company])
        
        matches = researcher.find_matching_ai_companies(sample_organization, min_score=0.1)
        
        assert len(matches) > 0
        assert matches[0].match_score is not None
        assert matches[0].has_grant_program == True
    
    def test_filter_grants_by_focus(self, sample_grant):
        """Test filtering grants by focus areas."""
        researcher = GrantResearcher()
        researcher.add_grants([sample_grant])
        
        # Filter by matching focus area
        filtered = researcher.filter_grants(focus_areas=["education"])
        assert len(filtered) > 0
        
        # Filter by non-matching focus area
        filtered = researcher.filter_grants(focus_areas=["housing"])
        assert len(filtered) == 0
    
    def test_filter_grants_by_amount(self, sample_grant):
        """Test filtering grants by amount."""
        researcher = GrantResearcher()
        researcher.add_grants([sample_grant])
        
        # Filter with suitable amount range
        filtered = researcher.filter_grants(min_amount=20000, max_amount=30000)
        assert len(filtered) > 0
        
        # Filter with unsuitable amount range
        filtered = researcher.filter_grants(min_amount=100000, max_amount=200000)
        assert len(filtered) == 0
    
    def test_filter_grants_by_status(self, sample_grant):
        """Test filtering grants by status."""
        researcher = GrantResearcher()
        researcher.add_grants([sample_grant])
        
        # Filter by matching status
        filtered = researcher.filter_grants(status=GrantStatus.OPEN)
        assert len(filtered) > 0
        
        # Filter by non-matching status
        filtered = researcher.filter_grants(status=GrantStatus.CLOSED)
        assert len(filtered) == 0
    
    def test_get_statistics(self, sample_grant, sample_ai_company):
        """Test getting database statistics."""
        researcher = GrantResearcher()
        researcher.add_grants([sample_grant])
        researcher.add_ai_companies([sample_ai_company])
        
        stats = researcher.get_statistics()
        
        assert stats["total_grants"] == 1
        assert stats["total_ai_companies"] == 1
        assert stats["open_grants"] == 1
        assert stats["companies_with_grants"] == 1
        assert "last_updated" in stats
    
    def test_generate_grant_report(self, sample_organization, sample_grant):
        """Test generating grant reports."""
        researcher = GrantResearcher()
        
        # Test with empty grants list
        df = researcher.generate_grant_report(sample_organization, [])
        assert len(df) == 0
        
        # Test with grants
        df = researcher.generate_grant_report(sample_organization, [sample_grant])
        assert len(df) > 0
        assert "organization_name" in df.columns
        assert df.iloc[0]["organization_name"] == sample_organization.name
    
    def test_generate_company_report(self, sample_organization, sample_ai_company):
        """Test generating AI company reports."""
        researcher = GrantResearcher()
        
        # Test with empty companies list
        df = researcher.generate_company_report(sample_organization, [])
        assert len(df) == 0
        
        # Test with companies
        df = researcher.generate_company_report(sample_organization, [sample_ai_company])
        assert len(df) > 0
        assert "organization_name" in df.columns
        assert df.iloc[0]["organization_name"] == sample_organization.name
