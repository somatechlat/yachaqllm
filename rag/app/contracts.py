"""Data contracts and validation helpers for YACHAQ-LEX chunks."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List
from urllib.parse import urlparse

REQUIRED_KEYS = {
    "source",
    "title",
    "ro_number",
    "ro_date",
    "article",
    "authority",
    "vigency",
    "url",
}


def validate_chunk_metadata(record: Dict[str, object]) -> List[str]:
    """Return a list of validation errors for a chunk metadata record."""
    errors: List[str] = []

    missing = REQUIRED_KEYS.difference(record)
    if missing:
        errors.append(f"missing keys: {sorted(missing)}")

    url = str(record.get("url", ""))
    if url:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            errors.append("url is not absolute")
    else:
        errors.append("url is empty")

    ro_number = str(record.get("ro_number", "")).strip()
    if not ro_number:
        errors.append("ro_number is empty")

    authority = str(record.get("authority", "")).strip().lower()
    allowed_authorities = {"constitution", "organic law", "law", "regulation", "resolution", "circular"}
    if authority and authority not in allowed_authorities:
        errors.append(f"authority '{record.get('authority')}' is not recognized")

    if record.get("ro_date"):
        try:
            datetime.strptime(str(record["ro_date"]), "%Y-%m-%d")
        except ValueError:
            errors.append("ro_date must be YYYY-MM-DD")
    else:
        errors.append("ro_date is empty")

    if record.get("vigency"):
        try:
            datetime.strptime(str(record["vigency"]), "%Y-%m-%d")
        except ValueError:
            errors.append("vigency must be YYYY-MM-DD")
    else:
        errors.append("vigency is empty")

    return errors
