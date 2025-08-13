"""Strict Pydantic models for scraper contract validation."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


class Funder(BaseModel):
    """Basic funder metadata."""
    name: str
    website: Optional[HttpUrl] = None


class GrantRecord(BaseModel):
    """Minimal grant record enforced across all scrapers."""

    id: constr(min_length=1)  # type: ignore[valid-type]
    title: constr(min_length=1)  # type: ignore[valid-type]
    description: Optional[str] = None
    funder: Optional[Funder] = None
    url: HttpUrl
    min_amount: Optional[int] = None
    max_amount: Optional[int] = None
    deadline: Optional[date] = None
    tags: List[str] = Field(default_factory=list)
    source: str

    # No validators needed; constrained types enforce non-empty values.
    # No validators needed; constrained types enforce non-empty values.
