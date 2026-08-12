#!/usr/bin/env python3
"""aims staleness read hook (SKELETON: contracts only, no bodies).

Fires when the agent reads a capsa record. Recomputes the record's anchor against current
source and, on mismatch, returns an advisory note. Advisory only: never blocks, never edits,
never auto-invalidates. Uses the same hashing as ../tools/aims_anchor.py so read-time and
write-time agree. Fail-open: a broken anchor reports "possibly moved — re-verify", never errors.

See staleness-read.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Drift:
    """One drift finding for a record: which anchor drifted and a human-readable reason."""

    record: str
    subject: str          # the file path or subtree root that changed
    reason: str           # "content changed" | "structure changed" | "source missing"


def check_record(record: Path, repo_root: Path) -> list[Drift]:
    """Recompute the record's anchor (anchors: or shape:) vs current source; return any Drift.

    Empty list means in-sync or nothing to check. Never raises on missing/unreadable source —
    that becomes a Drift(reason="source missing"), keeping the hook fail-open.
    """
    raise NotImplementedError


def advisory(drifts: list[Drift]) -> str:
    """Render drift findings as a short advisory to append to the read result.

    Must read as *possible* staleness, never as a verdict, and never as a block.
    """
    raise NotImplementedError


def on_read(read_path: Path, repo_root: Path) -> str | None:
    """Hook entry: if read_path is a capsa record with an anchor, return an advisory or None.

    Returns None when there is nothing to say (not a record, no anchor, or in-sync). Returning a
    string appends it to the read; it never prevents or alters the read itself.
    """
    raise NotImplementedError


if __name__ == "__main__":  # pragma: no cover
    # Invoked by the hook runner with the read event on stdin; parse, call on_read, emit advisory.
    raise NotImplementedError
