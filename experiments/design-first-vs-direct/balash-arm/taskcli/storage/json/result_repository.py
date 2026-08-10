"""Where execution results are kept -- the JSON implementation of ``ResultRepository``.

The JSON persistence boundary for execution results, and the only place that knows they
live in a JSON file or under what field names. A result is a historical fact, so this
store only ever *appends*: re-running an execution adds another row and never touches
the ones already written. Rows come back in append order, which is chronological.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ...domain import AgentId, ExecutionResult, TaskId
from .. import _jsonfile


class JsonResultRepository:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def append(self, result: ExecutionResult) -> None:
        """Record one more execution result. Append-only -- prior results are kept."""
        rows = _jsonfile.read_rows(self._path)
        rows.append(_to_row(result))
        _jsonfile.write_rows(self._path, rows)

    def for_task(self, task_id: TaskId) -> List[ExecutionResult]:
        """Every result for a task, in the order it was recorded (chronological)."""
        return [
            _from_row(row)
            for row in _jsonfile.read_rows(self._path)
            if row["task_id"] == task_id.value
        ]


def _to_row(result: ExecutionResult) -> Dict[str, Any]:
    return {
        "task_id": result.task_id.value,
        "agent_id": result.agent_id.value,
        "succeeded": result.succeeded,
        "output": result.output,
    }


def _from_row(row: Dict[str, Any]) -> ExecutionResult:
    return ExecutionResult(
        task_id=TaskId(row["task_id"]),
        agent_id=AgentId(row["agent_id"]),
        succeeded=row["succeeded"],
        output=row["output"],
    )
