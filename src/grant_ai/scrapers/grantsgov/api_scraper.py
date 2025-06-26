"""
Grants.gov API client and scraper integration for Grant AI project.
"""
import logging
from typing import List

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    ReadTimeout,
    RequestException,
)

from grant_ai.models.grant import EligibilityType, FundingType, Grant, GrantStatus

from ..base import GrantScraper

GRANTS_GOV_API_URL = (
    "https://www.grants.gov/grantsws/rest/opportunities/search/"
)

logger = logging.getLogger(__name__)


class GrantsGovAPIScraper(GrantScraper):
    """Scraper using the grants.gov public API."""

    def search_grants(self, query: str = "", **kwargs) -> List[Grant]:
        """Search for grants using the grants.gov API.
        
        Args:
            query: Search query string
            **kwargs: Additional API parameters
            
        Returns:
            List of Grant objects
            
        Raises:
            RequestException: For various network/API errors
        """
        params = {
            "startRecordNum": 0,
            "oppStatuses": "forecasted,posted,closed",
            "keyword": query,
            "rows": 25,
        }
        params.update(kwargs)
        
        try:
            logger.info(f"Searching grants.gov API with query: '{query}'")
            response = requests.get(
                GRANTS_GOV_API_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
        except ConnectionError as e:
            logger.error(f"Network connection failed: {e}")
            raise RequestException(
                "Unable to connect to grants.gov API. "
                "Please check your internet connection."
            ) from e
            
        except ReadTimeout as e:
            logger.error(f"API request timed out: {e}")
            raise RequestException(
                "grants.gov API request timed out. "
                "The service may be temporarily unavailable."
            ) from e
            
        except HTTPError as e:
            logger.error(f"HTTP error from grants.gov API: {e}")
            if response.status_code == 403:
                raise RequestException(
                    "Access denied by grants.gov API. "
                    "The service may be temporarily restricted."
                ) from e
            elif response.status_code == 429:
                raise RequestException(
                    "Too many requests to grants.gov API. "
                    "Please wait before trying again."
                ) from e
            elif response.status_code >= 500:
                raise RequestException(
                    f"grants.gov API server error ({response.status_code}). "
                    "The service may be temporarily down."
                ) from e
            else:
                raise RequestException(
                    f"grants.gov API returned error {response.status_code}: "
                    f"{response.text[:200]}"
                ) from e
                
        except Exception as e:
            logger.error(f"Unexpected error during API request: {e}")
            raise RequestException(
                f"Unexpected error occurred while accessing grants.gov API: "
                f"{e}"
            ) from e
        
        try:
            data = response.json()
        except ValueError as e:
            logger.error(f"Invalid JSON response from grants.gov API: {e}")
            raise RequestException(
                "grants.gov API returned invalid data. "
                "The service may be experiencing issues."
            ) from e
        
        results = []
        try:
            for item in data.get("oppHits", []):
                grant = Grant(
                    id=(item.get("cfdaList", [""])[0] + "-" +
                        item.get("opportunityId", "")),
                    title=item.get("opportunityTitle", ""),
                    description=item.get("synopsis", ""),
                    funder_name=item.get("agencyName", ""),
                    funder_type="government",
                    funding_type=FundingType.GRANT,
                    amount_min=None,
                    amount_max=None,
                    amount_typical=None,
                    status=(GrantStatus.OPEN
                            if item.get("opportunityStatus", "") == "posted"
                            else GrantStatus.CLOSED),
                    application_deadline=None,
                    eligibility_types=[EligibilityType.NONPROFIT],
                    focus_areas=item.get("cfdaList", []),
                    application_url=item.get("opportunityUrl", None),
                    information_url=item.get("opportunityUrl", None),
                    source="grants.gov",
                    source_url=item.get("opportunityUrl", None),
                )
                results.append(grant)
                
        except Exception as e:
            logger.error(f"Error processing grants.gov API response: {e}")
            raise RequestException(
                f"Error processing grant data from grants.gov API: {e}"
            ) from e
        
        logger.info(
            f"Successfully retrieved {len(results)} grants from grants.gov API"
        )
        return results
