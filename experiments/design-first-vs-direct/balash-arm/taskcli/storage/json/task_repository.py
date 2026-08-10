"""Where tasks are kept -- the JSON implementation of ``TaskRepository``.

This is one of the two backends behind the storage contract, and the *only* place that
knows tasks live in a JSON file or what the on-disk field names are. The rest of the
program asks it in domain terms -- "add this Task", "give me the task with this id",
"here is the changed task, save it" -- and never learns how or where the bytes land.
The mapping between a Task and its stored row lives here and nowhere else, so if the
on-disk shape ever changes, this file is the one that changes.

A caller holding only the ``TaskRepository`` port cannot tell this apart from the
SQLite implementation: ``get`` here linearly scans a list of dicts read from a whole
file; the SQLite one runs a ``SELECT ... WHERE id=?``. Same behavior, different
mechanism.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ...domain import (
    AssigneeKind,
    AssigneeRef,
    MemberId,
    Prerequisites,
    Status,
    Task,
    TaskId,
    TaskNotFoundError,
)
from .. import _jsonfile


class JsonTaskRepository:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def add(self, task: Task) -> None:
        rows = _jsonfile.read_rows(self._path)
        rows.append(_to_row(task))
        _jsonfile.write_rows(self._path, rows)

    def save(self, task: Task) -> None:
        """Persist changes to a task that already exists."""
        rows = _jsonfile.read_rows(self._path)
        for index, row in enumerate(rows):
            if row["id"] == task.id.value:
                rows[index] = _to_row(task)
                _jsonfile.write_rows(self._path, rows)
                return
        raise TaskNotFoundError(f"no task with id {task.id.value!r} to save")

    def get(self, task_id: TaskId) -> Task:
        for row in _jsonfile.read_rows(self._path):
            if row["id"] == task_id.value:
                return _from_row(row)
        raise TaskNotFoundError(f"no task with id {task_id.value!r}")

    def all(self) -> List[Task]:
        return [_from_row(row) for row in _jsonfile.read_rows(self._path)]


# --- the task <-> stored-row mapping; the only code that knows the disk shape ---


def _to_row(task: Task) -> Dict[str, Any]:
    return {
        "id": task.id.value,
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "assignee": _assignee_to_row(task.assignee),
        "prerequisites": [prereq.value for prereq in task.prerequisites],
    }


def _from_row(row: Dict[str, Any]) -> Task:
    return Task(
        task_id=TaskId(row["id"]),
        title=row["title"],
        description=row["description"],
        status=Status(row["status"]),
        assignee=_assignee_from_row(row["assignee"]),
        prerequisites=_prerequisites_from_row(row.get("prerequisites")),
    )


def _prerequisites_from_row(raw: Any) -> Prerequisites:
    # A row predating prerequisites (or any stage-1 row) simply has none -- read it as an
    # unqualified task rather than requiring a migration.
    if not raw:
        return Prerequisites.none()
    return Prerequisites.of(TaskId(value) for value in raw)


def _assignee_to_row(assignee: Optional[AssigneeRef]) -> Optional[Dict[str, str]]:
    if assignee is None:
        return None
    return {"kind": assignee.kind.value, "id": assignee.id_value}


def _assignee_from_row(raw: Any) -> Optional[AssigneeRef]:
    # The tagged form written since stage 2.
    if isinstance(raw, dict):
        return AssigneeRef(kind=AssigneeKind(raw["kind"]), id_value=raw["id"])
    # Back-compat: a stage-1 store wrote a bare id string, which meant a member.
    # Read it as a member assignment -- no migration step is needed.
    if isinstance(raw, str):
        return AssigneeRef.member(MemberId(raw))
    return None
