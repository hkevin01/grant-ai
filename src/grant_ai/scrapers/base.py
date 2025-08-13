"""Scraper interface & registry (legacy GrantScraper alias retained)."""
from __future__ import annotations

from abc import ABC
from typing import Any, Callable, Dict, List, Optional, cast

from pydantic import HttpUrl

from grant_ai.models.grants_core import GrantRecord
from grant_ai.models.organization import OrganizationProfile

_SCRAPER_REGISTRY: Dict[str, "ScraperBase"] = {}


def register_scraper(name: str) -> Callable[[type], type]:
    """Decorator to register a scraper implementation by name."""

    def _decorator(cls: type) -> type:
        instance = cls()  # instantiate once (scrapers should be stateless)
        _SCRAPER_REGISTRY[name] = instance
        return cls

    return _decorator


def available_scrapers() -> List[str]:
    """List registered scraper names."""
    return sorted(_SCRAPER_REGISTRY.keys())


def get_scraper(name: str) -> "ScraperBase":
    """Retrieve a registered scraper by name."""
    try:
        return _SCRAPER_REGISTRY[name]
    except KeyError as e:  # pragma: no cover
        raise ValueError(
            f"Scraper '{name}' not found. Available: {available_scrapers()}"
        ) from e


class ScraperBase(ABC):
    """Abstract base enforcing a single scrape_grants entrypoint."""

    source_name: str = "unknown"

    def scrape_grants(
        self,
        profile: OrganizationProfile,
        limit: Optional[int] = None,
        filters: Optional[Dict] = None,
    ) -> List[GrantRecord]:
        """Return grants relevant to the profile (never None).

        Default implementation attempts legacy fallbacks:
        - If a subclass implements get_all_grants(), filter by simple
          keyword match using organization's focus keywords.
        - If a subclass implements search_grants(query=...), use that.
        """
        # legacy: search_grants
        if hasattr(self, "search_grants") and callable(
            getattr(self, "search_grants")
        ):
            query = " ".join(profile.get_focus_keywords())
            results = getattr(self, "search_grants")(query=query)
            converted = [_to_record(g, self.source_name) for g in results]
            return self._truncate(converted, limit)

        # legacy: get_all_grants
        if hasattr(self, "get_all_grants") and callable(
            getattr(self, "get_all_grants")
        ):
            all_grants = getattr(self, "get_all_grants")()
            keywords = set(k.lower() for k in profile.get_focus_keywords())
            filtered = []
            for g in all_grants:
                title_part = str(getattr(g, 'title', ''))
                desc_part = str(getattr(g, 'description', ''))
                text = f"{title_part} {desc_part}".lower()
                if any(k in text for k in keywords):
                    filtered.append(g)
            converted = [_to_record(g, self.source_name) for g in filtered]
            return self._truncate(converted, limit)

        # Nothing to do by default
        return []

    def _truncate(
        self, items: List[GrantRecord], limit: Optional[int]
    ) -> List[GrantRecord]:
        return items[:limit] if limit else items

    # Legacy optional methods (may be implemented by old scrapers)
    def search_grants(self, query: str = "", **kwargs):  # pragma: no cover
        raise NotImplementedError

    def get_all_grants(self):  # pragma: no cover
        raise NotImplementedError


def _to_record(grant_obj: Any, source: str) -> GrantRecord:
    """Best-effort conversion from legacy Grant model to GrantRecord."""
    try:
        from grant_ai.models.grant import Grant as LegacyGrant  # local import
    except Exception:  # pragma: no cover - defensive
        LegacyGrant = object  # type: ignore

    if isinstance(grant_obj, LegacyGrant):
        url_str = (
            str(getattr(grant_obj, "application_url"))
            if getattr(grant_obj, "application_url", None)
            else (
                str(getattr(grant_obj, "information_url"))
                if getattr(grant_obj, "information_url", None)
                else "http://example.com"
            )
        )
        desc = getattr(grant_obj, "description", None) or ""
        min_amount = getattr(grant_obj, "amount_min", None)
        max_amount = getattr(grant_obj, "amount_max", None)
        deadline = getattr(grant_obj, "application_deadline", None)
        tags = getattr(grant_obj, "focus_areas", []) or []
        return GrantRecord(
            id=str(
                getattr(
                    grant_obj, "id", getattr(grant_obj, "title", "unknown")
                )
            ),
            title=str(getattr(grant_obj, "title", "Untitled")),
            description=str(desc) if desc is not None else None,
            url=cast(HttpUrl, HttpUrl(url_str)),
            min_amount=min_amount,
            max_amount=max_amount,
            deadline=deadline,
            tags=list(tags),
            source=source,
        )

    # Fallback minimal mapping
    title = str(getattr(grant_obj, "title", "Untitled"))
    desc = getattr(grant_obj, "description", None)
    url_str2 = getattr(grant_obj, "url", "http://example.com")
    return GrantRecord(
        id=title,
        title=title,
        description=desc,
        url=cast(HttpUrl, HttpUrl(str(url_str2))),
        source=source,
    )


# Backward compatibility alias
GrantScraper = ScraperBase



