"""MagicBricks scraper (best-effort HTML)."""
from __future__ import annotations

from models import Ad

from .htmlscrape import scrape_links

SEARCH_URL = (
    "https://www.magicbricks.com/property-for-sale/residential-real-estate"
    "?proptype=Multistorey-Apartment&cityName=Kochi&Locality=Kakkanad"
)


def fetch() -> list[Ad]:
    return scrape_links(
        source="magicbricks",
        search_url=SEARCH_URL,
        base_url="https://www.magicbricks.com",
        detail_path_re=r"/propertyDetails/|-pdpid-",
    )
