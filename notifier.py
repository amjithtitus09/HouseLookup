"""Twilio WhatsApp notifier."""
from __future__ import annotations

import logging

import config
from models import Ad

log = logging.getLogger("notifier")


def _client():
    from twilio.rest import Client

    return Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)


def is_configured() -> bool:
    return bool(
        config.TWILIO_ACCOUNT_SID
        and config.TWILIO_AUTH_TOKEN
        and config.CONTACT_NUMBER
    )


def send_ads(ads: list[Ad]) -> None:
    """Send one WhatsApp message per ad. Failures are logged, not raised."""
    if not ads:
        return
    if not is_configured():
        log.warning(
            "Twilio not configured (missing SID/token/contact). "
            "Skipping %d notification(s).",
            len(ads),
        )
        return

    client = _client()
    to = config.CONTACT_NUMBER
    if not to.startswith("whatsapp:"):
        to = f"whatsapp:{to}"

    for ad in ads:
        try:
            client.messages.create(
                from_=config.TWILIO_WHATSAPP_FROM,
                to=to,
                body=ad.as_message(),
            )
            log.info("Sent WhatsApp for %s", ad.id)
        except Exception as exc:  # noqa: BLE001 - never let one failure stop others
            log.error("Failed to send WhatsApp for %s: %s", ad.id, exc)
