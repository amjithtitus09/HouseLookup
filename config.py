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
SEARCH_QUERY = "DLF Kakkanad"

# How many listings (max) to pull per site per run.
MAX_RESULTS_PER_SITE = 60

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
