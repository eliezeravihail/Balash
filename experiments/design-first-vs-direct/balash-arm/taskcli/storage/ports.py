"""The storage contract -- the ports the service and composition root depend on.

These are the whole vocabulary the rest of the program uses to talk about
persistence. Nothing above this file knows whether tasks live in a JSON file or a
SQLite table; it knows only these method names, all phrased in domain terms. Two real
implementations sit behind the contract (``storage/json`` and ``storage/sqlite``), and
the composition root picks one at startup.

The ports are ``typing.Protocol``s -- structural, so the concrete repositories satisfy
them without inheriting anything and without creating an import cycle (the ports live in
``storage``; the implementations live under it). No path, row, table, column, or SQL
type appears in any signature: only domain objects and domain errors cross this
boundary.

Four narrow per-entity ports are what the *services* depend on -- each service takes
only the repositories it actually calls, so no service is forced to depend on a method
it never uses. One aggregate ``StorageBackend`` is what the *composition root* selects
and holds; it vends the four repositories that share a backend's resources (for SQLite,
one connection and one schema-initialization step; for JSON, four independent files).
"""

from __future__ import annotations

from typing import List, Protocol

from ..domain import (
    Agent,
    AgentRegistry,
    ExecutionResult,
    Member,
    Task,
    TaskId,
    Team,
)


class TaskRepository(Protocol):
    """Where tasks are kept, in domain terms."""

    def add(self, task: Task) -> None:
        """Store a brand-new task."""
        ...

    def save(self, task: Task) -> None:
        """Persist changes to a task that already exists.

        Raises ``TaskNotFoundError`` if no task with that id is stored.
        """
        ...

    def get(self, task_id: TaskId) -> Task:
        """The task with this id, or ``TaskNotFoundError`` if none answers to it."""
        ...

    def all(self) -> List[Task]:
        """Every stored task."""
        ...


class MemberRepository(Protocol):
    """Where the team roster is kept."""

    def add(self, member: Member) -> None:
        """Store a member, upserting by id -- re-adding an id updates the name and
        leaves exactly one member."""
        ...

    def team(self) -> Team:
        """Vend the whole roster as the Team authority."""
        ...


class AgentRepository(Protocol):
    """Where the agent registry is kept."""

    def add(self, agent: Agent) -> None:
        """Store an agent, upserting by id -- re-registering is idempotent."""
        ...

    def registry(self) -> AgentRegistry:
        """Vend every agent as the AgentRegistry authority."""
        ...


class ResultRepository(Protocol):
    """Where execution results are kept -- an append-only history."""

    def append(self, result: ExecutionResult) -> None:
        """Record one more execution result. Append-only -- never overwrites."""
        ...

    def for_task(self, task_id: TaskId) -> List[ExecutionResult]:
        """Every result for a task, oldest first (chronological)."""
        ...


class StorageBackend(Protocol):
    """One selected backend; vends the four repositories that share its resources.

    This is the thing the composition root selects and holds. Selecting a backend is
    choosing which ``StorageBackend`` to build; the choice never travels past the root,
    because everything downstream holds a repository port, never a backend name.
    """

    def tasks(self) -> TaskRepository:
        ...

    def members(self) -> MemberRepository:
        ...

    def agents(self) -> AgentRepository:
        ...

    def results(self) -> ResultRepository:
        ...
