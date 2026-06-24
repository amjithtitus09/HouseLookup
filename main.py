"""Entry point: scrape all sites, notify on new matching ads, persist state.

Usage:
    python main.py            # scrape, notify via WhatsApp, save seen ids
    python main.py --dry-run  # scrape + print matches, no WhatsApp, no state write
    python main.py --seed     # mark everything currently found as seen (no notify)
"""
from __future__ import annotations

import argparse
import logging

import notifier
from models import Ad
from scrapers import SCRAPERS
from state import load_seen, save_seen

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("main")


def collect_ads() -> list[Ad]:
    """Run every scraper in isolation; one failing site never stops the others."""
    all_ads: list[Ad] = []
    for name, fetch in SCRAPERS:
        try:
            ads = fetch()
            all_ads.extend(ads)
        except Exception as exc:  # noqa: BLE001
            log.error("Scraper '%s' crashed: %s", name, exc)
    # De-duplicate across sources by ad id.
    unique: dict[str, Ad] = {}
    for ad in all_ads:
        unique.setdefault(ad.id, ad)
    # Newest first by post date. Ads without a known timestamp (the HTML
    # scrapers don't expose one) sort last, after the dated listings.
    ordered = sorted(
        unique.values(),
        key=lambda ad: ad.posted_ts if ad.posted_ts is not None else float("-inf"),
        reverse=True,
    )
    return ordered


def main() -> None:
    parser = argparse.ArgumentParser(description="DLF NTH Kakkanad ad watcher")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print matches, don't send or save"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Mark all current matches as seen without notifying",
    )
    args = parser.parse_args()

    seen = load_seen()
    ads = collect_ads()
    new_ads = [ad for ad in ads if ad.id not in seen]

    log.info("Found %d matching ads (%d new).", len(ads), len(new_ads))
    for ad in new_ads:
        log.info("NEW: %s | %s | %s", ad.posted_time or "?", ad.title, ad.url)

    if args.dry_run:
        log.info("Dry run: not sending notifications or saving state.")
        return

    if args.seed:
        save_seen(seen | {ad.id for ad in ads})
        log.info("Seeded %d ad ids as seen.", len(ads))
        return

    notifier.send_ads(new_ads)
    save_seen(seen | {ad.id for ad in ads})
    log.info("State saved. %d ids tracked.", len(seen | {ad.id for ad in ads}))


if __name__ == "__main__":
    main()
