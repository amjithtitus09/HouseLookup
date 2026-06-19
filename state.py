"""Persistent store of already-seen ad ids (committed back by CI)."""
from __future__ import annotations

import json
import os
from typing import Iterable

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SEEN_PATH = os.path.join(DATA_DIR, "seen_ids.json")


def load_seen() -> set[str]:
    try:
        with open(SEEN_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return set(data.get("ids", []))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(ids: Iterable[str]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    payload = {"ids": sorted(set(ids))}
    with open(SEEN_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")
