"""OLX scraper using OLX's public relevance search JSON API.

This is the most reliable source. We query OLX, then keep only listings whose
title/location mention the target project + locality.
"""
from __future__ import annotations

import logging

import config
from models import Ad

from .http import get_json, make_session

log = logging.getLogger("scrapers.olx")

API = "https://www.olx.in/api/relevance/v4/search"


def _build_url(item: dict) -> str:
    # Prefer a canonical url provided by the API; fall back to id-based path.
    for key in ("url", "ad_url", "canonical_url"):
        val = item.get(key)
        if isinstance(val, str) and val.startswith("http"):
            return val
    item_id = item.get("id")
    return f"https://www.olx.in/item/iid-{item_id}" if item_id else "https://www.olx.in"


def _price(item: dict) -> str | None:
    price = item.get("price") or {}
    value = price.get("value") or {}
    return value.get("display") or price.get("display")


def _location(item: dict) -> str | None:
    loc = item.get("locations_resolved") or {}
    for key in (
        "SUBLOCALITY_LEVEL_1_name",
        "ADMIN_LEVEL_3_name",
        "ADMIN_LEVEL_1_name",
        "CITY_name",
    ):
        if loc.get(key):
            return loc[key]
    return None


def fetch() -> list[Ad]:
    session = make_session()
    params = {
        "query": config.SEARCH_QUERY,
        "size": config.MAX_RESULTS_PER_SITE,
        "page": 0,
        "lang": "en-v1",
        "sort_by": "relevance-desc",
    }
    data = get_json(session, API, params=params)
    if not data or not isinstance(data, dict):
        return []

    items = data.get("data") or []
    ads: list[Ad] = []
    for item in items:
        title = item.get("title") or ""
        location = _location(item)
        price = _price(item)
        if not config.matches_target(title, location or ""):
            continue
        if not config.is_rental(title, location or "", price or ""):
            continue
        ads.append(
            Ad(
                source="olx",
                title=title.strip(),
                url=_build_url(item),
                price=price,
                location=location,
                posted_time=item.get("display_date") or item.get("created_at_first"),
                raw_id=str(item.get("id")) if item.get("id") else None,
            )
        )
    log.info("OLX: %d matching ads", len(ads))
    return ads
