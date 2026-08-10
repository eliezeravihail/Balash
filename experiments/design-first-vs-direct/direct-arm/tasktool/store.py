"""Persistence for tasks and agents.

A store owns some on-disk representation and nothing else: it reads and writes
a :class:`State` snapshot through the :class:`TaskStore` interface. Business
rules live in the manager, which never knows which concrete store backs it.

This module holds the shared :class:`State`, the :class:`TaskStore` contract,
and the JSON-file implementation. The SQLite implementation lives in
``sqlite_store.py`` and satisfies the same contract.
"""

from __future__ import annotations

import abc
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .models import Agent, Task

SCHEMA_VERSION = 2


@dataclass
class State:
    """The complete persisted state: tasks, agents, and their id counters."""

    tasks: dict[int, Task] = field(default_factory=dict)
    next_id: int = 1
    agents: dict[str, Agent] = field(default_factory=dict)
    next_agent_seq: int = 1


class TaskStore(abc.ABC):
    """The storage boundary the manager depends on.

    A store loads the entire state and persists the entire state. Everything the
    product needs -- tasks, human/agent assignment, execution history -- rides
    inside :class:`State`, so a new backend only has to translate that snapshot
    to and from its own format.
    """

    @abc.abstractmethod
    def load(self) -> State:
        """Return the persisted state, or an empty State if nothing is stored."""

    @abc.abstractmethod
    def save(self, state: State) -> None:
        """Persist the given state, replacing whatever was there before."""


class JsonTaskStore(TaskStore):
    """Reads/writes the whole :class:`State` as one JSON document.

    Writes are atomic (temp file + ``os.replace``) so a crash mid-write cannot
    corrupt an existing data file.
    """

    def __init__(self, path: os.PathLike | str) -> None:
        self.path = Path(path)

    def load(self) -> State:
        if not self.path.exists():
            return State()
        with self.path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)

        tasks = {t["id"]: Task.from_dict(t) for t in raw.get("tasks", [])}
        agents = {a["id"]: Agent.from_dict(a) for a in raw.get("agents", [])}
        next_id = raw.get("next_id", max(tasks, default=0) + 1)
        next_agent_seq = raw.get("next_agent_seq", len(agents) + 1)
        return State(
            tasks=tasks,
            next_id=next_id,
            agents=agents,
            next_agent_seq=next_agent_seq,
        )

    def save(self, state: State) -> None:
        payload = {
            "version": SCHEMA_VERSION,
            "next_id": state.next_id,
            "next_agent_seq": state.next_agent_seq,
            "tasks": [task.to_dict() for task in state.tasks.values()],
            "agents": [agent.to_dict() for agent in state.agents.values()],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._atomic_write(json.dumps(payload, indent=2, ensure_ascii=False))

    def _atomic_write(self, text: str) -> None:
        directory = self.path.parent
        fd, tmp_name = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, self.path)
        except BaseException:
            # Best-effort cleanup; never leave a stray temp file on failure.
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)
            raise
