"""The tasks a task must wait on -- a first-class concept, and the single owner of the
prerequisite rules.

A task may depend on other tasks: it is not workable until every task it depends on is
done. ``Prerequisites`` is the set of those task references a task holds, and it is the
one place two rules about that set live, so no caller re-implements either:

1. **Validity at creation (the acyclicity guarantee).** Every prerequisite must
   reference a task that *already exists*. ``require_all_known`` enforces that, and that
   single rule is exactly what makes a prerequisite cycle impossible -- see the note
   below. It is the only guard the invariant needs.

2. **Readiness.** A task is READY when every task it depends on is done, and BLOCKED
   otherwise. ``readiness`` decides that from the set of done task ids it is handed.
   Readiness is derived on every ask, never stored, so nothing can leave a task marked
   "ready" out of step with its prerequisites' real statuses.

Why no cycle-detection machinery (DFS / graph colouring) is built
-----------------------------------------------------------------
Prerequisites are set at creation time only and are immutable afterward, and each one
must reference a task that already exists (rule 1). A task's own id is minted fresh at
creation, so it is not among the existing ids the new task's prerequisites are checked
against -- a task cannot even name itself. Every prerequisite edge therefore points from
a newer task strictly back to an older one; "was created before" is a topological order
the graph can never contradict, because the only entry point (creation) can only add
edges in that one direction and no path ever edits them later. A cycle would need an
edge from an older task to a newer one, which no code path can produce. So a DFS cycle
check would be machinery guarding against a state the structure already makes
unreachable -- the wrong abstraction. The invariant is honoured by enforcing the one
rule that actually keeps the graph acyclic (existence-at-creation), in one place, rather
than by detecting a shape that cannot form.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet, Iterable, Iterator, List, Tuple

from .errors import UnknownPrerequisiteError
from .ids import TaskId
from .readiness import Readiness


@dataclass(frozen=True)
class Prerequisites:
    ids: Tuple[TaskId, ...]  # the tasks that must be done first; deduped, order kept

    @classmethod
    def none(cls) -> "Prerequisites":
        """No prerequisites -- the common case, and what an unqualified task has."""
        return cls(())

    @classmethod
    def of(cls, task_ids: Iterable[TaskId]) -> "Prerequisites":
        """Build prerequisites from task ids, dropping duplicates while preserving the
        order they were first named in (so display is stable)."""
        unique: List[TaskId] = []
        for task_id in task_ids:
            if task_id not in unique:
                unique.append(task_id)
        return cls(tuple(unique))

    @property
    def is_empty(self) -> bool:
        return not self.ids

    def __iter__(self) -> Iterator[TaskId]:
        return iter(self.ids)

    def __len__(self) -> int:
        return len(self.ids)

    def require_all_known(self, existing: AbstractSet[TaskId]) -> None:
        """Refuse unless every prerequisite references a task that already exists.

        This is the single gate the acyclicity invariant funnels through: because a new
        task's id is never among ``existing`` at its own creation, this both rejects a
        task naming itself and guarantees every prerequisite edge points back to an
        older task, so no cycle can form. Raises ``UnknownPrerequisiteError`` naming the
        offending ids.
        """
        missing = [task_id for task_id in self.ids if task_id not in existing]
        if missing:
            named = ", ".join(repr(task_id.value) for task_id in missing)
            raise UnknownPrerequisiteError(
                f"these prerequisites are not existing tasks: {named}; "
                "a task can only depend on tasks that already exist"
            )

    def readiness(self, completed: AbstractSet[TaskId]) -> Readiness:
        """READY iff every prerequisite is among the done tasks, else BLOCKED. With no
        prerequisites this is vacuously READY. The one place the blocked/ready rule
        lives; callers hand in which task ids are done and are told the answer."""
        if all(task_id in completed for task_id in self.ids):
            return Readiness.READY
        return Readiness.BLOCKED
