"""Shared HTTP utilities for scrapers."""
from __future__ import annotations

import logging

import requests

import config

log = logging.getLogger("scrapers")


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": config.USER_AGENT,
            "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9",
            "Connection": "keep-alive",
        }
    )
    return s


def get_json(session: requests.Session, url: str, **kwargs) -> dict | list | None:
    try:
        resp = session.get(url, timeout=config.REQUEST_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except (requests.RequestException, ValueError) as exc:
        log.warning("JSON request failed for %s: %s", url, exc)
        return None


def get_text(session: requests.Session, url: str, **kwargs) -> str | None:
    target_url = url
    if config.SCRAPER_API_KEY:
        # Route through ScrapingAnt: it fetches `url` (optionally with a real
        # browser) and returns the rendered HTML body directly.
        target_url = config.SCRAPER_ENDPOINT
        params = dict(kwargs.pop("params", {}) or {})
        params.update(
            {
                "url": url,
                "x-api-key": config.SCRAPER_API_KEY,
                "browser": "true" if config.SCRAPER_RENDER_JS else "false",
            }
        )
        kwargs["params"] = params
    try:
        resp = session.get(target_url, timeout=config.REQUEST_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        log.warning("HTML request failed for %s: %s", url, exc)
        return None
