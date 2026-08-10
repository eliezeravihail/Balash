"""Domain model for the task manager.

Everything here is pure data + rules; it knows nothing about disk or the CLI.
The dataclasses carry their own JSON-friendly (de)serialization so the storage
layer can stay format-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional, Union


class Status(Enum):
    """The workflow states a task moves through, in order.

    The declaration order is the workflow order: TODO -> IN_PROGRESS -> DONE.
    A task advances one step at a time and never skips or regresses.
    """

    TODO = "todo"
    IN_PROGRESS = "in progress"
    DONE = "done"

    @classmethod
    def from_value(cls, value: str) -> "Status":
        for status in cls:
            if status.value == value:
                return status
        raise ValueError(f"Unknown status: {value!r}")

    def is_terminal(self) -> bool:
        return self is _SEQUENCE[-1]

    def next(self) -> "Status":
        """Return the following status in the workflow.

        Raises ValueError if the task is already in the terminal status.
        """
        index = _SEQUENCE.index(self)
        if index + 1 >= len(_SEQUENCE):
            raise ValueError(
                f"Task is already '{self.value}' and cannot advance further"
            )
        return _SEQUENCE[index + 1]


# Ordered once, reused by Status.next()/is_terminal().
_SEQUENCE = list(Status)


# --------------------------------------------------------------------------
# Assignees: a task can be assigned to a human member or an AI agent.
# These are a small tagged union; the "kind" discriminator is what gets
# persisted so the two shapes can be told apart on load.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class HumanAssignee:
    """A human team member as recorded on a task.

    ``member_id`` is the stable identifier; ``display_name`` is whatever name
    the team lead typed at the moment of assignment and is snapshotted here.
    """

    member_id: str
    display_name: str
    KIND = "human"

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.KIND,
            "member_id": self.member_id,
            "display_name": self.display_name,
        }


@dataclass(frozen=True)
class AgentAssignee:
    """A reference to an AI agent entity that a task is assigned to.

    Only the agent id is stored here; the agent's provider/model live on the
    Agent entity itself and are looked up when needed.
    """

    agent_id: str
    KIND = "agent"

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.KIND, "agent_id": self.agent_id}


Assignee = Union[HumanAssignee, AgentAssignee]


def assignee_from_dict(data: Optional[dict[str, Any]]) -> Optional[Assignee]:
    if data is None:
        return None
    # Stage-1 files had no "kind" key and were always human.
    kind = data.get("kind", HumanAssignee.KIND)
    if kind == HumanAssignee.KIND:
        return HumanAssignee(data["member_id"], data["display_name"])
    if kind == AgentAssignee.KIND:
        return AgentAssignee(data["agent_id"])
    raise ValueError(f"Unknown assignee kind: {kind!r}")


# --------------------------------------------------------------------------
# AI agents and their execution results.
# --------------------------------------------------------------------------


@dataclass
class Agent:
    """A persisted AI agent. Provider and model are properties of the agent."""

    id: str
    provider: str
    model: str

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "provider": self.provider, "model": self.model}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Agent":
        return cls(id=data["id"], provider=data["provider"], model=data["model"])


@dataclass
class ExecutionResult:
    """The outcome of one agent execution of a task.

    Records exactly what the product asks for: which task, which agent,
    whether it succeeded, and the text output produced.
    """

    task_id: int
    agent_id: str
    success: bool
    output: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "success": self.success,
            "output": self.output,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionResult":
        return cls(
            task_id=data["task_id"],
            agent_id=data["agent_id"],
            success=data["success"],
            output=data["output"],
        )


# --------------------------------------------------------------------------
# Tasks.
# --------------------------------------------------------------------------


@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    status: Status = Status.TODO
    assignee: Optional[Assignee] = None
    executions: List[ExecutionResult] = field(default_factory=list)
    # Ids of tasks that must be "done" before this one is workable. Set at
    # creation only; the manager validates existence and rejects cycles. A task
    # is a plain data holder here -- the ready/blocked rule needs the other
    # tasks' statuses and so lives in the manager.
    prerequisites: List[int] = field(default_factory=list)

    def assign_human(self, member_id: str, display_name: str) -> None:
        """(Re)assign this task to a human, snapshotting the name given now."""
        self.assignee = HumanAssignee(member_id=member_id, display_name=display_name)

    def assign_agent(self, agent_id: str) -> None:
        """(Re)assign this task to an AI agent by id."""
        self.assignee = AgentAssignee(agent_id=agent_id)

    def advance(self) -> None:
        """Move this task one step forward in the workflow."""
        self.status = self.status.next()

    def record_execution(self, result: ExecutionResult) -> None:
        """Append an execution result, retaining all prior history."""
        self.executions.append(result)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "assignee": self.assignee.to_dict() if self.assignee else None,
            "executions": [e.to_dict() for e in self.executions],
            "prerequisites": list(self.prerequisites),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=Status.from_value(data["status"]),
            assignee=assignee_from_dict(data.get("assignee")),
            executions=[
                ExecutionResult.from_dict(e) for e in data.get("executions", [])
            ],
            prerequisites=list(data.get("prerequisites", [])),
        )
