"""The JSON storage backend -- the aggregate that vends the four JSON repositories.

This is the JSON implementation of the ``StorageBackend`` port. In the JSON world each
repository owns one independent file (``tasks.json``, ``members.json``, ``agents.json``,
``results.json``) under a single ``data_dir``; nothing is shared between them, there is
no connection to open and no schema to create. So this aggregate is a trivial factory:
it hands each repository its file path and vends it.

The four files are the JSON backend's whole world. The composition root holds one of
these and asks it for the repositories the services need, never learning that they are
files -- exactly as it would hold a ``SqliteStorage`` instead.
"""

from __future__ import annotations

from pathlib import Path

from .agent_repository import JsonAgentRepository
from .member_repository import JsonMemberRepository
from .result_repository import JsonResultRepository
from .task_repository import JsonTaskRepository


class JsonStorage:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = Path(data_dir)

    def tasks(self) -> JsonTaskRepository:
        return JsonTaskRepository(self._data_dir / "tasks.json")

    def members(self) -> JsonMemberRepository:
        return JsonMemberRepository(self._data_dir / "members.json")

    def agents(self) -> JsonAgentRepository:
        return JsonAgentRepository(self._data_dir / "agents.json")

    def results(self) -> JsonResultRepository:
        return JsonResultRepository(self._data_dir / "results.json")
