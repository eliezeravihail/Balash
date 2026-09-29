"""Deterministic text helpers: normalization, store names, money, Hebrew display."""

from __future__ import annotations

import re
from datetime import date

_QUOTES = str.maketrans({"״": '"', "׳": "'", "“": '"', "”": '"', "’": "'", "`": "'"})
_SPACES = re.compile(r"\s+")
_STORE_NOISE = re.compile(
    r'(בע"מ|בעמ|בע״מ|ltd\.?|limited|inc\.?|סניף\s*\S+|עוסק\s*מורשה|ח\.?פ\.?\s*\d+|[\d\-]{6,})',
    re.IGNORECASE,
)
_PUNCT = re.compile(r"[^\w\s\"']", re.UNICODE)

HEBREW_MONTHS = [
    "ינואר", "פברואר", "מרץ", "אפריל", "מאי", "יוני",
    "יולי", "אוגוסט", "ספטמבר", "אוקטובר", "נובמבר", "דצמבר",
]


def normalize_desc(text: str) -> str:
    """Stable key for a product description: same printed text, same key."""
    text = (text or "").translate(_QUOTES).strip().lower()
    return _SPACES.sub(" ", text)


def normalize_store(name: str | None) -> str:
    if not name:
        return ""
    text = name.translate(_QUOTES).lower()
    text = _STORE_NOISE.sub(" ", text)
    text = _PUNCT.sub(" ", text)
    return _SPACES.sub(" ", text).strip()


def resolve_account(name: str | None, aliases: dict[str, list[str]]) -> str:
    """Map a printed store name to its canonical name using the configured aliases.

    Exact match on the normalized form first, then containment either way
    (a printed "מכולת יוסי בע"מ סניף 2" still matches the alias "מכולת יוסי").
    Unknown names stay as their normalized form.
    """
    key = normalize_store(name)
    if not key:
        return ""
    table = {normalize_store(canon): canon for canon in aliases}
    for canon, names in aliases.items():
        for alias in names:
            table[normalize_store(alias)] = canon
    if key in table:
        return table[key]
    for alias_key, canon in sorted(table.items(), key=lambda kv: -len(kv[0])):
        if alias_key and (alias_key in key or key in alias_key):
            return canon
    return key


def money(value: float | None) -> str:
    if value is None:
        return "?"
    sign = "-" if value < 0 else ""
    return f"{sign}{abs(value):,.2f} ₪"


def fmt_date(iso: str | None) -> str:
    if not iso:
        return "תאריך לא ידוע"
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        return iso
    return d.strftime("%d.%m.%Y")


def month_label(month: str) -> str:
    year, m = month.split("-")
    return f"{HEBREW_MONTHS[int(m) - 1]} {year}"


def rtl(text: str) -> str:
    """Visual order for renderers without bidi support, such as matplotlib."""
    from bidi import get_display

    return get_display(text)
