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
    if config.SCRAPER_API_KEY:
        return _get_text_via_proxy(session, url, **kwargs)
    try:
        resp = session.get(url, timeout=config.REQUEST_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        log.warning("HTML request failed for %s: %s", url, exc)
        return None


def _get_text_via_proxy(session: requests.Session, url: str, **kwargs) -> str | None:
    """Fetch `url` through ScrapingAnt, retrying transient 409 responses.

    ScrapingAnt renders the page (optionally with a real browser) and returns
    the HTML body directly. A 409 means it couldn't bypass the target's
    protection on that attempt and should be retried.
    """
    params = dict(kwargs.pop("params", {}) or {})
    params.update(
        {
            "url": url,
            "x-api-key": config.SCRAPER_API_KEY,
            "browser": "true" if config.SCRAPER_RENDER_JS else "false",
            "proxy_country": config.SCRAPER_COUNTRY,
        }
    )
    kwargs["params"] = params
    last_exc: Exception | None = None
    for attempt in range(1, config.SCRAPER_RETRIES + 1):
        try:
            resp = session.get(
                config.SCRAPER_ENDPOINT, timeout=config.SCRAPER_TIMEOUT, **kwargs
            )
            if resp.status_code == 409 and attempt < config.SCRAPER_RETRIES:
                log.info("Proxy 409 for %s (attempt %d), retrying", url, attempt)
                continue
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            last_exc = exc
    log.warning("Proxied HTML request failed for %s: %s", url, last_exc)
    return None
