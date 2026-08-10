"""Where execution results are kept -- the SQLite implementation of ``ResultRepository``.

The SQLite persistence boundary for execution results: append-only history in a
``results`` table. Each execute is one ``INSERT``; the code issues no UPDATE or DELETE
against ``results``, so a prior result is never overwritten -- the same guarantee the
JSON store gives by only ever appending to a list. ``for_task`` returns a task's results
oldest-first via ``ORDER BY seq``, the private surrogate key that stands in for JSON's
append position. ``succeeded`` is stored as INTEGER 0/1 and mapped back to a Python
``bool`` on read; ``seq`` never leaves this file.
"""

from __future__ import annotations

import sqlite3
from typing import List

from ...domain import AgentId, ExecutionResult, TaskId


class SqliteResultRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def append(self, result: ExecutionResult) -> None:
        """Record one more execution result. Append-only -- prior results are kept."""
        self._conn.execute(
            "INSERT INTO results (task_id, agent_id, succeeded, output) "
            "VALUES (?, ?, ?, ?)",
            (
                result.task_id.value,
                result.agent_id.value,
                1 if result.succeeded else 0,
                result.output,
            ),
        )
        self._conn.commit()

    def for_task(self, task_id: TaskId) -> List[ExecutionResult]:
        """Every result for a task, in the order it was recorded (chronological)."""
        rows = self._conn.execute(
            "SELECT task_id, agent_id, succeeded, output FROM results "
            "WHERE task_id = ? ORDER BY seq",
            (task_id.value,),
        ).fetchall()
        return [_from_row(row) for row in rows]


def _from_row(row: sqlite3.Row) -> ExecutionResult:
    return ExecutionResult(
        task_id=TaskId(row["task_id"]),
        agent_id=AgentId(row["agent_id"]),
        succeeded=bool(row["succeeded"]),
        output=row["output"],
    )
