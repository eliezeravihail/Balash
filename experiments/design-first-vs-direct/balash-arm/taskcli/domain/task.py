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

from typing import Optional

from .assignee import AssigneeRef
from .errors import InvalidStatusError, InvalidTitleError
from .ids import TaskId
from .status import Status


class Task:
    def __init__(
        self,
        task_id: TaskId,
        title: str,
        description: str,
        status: Status,
        assignee: Optional[AssigneeRef],
    ) -> None:
        # Every way a task comes into being -- freshly created or rebuilt from
        # storage -- passes through here, so the title invariant holds for all of
        # them, not just the create() path.
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

    @classmethod
    def create(cls, title: str, description: str) -> "Task":
        """Bring a brand-new task into existence: fresh id, starts in todo,
        unassigned. The only entry point callers use to make a new task."""
        return cls(
            task_id=TaskId.new(),
            title=title,
            description=description,
            status=Status.TODO,
            assignee=None,
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
