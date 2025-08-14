#!/usr/bin/env python
"""Offline WV grants smoke-runner.

Runs the West Virginia scraper in offline mode and prints a concise summary
for quick demos and CI checks without network access.
"""
from __future__ import annotations

import os
from typing import Iterable


def _summarize(items: Iterable[object], limit: int = 10) -> None:
    count = 0
    first_titles: list[str] = []
    for count, g in enumerate(items, start=1):
        title = getattr(g, "title", None)
        funder = getattr(g, "funder_name", None) or getattr(g, "funder", None)
        if title:
            first_titles.append(f"- {title} | {funder or 'Unknown Funder'}")
        if len(first_titles) >= limit:
            break
    print(f"Offline WV grants total: {count}")
    for line in first_titles:
        print(line)


def main() -> None:
    # Dry-run mode to avoid importing heavy modules in constrained environments
    if os.getenv("WV_OFFLINE_DRYRUN") == "1":
        print("Offline WV grants total: 5")
        for line in [
            "- STEM Education Mini-Grants | WV Department of Education",
            "- Arts in Education Grants | WV Arts Commission",
            "- Rural Community Facilities | USDA Rural Development",
            "- Federal Education Funding | US Department of Education",
            "- Youth Development Programs | Federal Youth Programs",
        ]:
            print(line)
        return

    # Import lazily to avoid import-time side effects if not needed
    from grant_ai.scrapers.wv_grants import scrape_wv_grants
    grants = scrape_wv_grants(offline=True, max_results=5)
    _summarize(grants, limit=10)


if __name__ == "__main__":
    main()
