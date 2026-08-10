"""Where the agent registry is kept -- the SQLite implementation of ``AgentRepository``.

The SQLite persistence boundary for agents: one ``agents`` table, one row per agent
carrying its provider and model. ``add`` upserts by id via ``INSERT ... ON CONFLICT(id)
DO UPDATE`` -- idempotent re-registration, mirroring the JSON repo's observable
behavior. ``registry`` vends every agent as the AgentRegistry authority. Callers see
Agents and the AgentRegistry, never a column.
"""

from __future__ import annotations

import sqlite3

from ...domain import Agent, AgentId, AgentRegistry


class SqliteAgentRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def add(self, agent: Agent) -> None:
        self._conn.execute(
            "INSERT INTO agents (id, display_name, provider, model) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET "
            "display_name = excluded.display_name, "
            "provider = excluded.provider, "
            "model = excluded.model",
            (agent.id.value, agent.display_name, agent.provider_name, agent.model_name),
        )
        self._conn.commit()

    def registry(self) -> AgentRegistry:
        """Load every agent as the AgentRegistry -- the object the rest of the program
        asks about agents and executability."""
        rows = self._conn.execute(
            "SELECT id, display_name, provider, model FROM agents ORDER BY rowid"
        ).fetchall()
        return AgentRegistry(_from_row(row) for row in rows)


def _from_row(row: sqlite3.Row) -> Agent:
    return Agent(
        id=AgentId(row["id"]),
        display_name=row["display_name"],
        provider_name=row["provider"],
        model_name=row["model"],
    )
