"""Where the agent registry is kept -- the JSON implementation of ``AgentRepository``.

The JSON persistence boundary for agents, and the only place that knows agents live in
a JSON file or under what field names. It hands back domain objects: the whole
AgentRegistry assembled from the stored agents. Mirrors JsonMemberRepository -- one
file, one row mapping, over the shared JSON backend.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ...domain import Agent, AgentId, AgentRegistry
from .. import _jsonfile


class JsonAgentRepository:
    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def add(self, agent: Agent) -> None:
        rows = _jsonfile.read_rows(self._path)
        for index, row in enumerate(rows):
            if row["id"] == agent.id.value:
                rows[index] = _to_row(agent)  # re-registering is idempotent
                _jsonfile.write_rows(self._path, rows)
                return
        rows.append(_to_row(agent))
        _jsonfile.write_rows(self._path, rows)

    def registry(self) -> AgentRegistry:
        """Load every agent as the AgentRegistry -- the object the rest of the program
        asks about agents and executability."""
        agents = (_from_row(row) for row in _jsonfile.read_rows(self._path))
        return AgentRegistry(agents)


def _to_row(agent: Agent) -> Dict[str, Any]:
    return {
        "id": agent.id.value,
        "display_name": agent.display_name,
        "provider": agent.provider_name,
        "model": agent.model_name,
    }


def _from_row(row: Dict[str, Any]) -> Agent:
    return Agent(
        id=AgentId(row["id"]),
        display_name=row["display_name"],
        provider_name=row["provider"],
        model_name=row["model"],
    )
