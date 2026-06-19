"""Site scrapers. Each module exposes fetch() -> list[Ad]."""
from __future__ import annotations

from typing import Callable

from models import Ad

from . import housing, magicbricks, nine9acres, olx

# Registry of (name, fetch) pairs. Order = notification order.
SCRAPERS: list[tuple[str, Callable[[], list[Ad]]]] = [
    ("olx", olx.fetch),
    ("housing", housing.fetch),
    ("99acres", nine9acres.fetch),
    ("magicbricks", magicbricks.fetch),
]
