"""Where tasks are kept -- the SQLite implementation of ``TaskRepository``.

The other backend behind the storage contract, and the only place that knows tasks live
in a ``tasks`` table or what its columns are. It is byte-for-byte interchangeable with
the JSON implementation from a caller's seat: ``get`` runs ``SELECT ... WHERE id=?``
where the JSON one scans a list; ``save`` runs one ``UPDATE ... WHERE id=?`` where the
JSON one rewrites a whole file. Same behavior, different mechanism -- and the same
domain objects and domain errors cross the boundary, never a row or a column name.

The tagged assignee ``{kind, id}`` maps to two columns (``assignee_kind``,
``assignee_id``); both NULL means unassigned. That mapping is sealed here, exactly as
the JSON dict mapping is sealed in the JSON repository.
"""

from __future__ import annotations

import sqlite3
from typing import List, Optional

from ...domain import (
    AssigneeKind,
    AssigneeRef,
    Prerequisites,
    Status,
    Task,
    TaskId,
    TaskNotFoundError,
)


class SqliteTaskRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def add(self, task: Task) -> None:
        kind, ident = _assignee_columns(task.assignee)
        self._conn.execute(
            "INSERT INTO tasks (id, title, description, status, assignee_kind, "
            "assignee_id) VALUES (?, ?, ?, ?, ?, ?)",
            (task.id.value, task.title, task.description, task.status.value, kind, ident),
        )
        self._write_prerequisites(task)
        self._conn.commit()

    def save(self, task: Task) -> None:
        """Persist changes to a task that already exists.

        Prerequisites are fixed at creation, so a save never rewrites them -- only the
        mutable columns (title/description/status/assignee) are updated here.
        """
        kind, ident = _assignee_columns(task.assignee)
        cursor = self._conn.execute(
            "UPDATE tasks SET title = ?, description = ?, status = ?, "
            "assignee_kind = ?, assignee_id = ? WHERE id = ?",
            (task.title, task.description, task.status.value, kind, ident, task.id.value),
        )
        self._conn.commit()
        if cursor.rowcount == 0:
            raise TaskNotFoundError(f"no task with id {task.id.value!r} to save")

    def get(self, task_id: TaskId) -> Task:
        row = self._conn.execute(
            "SELECT id, title, description, status, assignee_kind, assignee_id "
            "FROM tasks WHERE id = ?",
            (task_id.value,),
        ).fetchone()
        if row is None:
            raise TaskNotFoundError(f"no task with id {task_id.value!r}")
        return _from_row(row, self._prerequisites_of(task_id))

    def all(self) -> List[Task]:
        # ORDER BY the implicit rowid preserves insertion order -- the same order the
        # JSON store returns rows in, so listings read identically across backends.
        rows = self._conn.execute(
            "SELECT id, title, description, status, assignee_kind, assignee_id "
            "FROM tasks ORDER BY rowid"
        ).fetchall()
        return [
            _from_row(row, self._prerequisites_of(TaskId(row["id"]))) for row in rows
        ]

    # --- the prerequisite join table; one edge per row ---

    def _write_prerequisites(self, task: Task) -> None:
        self._conn.executemany(
            "INSERT INTO task_prerequisites (task_id, prereq_id) VALUES (?, ?)",
            [(task.id.value, prereq.value) for prereq in task.prerequisites],
        )

    def _prerequisites_of(self, task_id: TaskId) -> Prerequisites:
        rows = self._conn.execute(
            "SELECT prereq_id FROM task_prerequisites WHERE task_id = ? ORDER BY rowid",
            (task_id.value,),
        ).fetchall()
        return Prerequisites.of(TaskId(row["prereq_id"]) for row in rows)


# --- the task <-> row mapping; the only code that knows the column shape ---


def _assignee_columns(
    assignee: Optional[AssigneeRef],
) -> tuple[Optional[str], Optional[str]]:
    if assignee is None:
        return None, None
    return assignee.kind.value, assignee.id_value


def _from_row(row: sqlite3.Row, prerequisites: Prerequisites) -> Task:
    return Task(
        task_id=TaskId(row["id"]),
        title=row["title"],
        description=row["description"],
        status=Status(row["status"]),
        assignee=_assignee_from_row(row["assignee_kind"], row["assignee_id"]),
        prerequisites=prerequisites,
    )


def _assignee_from_row(
    kind: Optional[str], ident: Optional[str]
) -> Optional[AssigneeRef]:
    if kind is None:
        return None
    return AssigneeRef(kind=AssigneeKind(kind), id_value=ident)
