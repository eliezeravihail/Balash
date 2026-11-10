#!/usr/bin/env python3
"""aims anchor — write-time anchor stamper (SKELETON: contracts only, no bodies).

Stamps a staleness anchor into a capsa record's frontmatter. The anchor kind follows the
record's claim: `anchors:` (per-file content hash) for a file-content claim, or `shape:`
(child-name fingerprint) for a structural claim. Called explicitly by the method when it files
a record — never as a hook. Stdlib-only; idempotent; touches exactly one record file.

See aims-anchor.md and ../docs/format-profile.md §2.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Anchor:
    """One file-content anchor: a product-repo path and the sha256 of its bytes at write time."""

    path: str
    hash: str


@dataclass(frozen=True)
class Shape:
    """A structural anchor: a subtree root and the sha256 of its sorted child-name set."""

    root: str
    children_hash: str
    depth: int = 1


def content_hash(file: Path) -> str:
    """Return 'sha256:<hex>' over the file's bytes. Raises if the file is absent."""
    raise NotImplementedError


def shape_hash(root: Path, depth: int = 1) -> str:
    """Return 'sha256:<hex>' over the sorted set of child *names* under root to `depth`.

    Names only — never file contents. This is what makes a structural anchor content-blind.
    """
    raise NotImplementedError


def stamp_anchors(record: Path, paths: list[Path]) -> list[Anchor]:
    """Compute one Anchor per path and write the `anchors:` block into the record's frontmatter.

    Idempotent (stable key order, sorted by path). Preserves all other keys, the body, and
    formatting. Raises if the record already carries a `shape:` block (claim-kind conflict).
    """
    raise NotImplementedError


def stamp_shape(record: Path, root: Path, depth: int = 1) -> Shape:
    """Compute the Shape fingerprint for `root` and write the `shape:` block into the record.

    Idempotent; preserves everything else. Raises if the record already carries `anchors:`.
    """
    raise NotImplementedError


def main(argv: list[str]) -> int:
    """Parse args (aims anchor [--shape] [--depth N] <record> <path|root>...), dispatch, report."""
    raise NotImplementedError


if __name__ == "__main__":  # pragma: no cover
    import sys

    raise SystemExit(main(sys.argv[1:]))
