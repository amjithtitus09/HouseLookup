"""Housing.com scraper (best-effort HTML)."""
from __future__ import annotations

from models import Ad

from .htmlscrape import scrape_links

SEARCH_URL = (
    "https://housing.com/in/buy/searches/"
    "P3v8r9k5dlf-new-town-heights-kakkanad"
)
# Fallback generic search if the slug above stops resolving.
GENERIC_SEARCH = "https://housing.com/in/buy/real-estate-kakkanad-kochi"


def fetch() -> list[Ad]:
    ads = scrape_links(
        source="housing",
        search_url=GENERIC_SEARCH,
        base_url="https://housing.com",
        detail_path_re=r"/in/buy/resale/|/rent/|/resale/page/|/buy/[A-Za-z0-9]",
    )
    return ads
