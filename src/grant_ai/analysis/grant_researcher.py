"""Grant research and matching functionality."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from ..models.ai_company import AICompany
from ..models.grant import Grant
from ..models.organization import OrganizationProfile

logger = logging.getLogger(__name__)


class GrantResearcher:
    """Main class for researching and matching grants to organizations."""

    def __init__(self):
        """Initialize the grant researcher."""
        self.grants: list[Grant] = []
        self.ai_companies: list[AICompany] = []
        self.logger = logger

    def add_grants(self, grants: list[Grant]) -> None:
        """Add grants to the research database."""
        self.grants.extend(grants)
        self.logger.info(f"Added {len(grants)} grants to database")

    def add_ai_companies(self, companies: list[AICompany]) -> None:
        """Add AI companies to the research database."""
        self.ai_companies.extend(companies)
        self.logger.info(f"Added {len(companies)} AI companies to database")

    def find_matching_grants(
        self, organization: OrganizationProfile, min_score: float = 0.3, limit: Optional[int] = None
    ) -> list[Grant]:
        """Find grants that match an organization's profile."""
        org_keywords = organization.get_focus_keywords()
        min_amount, max_amount = organization.preferred_grant_size

        matching_grants = []

        for grant in self.grants:
            # Calculate relevance score
            score = grant.calculate_relevance_score(org_keywords, organization.annual_budget)

            # Apply filters
            if score < min_score:
                continue

            if not grant.is_currently_open():
                continue

            if not grant.is_amount_suitable(min_amount, max_amount):
                continue

            # Add match reasons
            grant.match_reasons = []
            if grant.matches_focus_areas(org_keywords):
                grant.match_reasons.append("Focus areas match organization needs")
            if grant.is_amount_suitable(min_amount, max_amount):
                grant.match_reasons.append("Grant amount suitable for organization")
            if grant.is_currently_open():
                grant.match_reasons.append("Currently accepting applications")

            matching_grants.append(grant)

        # Sort by relevance score
        matching_grants.sort(key=lambda g: g.relevance_score or 0, reverse=True)

        if limit:
            matching_grants = matching_grants[:limit]

        self.logger.info(f"Found {len(matching_grants)} matching grants for {organization.name}")

        return matching_grants

    def find_matching_ai_companies(
        self, organization: OrganizationProfile, min_score: float = 0.4, limit: Optional[int] = None
    ) -> list[AICompany]:
        """Find AI companies with grant programs matching organization needs."""
        org_keywords = organization.get_focus_keywords()

        matching_companies = []

        for company in self.ai_companies:
            # Only consider companies with grant programs
            if not company.has_grant_program:
                continue

            # Calculate match score
            score = company.calculate_match_score(
                org_keywords, organization.annual_budget, "nonprofit"
            )

            if score >= min_score:
                matching_companies.append(company)

        # Sort by match score
        matching_companies.sort(key=lambda c: c.match_score or 0, reverse=True)

        if limit:
            matching_companies = matching_companies[:limit]

        self.logger.info(
            f"Found {len(matching_companies)} matching AI companies for {organization.name}"
        )

        return matching_companies

    def generate_grant_report(
        self,
        organization: OrganizationProfile,
        grants: list[Grant],
        output_file: Optional[str] = None,
    ) -> pd.DataFrame:
        """Generate a detailed report of matching grants."""
        if not grants:
            self.logger.warning("No grants provided for report generation")
            return pd.DataFrame()

        # Convert grants to DataFrame
        grant_data = [grant.to_dict() for grant in grants]
        df = pd.DataFrame(grant_data)

        # Add organization-specific information
        df["organization_name"] = organization.name
        df["report_generated"] = datetime.now().isoformat()

        # Sort by relevance score
        df = df.sort_values("relevance_score", ascending=False)

        # Save to file if specified
        if output_file:
            if output_file.endswith(".xlsx"):
                df.to_excel(output_file, index=False)
            elif output_file.endswith(".csv"):
                df.to_csv(output_file, index=False)
            else:
                raise ValueError("Output file must be .xlsx or .csv format")

            self.logger.info(f"Grant report saved to {output_file}")

        return df

    def generate_company_report(
        self,
        organization: OrganizationProfile,
        companies: list[AICompany],
        output_file: Optional[str] = None,
    ) -> pd.DataFrame:
        """Generate a detailed report of matching AI companies."""
        if not companies:
            self.logger.warning("No companies provided for report generation")
            return pd.DataFrame()

        # Convert companies to DataFrame
        company_data = [company.to_dict() for company in companies]
        df = pd.DataFrame(company_data)

        # Add organization-specific information
        df["organization_name"] = organization.name
        df["report_generated"] = datetime.now().isoformat()

        # Sort by match score
        df = df.sort_values("match_score", ascending=False)

        # Save to file if specified
        if output_file:
            if output_file.endswith(".xlsx"):
                df.to_excel(output_file, index=False)
            elif output_file.endswith(".csv"):
                df.to_csv(output_file, index=False)
            else:
                raise ValueError("Output file must be .xlsx or .csv format")

            self.logger.info(f"AI company report saved to {output_file}")

        return df

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the current database."""
        stats = {
            "total_grants": len(self.grants),
            "total_ai_companies": len(self.ai_companies),
            "open_grants": len([g for g in self.grants if g.is_currently_open()]),
            "companies_with_grants": len([c for c in self.ai_companies if c.has_grant_program]),
            "average_grant_amount": 0,
            "last_updated": datetime.now().isoformat(),
        }

        # Calculate average grant amount
        amounts = [g.amount_typical for g in self.grants if g.amount_typical]
        if amounts:
            stats["average_grant_amount"] = sum(amounts) / len(amounts)

        return stats

    def filter_grants(
        self,
        focus_areas: Optional[list[str]] = None,
        min_amount: Optional[int] = None,
        max_amount: Optional[int] = None,
        status: Optional[str] = None,
        funder_type: Optional[str] = None,
    ) -> list[Grant]:
        """Filter grants based on various criteria."""
        filtered_grants = self.grants.copy()

        if focus_areas:
            focus_keywords = [area.lower() for area in focus_areas]
            filtered_grants = [
                grant for grant in filtered_grants if grant.matches_focus_areas(focus_keywords)
            ]

        if min_amount:
            filtered_grants = [
                grant
                for grant in filtered_grants
                if not grant.amount_max or grant.amount_max >= min_amount
            ]

        if max_amount:
            filtered_grants = [
                grant
                for grant in filtered_grants
                if not grant.amount_min or grant.amount_min <= max_amount
            ]

        if status:
            filtered_grants = [grant for grant in filtered_grants if grant.status == status]

        if funder_type:
            filtered_grants = [
                grant
                for grant in filtered_grants
                if grant.funder_type.lower() == funder_type.lower()
            ]

        return filtered_grants

    def grant_success_trend(
        self, organization: OrganizationProfile, years: int = 5
    ) -> pd.DataFrame:
        """Analyze grant success trends for an organization over the past N years."""
        now = datetime.now().year
        history = [g for g in organization.past_grants if g.year >= now - years]
        if not history:
            self.logger.warning("No grant history available for trend analysis")
            return pd.DataFrame()
        df = pd.DataFrame([g.dict() for g in history])
        trend = (
            df.groupby(["year", "status"]).agg({"amount": "sum", "grant_id": "count"}).reset_index()
        )
        trend.rename(columns={"grant_id": "applications"}, inplace=True)
        return trend

    def predictive_grant_match(self, organization: OrganizationProfile) -> list[Grant]:
        """Predict grants most likely to be awarded based on historical data and profile."""
        # Placeholder: Use simple scoring for demonstration
        matches = self.find_matching_grants(organization, min_score=0.5)
        # Rank by historical win rate if available
        win_ids = {g.grant_id for g in organization.past_grants if g.status == "won"}
        for grant in matches:
            grant.predicted_success = 1.0 if grant.grant_id in win_ids else 0.5
        matches.sort(key=lambda g: getattr(g, "predicted_success", 0), reverse=True)
        return matches

    def visualize_grant_trends(
        self, trend_df: pd.DataFrame, output_file: Optional[str] = None
    ) -> None:
        """Generate and save a chart of grant success trends."""
        import matplotlib.pyplot as plt

        if trend_df.empty:
            self.logger.warning("No trend data to visualize")
            return
        pivot = trend_df.pivot(index="year", columns="status", values="applications").fillna(0)
        pivot.plot(kind="bar", stacked=True)
        plt.title("Grant Applications by Year and Status")
        plt.xlabel("Year")
        plt.ylabel("Applications")
        plt.tight_layout()
        if output_file:
            plt.savefig(output_file)
            self.logger.info(f"Grant trend chart saved to {output_file}")
        else:
            plt.show()
