"""
CLI script to fetch grants from grants.gov API and save as JSON.
"""
import json
from pathlib import Path

from grant_ai.scrapers.grantsgov.api_scraper import GrantsGovAPIScraper


def main():
    scraper = GrantsGovAPIScraper()
    print("Fetching grants from grants.gov API...")
    grants = scraper.search_grants(query="housing", rows=10)
    print(f"Fetched {len(grants)} grants.")
    out_path = Path("data/grants_gov_housing.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump([g.dict() for g in grants], f, indent=2, default=str)
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    main()
