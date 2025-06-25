"""
Test for Grants.gov API scraper.
"""
import pytest

from grant_ai.scrapers.grantsgov.api_scraper import GrantsGovAPIScraper


def test_grantsgov_api_scraper(monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return {
                "oppHits": [
                    {
                        "cfdaList": ["10.123"],
                        "opportunityId": "TEST123",
                        "opportunityTitle": "Test Grant",
                        "synopsis": "A test grant opportunity.",
                        "agencyName": "Test Agency",
                        "opportunityStatus": "posted",
                        "opportunityUrl": "https://www.grants.gov/test123"
                    }
                ]
            }
    monkeypatch.setattr("requests.get", lambda *a, **k: DummyResponse())
    scraper = GrantsGovAPIScraper()
    grants = scraper.search_grants(query="test", rows=1)
    assert len(grants) == 1
    g = grants[0]
    assert g.title == "Test Grant"
    assert g.funder_name == "Test Agency"
    assert g.status == "open"
    assert g.application_url == "https://www.grants.gov/test123"
