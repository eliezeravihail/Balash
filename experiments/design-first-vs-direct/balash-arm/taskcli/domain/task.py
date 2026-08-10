"""A task -- the core concept of the product.

A Task is not a bag of fields that other code reaches into and mutates. It owns the
rules about itself: what it takes for a task to exist (a non-blank title), what it
means to assign or unassign it, and how its status changes. Callers *tell* a task to
change ("assign this to Alice", "move this to done") and the task decides how; they do
not pull its fields out and set them from the outside.

What a task deliberately does NOT own: knowledge of who the whole team is, nor which
*kind* of thing it is assigned to. A task holds an opaque reference to whoever it is
assigned to -- a member or an agent -- but "is that assignee real?" and "which kind is
it?" are questions for the authorities and the reference, not the task. So assign_to
takes an already-validated AssigneeRef, and the task never branches on its kind.
Keeping that boundary is what lets the task stay a small, self-contained concept.
"""

from __future__ import annotations

from typing import AbstractSet, Optional

from .assignee import AssigneeRef
from .errors import InvalidStatusError, InvalidTitleError
from .ids import TaskId
from .prerequisites import Prerequisites
from .readiness import Readiness
from .status import Status


class Task:
    def __init__(
        self,
        task_id: TaskId,
        title: str,
        description: str,
        status: Status,
        assignee: Optional[AssigneeRef],
        prerequisites: Optional[Prerequisites] = None,
    ) -> None:
        # Every way a task comes into being -- freshly created or rebuilt from
        # storage -- passes through here, so the title invariant holds for all of
        # them, not just the create() path. Prerequisites default to none, so a task
        # made without them (and any store predating them) is simply unqualified.
        title = title.strip()
        if not title:
            raise InvalidTitleError("a task needs a title")
        if not isinstance(status, Status):
            raise InvalidStatusError("a task status must be a Status")
        self._id = task_id
        self._title = title
        self._description = description
        self._status = status
        self._assignee = assignee
        self._prerequisites = (
            prerequisites if prerequisites is not None else Prerequisites.none()
        )

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        prerequisites: Optional[Prerequisites] = None,
    ) -> "Task":
        """Bring a brand-new task into existence: fresh id, starts in todo,
        unassigned, waiting on the given prerequisites (none by default). The only
        entry point callers use to make a new task. Prerequisites are fixed here, at
        creation -- there is deliberately no way to add or remove one later."""
        return cls(
            task_id=TaskId.new(),
            title=title,
            description=description,
            status=Status.TODO,
            assignee=None,
            prerequisites=prerequisites,
        )

    # --- behaviour: callers tell the task what to do ---

    def assign_to(self, assignee: AssigneeRef) -> None:
        """Put this task in an assignee's hands -- a member or an agent. The caller
        must have obtained a real, already-validated reference from the matching
        authority; the task trusts that and records it, never inspecting its kind."""
        self._assignee = assignee

    def unassign(self) -> None:
        """Return this task to nobody's hands."""
        self._assignee = None

    def change_status(self, status: Status) -> None:
        """Move this task to another status. Every transition among the three is
        allowed by design -- including reopening a done task -- so there is no
        forbidden-transition check here; there is exactly one on purpose."""
        if not isinstance(status, Status):
            raise InvalidStatusError("a task status must be a Status")
        self._status = status

    def readiness(self, completed: AbstractSet[TaskId]) -> Readiness:
        """Whether this task can be worked yet -- READY iff every task it depends on is
        done. The caller supplies which task ids are done, because a task never knows
        the wider world itself; the blocked/ready rule stays owned by Prerequisites, to
        which this simply delegates. Tell the task, don't reach into its prerequisites
        and decide outside it."""
        return self._prerequisites.readiness(completed)

    # --- read-only views of state (for display and persistence mapping) ---

    @property
    def id(self) -> TaskId:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def status(self) -> Status:
        return self._status

    @property
    def assignee(self) -> Optional[AssigneeRef]:
        return self._assignee

    @property
    def is_assigned(self) -> bool:
        return self._assignee is not None

    @property
    def prerequisites(self) -> Prerequisites:
        """The tasks this task waits on -- read-only; they are fixed at creation."""
        return self._prerequisites
