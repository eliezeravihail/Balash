"""Where the team roster is kept -- the SQLite implementation of ``MemberRepository``.

The SQLite persistence boundary for members: one ``members`` table, one row per member.
``add`` is an upsert via ``INSERT ... ON CONFLICT(id) DO UPDATE`` -- the relational form
of the JSON repo's scan-for-id/replace-else-append, idempotent in the same observable
way (re-adding an id updates the name and leaves one row). ``team`` vends the whole
roster as the Team authority. Callers see Members and the Team, never a column.
"""

from __future__ import annotations

import sqlite3

from ...domain import Member, MemberId, Team


class SqliteMemberRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def add(self, member: Member) -> None:
        self._conn.execute(
            "INSERT INTO members (id, display_name) VALUES (?, ?) "
            "ON CONFLICT(id) DO UPDATE SET display_name = excluded.display_name",
            (member.id.value, member.display_name),
        )
        self._conn.commit()

    def team(self) -> Team:
        """Load the whole roster as the Team -- the object the rest of the program
        asks about membership."""
        rows = self._conn.execute(
            "SELECT id, display_name FROM members ORDER BY rowid"
        ).fetchall()
        return Team(_from_row(row) for row in rows)


def _from_row(row: sqlite3.Row) -> Member:
    return Member(id=MemberId(row["id"]), display_name=row["display_name"])
