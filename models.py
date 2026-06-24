"""Normalized representation of a property listing."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Ad:
    source: str  # e.g. "olx"
    title: str
    url: str
    price: Optional[str] = None
    location: Optional[str] = None
    posted_time: Optional[str] = None
    posted_ts: Optional[float] = None  # sortable epoch seconds, if known
    raw_id: Optional[str] = None  # site-native id, if available
    id: str = field(init=False)

    def __post_init__(self) -> None:
        if self.raw_id:
            self.id = f"{self.source}:{self.raw_id}"
        else:
            digest = hashlib.sha1(self.url.encode("utf-8")).hexdigest()[:16]
            self.id = f"{self.source}:{digest}"

    def as_message(self) -> str:
        parts = [f"🏠 New listing on {self.source.upper()}", self.title]
        if self.price:
            parts.append(f"💰 {self.price}")
        if self.location:
            parts.append(f"📍 {self.location}")
        if self.posted_time:
            parts.append(f"🕒 {self.posted_time}")
        parts.append(self.url)
        return "\n".join(parts)
