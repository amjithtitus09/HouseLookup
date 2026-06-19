"""NoBroker scraper (best-effort HTML).

NoBroker has aggressive bot protection; this is best-effort and may return
nothing on many runs. It must never raise.
"""
from __future__ import annotations

from models import Ad

from .htmlscrape import scrape_links

SEARCH_URL = (
    "https://www.nobroker.in/property/sale/kochi/Kakkanad"
    "?searchParam=W3sibGF0IjoxMC4wMTU5LCJsb24iOjc2LjM0MTksInBsYWNlSWQiOiIifV0="
)


def fetch() -> list[Ad]:
    return scrape_links(
        source="nobroker",
        search_url=SEARCH_URL,
        base_url="https://www.nobroker.in",
        detail_path_re=r"/property/|-detail",
    )
