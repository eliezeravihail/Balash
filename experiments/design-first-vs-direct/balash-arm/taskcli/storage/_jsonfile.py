"""A tiny helper for reading and writing a JSON list-of-rows file.

This is shared plumbing, not an abstraction over storage: both repositories keep
their rows in a JSON file the same way, and that mechanism (read the whole list,
write the whole list, replace atomically) is genuinely one thing that changes
together. It knows nothing about tasks or members -- only about turning a list of
dicts into a file and back. What a *row* means is each repository's own business.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List


def read_rows(path: Path) -> List[Dict[str, Any]]:
    """Return the stored rows, or an empty list if nothing has been written yet."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_rows(path: Path, rows: List[Dict[str, Any]]) -> None:
    """Replace the file's contents with these rows.

    Written to a temporary file in the same directory and then atomically renamed,
    so a crash mid-write cannot leave a half-written store behind -- the caller's
    only legitimate concern is that a write happens completely or not at all.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(rows, handle, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise
