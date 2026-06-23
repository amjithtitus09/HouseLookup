"""Shared HTTP utilities for scrapers."""
from __future__ import annotations

import json
import logging
from urllib.parse import urlencode

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
    """GET a JSON endpoint, routed through ScrapingAnt when a key is set.

    Sites like OLX block GitHub Actions' datacenter IPs, so a direct request
    just times out. When ``SCRAPER_API_KEY`` is configured the call is proxied
    through ScrapingAnt (Indian exit IP, retries) like the HTML scrapers. JSON
    endpoints are fetched with ``browser=false`` so the raw JSON body comes
    back unwrapped, then parsed here.
    """
    if config.SCRAPER_API_KEY:
        body = _get_via_proxy(session, url, render_js=False, **kwargs)
    else:
        body = _get_direct(session, url, **kwargs)
    if body is None:
        return None
    try:
        return json.loads(body)
    except ValueError as exc:
        log.warning("JSON parse failed for %s: %s", url, exc)
        return None


def get_text(session: requests.Session, url: str, **kwargs) -> str | None:
    if config.SCRAPER_API_KEY:
        return _get_via_proxy(session, url, render_js=config.SCRAPER_RENDER_JS, **kwargs)
    return _get_direct(session, url, **kwargs)


def _get_direct(session: requests.Session, url: str, **kwargs) -> str | None:
    try:
        resp = session.get(url, timeout=config.REQUEST_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        log.warning("Request failed for %s: %s", url, exc)
        return None


def _get_via_proxy(
    session: requests.Session, url: str, *, render_js: bool, **kwargs
) -> str | None:
    """Fetch ``url`` through ScrapingAnt, retrying transient 409 responses.

    ScrapingAnt renders the page (optionally with a real browser) and returns
    the response body directly. A 409 means it couldn't bypass the target's
    protection on that attempt and should be retried.

    Any ``params`` meant for the target are encoded onto ``url`` first, since
    ScrapingAnt only fetches whatever full URL it is handed.
    """
    target_params = kwargs.pop("params", None) or {}
    target_url = url
    if target_params:
        sep = "&" if "?" in url else "?"
        target_url = f"{url}{sep}{urlencode(target_params, doseq=True)}"

    kwargs["params"] = {
        "url": target_url,
        "x-api-key": config.SCRAPER_API_KEY,
        "browser": "true" if render_js else "false",
        "proxy_country": config.SCRAPER_COUNTRY,
    }
    last_exc: Exception | None = None
    for attempt in range(1, config.SCRAPER_RETRIES + 1):
        try:
            resp = session.get(
                config.SCRAPER_ENDPOINT, timeout=config.SCRAPER_TIMEOUT, **kwargs
            )
            if resp.status_code == 409 and attempt < config.SCRAPER_RETRIES:
                log.info("Proxy 409 for %s (attempt %d), retrying", target_url, attempt)
                continue
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            last_exc = exc
    log.warning("Proxied request failed for %s: %s", target_url, last_exc)
    return None
