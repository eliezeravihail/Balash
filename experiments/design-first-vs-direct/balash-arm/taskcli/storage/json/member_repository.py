"""Where the team roster is kept -- the JSON implementation of ``MemberRepository``.

The JSON persistence boundary for members, and the only place that knows members live
in a JSON file or under what field names. It hands back domain objects: individual
Members, or the whole Team assembled from them. Callers add a member and later load the
team without ever seeing the file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ...domain import Member, MemberId, Team
from .. import _jsonfile


class JsonMemberRepository:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def add(self, member: Member) -> None:
        rows = _jsonfile.read_rows(self._path)
        for index, row in enumerate(rows):
            if row["id"] == member.id.value:
                rows[index] = _to_row(member)  # updating a name is fine and idempotent
                _jsonfile.write_rows(self._path, rows)
                return
        rows.append(_to_row(member))
        _jsonfile.write_rows(self._path, rows)

    def team(self) -> Team:
        """Load the whole roster as the Team -- the object the rest of the program
        asks about membership."""
        members = (_from_row(row) for row in _jsonfile.read_rows(self._path))
        return Team(members)


def _to_row(member: Member) -> Dict[str, Any]:
    return {"id": member.id.value, "display_name": member.display_name}


def _from_row(row: Dict[str, Any]) -> Member:
    return Member(id=MemberId(row["id"]), display_name=row["display_name"])
