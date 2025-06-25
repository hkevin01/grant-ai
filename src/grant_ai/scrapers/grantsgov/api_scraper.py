"""
Grants.gov API client and scraper integration for Grant AI project.
"""
from typing import List

import requests

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus

from .base import GrantScraper

GRANTS_GOV_API_URL = "https://www.grants.gov/grantsws/rest/opportunities/search/"

class GrantsGovAPIScraper(GrantScraper):
    """Scraper using the grants.gov public API."""

    def search_grants(self, query: str = "", **kwargs) -> List[Grant]:
        params = {
            "startRecordNum": 0,
            "oppStatuses": "forecasted,posted,closed",
            "keyword": query,
            "rows": 25,
        }
        params.update(kwargs)
        response = requests.get(GRANTS_GOV_API_URL, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        results = []
        for item in data.get("oppHits", []):
            grant = Grant(
                id=item.get("cfdaList", [""])[0] + "-" + item.get("opportunityId", ""),
                title=item.get("opportunityTitle", ""),
                description=item.get("synopsis", ""),
                funder_name=item.get("agencyName", ""),
                funder_type="government",
                funding_type=FundingType.GRANT,
                amount_min=None,
                amount_max=None,
                amount_typical=None,
                status=GrantStatus.OPEN if item.get("opportunityStatus", "") == "posted" else GrantStatus.CLOSED,
                application_deadline=None,
                eligibility_types=[EligibilityType.NONPROFIT],
                focus_areas=item.get("cfdaList", []),
                application_url=item.get("opportunityUrl", None),
                information_url=item.get("opportunityUrl", None),
                source="grants.gov",
                source_url=item.get("opportunityUrl", None),
            )
            results.append(grant)
        return results
