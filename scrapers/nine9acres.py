"""99acres scraper (best-effort HTML)."""
from __future__ import annotations

from models import Ad

from .htmlscrape import scrape_links

# 99acres rentals for DLF New Town Heights, Kakkanad, Kochi.
SEARCH_URL = (
    "https://www.99acres.com/flats-for-rent-in-dlf-new-town-heights-kochi"
    "-kakkanad-kochi-3720-rnpffid"
)


def fetch() -> list[Ad]:
    return scrape_links(
        source="99acres",
        search_url=SEARCH_URL,
        base_url="https://www.99acres.com",
        detail_path_re=r"/[a-z0-9-]+-spid-|/property-",
    )
