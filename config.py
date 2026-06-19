"""Configuration: keyword filters and Twilio credentials loaded from env."""
from __future__ import annotations

import os
import re

from dotenv import load_dotenv

load_dotenv()

# --- Search target ---------------------------------------------------------
# The listing must mention the project (NTH / New Town Heights) AND the locality.
# Matching is case-insensitive and checked against the ad title + location.
PROJECT_TERMS: tuple[str, ...] = ("nth", "new town heights")
LOCALITY_TERMS: tuple[str, ...] = ("kakkanad",)

# Broad query strings handed to each site's search.
SEARCH_QUERY = "dlf kakkanad"

# --- Listing type ----------------------------------------------------------
# When True, only rental listings are kept; sale/resale listings are dropped.
RENTALS_ONLY = True
# Words that signal a rental listing.
RENT_TERMS: tuple[str, ...] = (
    "rent",
    "rental",
    "lease",
    "let out",
    "for rent",
    "per month",
    "/month",
    "monthly",
)
# Words that signal a sale listing (used to exclude when RENTALS_ONLY).
SALE_TERMS: tuple[str, ...] = (
    "for sale",
    "resale",
    "lakh",
    "lac",
    "crore",
)

# How many listings (max) to pull per site per run.
MAX_RESULTS_PER_SITE = 60

# --- Scraping proxy (ScrapingAnt) ------------------------------------------
# Optional. When SCRAPER_API_KEY is set, the HTML scrapers (Housing, 99acres,
# MagicBricks) route through ScrapingAnt so JS-rendered, bot-protected pages
# load. OLX's JSON API stays direct. Get a free key at https://scrapingant.com
# and store it as the SCRAPER_API_KEY GitHub secret (or in your local .env).
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY", "")
# Use a real headless browser to render JavaScript (needed for these sites).
SCRAPER_RENDER_JS = True
SCRAPER_ENDPOINT = "https://api.scrapingant.com/v2/general"

# Network
REQUEST_TIMEOUT = 20  # seconds
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# --- Twilio WhatsApp -------------------------------------------------------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
# Twilio sandbox default: "whatsapp:+14155238886"
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
# Your number in E.164, e.g. "whatsapp:+9198XXXXXXXX"
CONTACT_NUMBER = os.getenv("CONTACT_NUMBER", "")


def matches_target(*texts: str) -> bool:
    """Return True if the combined text mentions the project AND the locality.

    Project/locality terms are matched on word boundaries so that short terms
    like "nth" don't accidentally match inside words such as "month" or "tenth".
    """
    blob = " ".join(t for t in texts if t).lower()
    has_project = any(
        re.search(rf"\b{re.escape(term)}\b", blob) for term in PROJECT_TERMS
    )
    has_locality = any(
        re.search(rf"\b{re.escape(term)}\b", blob) for term in LOCALITY_TERMS
    )
    return has_project and has_locality


def is_rental(*texts: str) -> bool:
    """Return True if the listing looks like a rental.

    When ``RENTALS_ONLY`` is disabled this always returns True. Otherwise the
    text must contain a rent signal and must not contain a sale-only signal
    (e.g. a price quoted in lakh/crore, or "for sale"/"resale").
    """
    if not RENTALS_ONLY:
        return True
    blob = " ".join(t for t in texts if t).lower()
    has_sale = any(term in blob for term in SALE_TERMS)
    has_rent = any(term in blob for term in RENT_TERMS)
    if has_sale and not has_rent:
        return False
    return has_rent

