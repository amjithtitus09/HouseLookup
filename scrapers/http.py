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
    try:
        resp = session.get(url, timeout=config.REQUEST_TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        log.warning("HTML request failed for %s: %s", url, exc)
        return None
