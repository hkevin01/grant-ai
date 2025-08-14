"""RSS/Sitemap ingestion utilities.

Lightweight parser with optional feedparser dependency. Falls back to stdlib
xml parsing when feedparser isn't available. Safe for import in minimal envs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RSSItem:
    title: str
    link: str
    published: Optional[str] = None
    summary: Optional[str] = None


def _try_import_feedparser():
    try:
        import feedparser  # type: ignore
        return feedparser
    except Exception:
        return None


def parse_rss(
    url: str,
    *,
    limit: int = 50,
    timeout: int = 15,
) -> List[RSSItem]:
    """Parse an RSS/Atom feed and return a list of items.

    - Uses `feedparser` if available. If not, falls back to stdlib xml.
    - Never raises on parse errors; returns best-effort results.
    """
    items: List[RSSItem] = []

    feedparser = _try_import_feedparser()
    if feedparser:
        try:
            parsed = feedparser.parse(url)
            entries = parsed.get("entries") or []
            for entry in entries[:limit]:
                published = (
                    entry.get("published")
                    or entry.get("updated")
                    or None
                )
                summary_val = entry.get("summary")
                items.append(
                    RSSItem(
                        title=str(entry.get("title", "")),
                        link=str(entry.get("link", "")),
                        published=(
                            str(published) if published is not None else None
                        ),
                        summary=(
                            str(summary_val)
                            if summary_val is not None
                            else None
                        ),
                    )
                )
            return items
        except Exception:
            # Fall through to stdlib path
            items = []

    # Stdlib fallback
    try:
        import urllib.request
        import xml.etree.ElementTree as ET

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        # nosec B310: URL comes from trusted configuration/use
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        # Handle RSS 2.0 and Atom
        # RSS
        for item in root.findall('.//item')[:limit]:
            title = (item.findtext('title') or '').strip()
            link = (item.findtext('link') or '').strip()
            pub = (item.findtext('pubDate') or '').strip() or None
            desc = (item.findtext('description') or '').strip() or None
            if title or link:
                items.append(
                    RSSItem(
                        title=title,
                        link=link or "",
                        published=pub,
                        summary=desc,
                    )
                )
        if items:
            return items
        # Atom
        ns = {'a': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//a:entry', ns)[:limit]:
            title = (entry.findtext('a:title', namespaces=ns) or '').strip()
            link_el = entry.find('a:link', ns)
            link = link_el.get('href') if link_el is not None else ''
            updated = (
                entry.findtext('a:updated', namespaces=ns) or ''
            ).strip() or None
            summary = (
                entry.findtext('a:summary', namespaces=ns) or ''
            ).strip() or None
            if title or link:
                items.append(
                    RSSItem(
                        title=title,
                        link=link or "",
                        published=updated,
                        summary=summary,
                    )
                )
    except Exception:
        return []

    return items
