"""99acres scraper (best-effort HTML)."""
from __future__ import annotations

from models import Ad

from .htmlscrape import scrape_links

# 99acres property search for Kakkanad, Kochi.
SEARCH_URL = (
    "https://www.99acres.com/search/property/buy/kakkanad-kochi"
    "?city=58&locality=&keyword=DLF%20New%20Town%20Heights&preference=S&area_unit=1"
)


def fetch() -> list[Ad]:
    return scrape_links(
        source="99acres",
        search_url=SEARCH_URL,
        base_url="https://www.99acres.com",
        detail_path_re=r"/[a-z0-9-]+-spid-|/property-",
    )
