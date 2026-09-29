"""The unit that flows between blocks."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class Record:
    """One piece of data passed between blocks.

    ``kind`` names the shape of ``data`` (for example ``item``, ``receipt``,
    ``finding``, ``message``). ``cites`` holds the ids of the records this one
    was derived from, so every output can be traced back to raw input.
    """

    kind: str
    data: dict[str, Any]
    id: str = ""
    cites: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id:
            self.id = new_id(self.kind[:4])

    def derive(self, kind: str, data: dict[str, Any], id: str = "") -> "Record":
        """Create a record that cites this one."""
        return Record(kind=kind, data=data, id=id, cites=[self.id])
