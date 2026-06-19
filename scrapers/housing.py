"""Housing.com scraper (best-effort HTML)."""
from __future__ import annotations

from models import Ad

from .htmlscrape import scrape_links

SEARCH_URL = (
    "https://housing.com/rent-dlf-new-town-heights-for-rent-in-kakkanad-kochi"
    "-rpid-AGqj1AH0"
)
# Fallback generic search if the slug above stops resolving.
GENERIC_SEARCH = "https://housing.com/in/rent/real-estate-kakkanad-kochi"


def fetch() -> list[Ad]:
    ads = scrape_links(
        source="housing",
        search_url=SEARCH_URL,
        base_url="https://housing.com",
        detail_path_re=r"/in/rent/|/rent/page/|/rent/[A-Za-z0-9]",
    )
    return ads
