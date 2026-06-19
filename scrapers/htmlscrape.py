"""Best-effort HTML listing extraction shared by the harder-to-scrape sites.

These sites (99acres, MagicBricks, Housing, NoBroker) use heavy anti-bot
protection and JS rendering, so static scraping is best-effort: it extracts
anchor links to detail pages and keeps the ones whose visible text matches the
target. A site returning nothing must never raise.
"""
from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import config
from models import Ad

from .http import get_text, make_session

log = logging.getLogger("scrapers.html")


def scrape_links(
    source: str,
    search_url: str,
    base_url: str,
    detail_path_re: str,
) -> list[Ad]:
    """Fetch a search page and build Ads from matching detail-page links."""
    session = make_session()
    html = get_text(session, search_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(detail_path_re)
    seen_hrefs: set[str] = set()
    ads: list[Ad] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if not pattern.search(href):
            continue
        # Use the anchor's nearest card text for matching/context.
        card = anchor.find_parent(["article", "li", "div"]) or anchor
        text = " ".join(card.get_text(" ", strip=True).split())[:300]
        title = " ".join(anchor.get_text(" ", strip=True).split()) or text[:120]
        if not config.matches_target(title, text):
            continue
        full_url = urljoin(base_url, href.split("?")[0])
        if full_url in seen_hrefs:
            continue
        seen_hrefs.add(full_url)
        ads.append(Ad(source=source, title=title or "Listing", url=full_url))
        if len(ads) >= config.MAX_RESULTS_PER_SITE:
            break

    log.info("%s: %d matching ads", source, len(ads))
    return ads
