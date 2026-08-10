"""The SQLite storage backend -- the aggregate that owns the db and vends four repos.

This is the SQLite implementation of the ``StorageBackend`` port, and it is where the
aggregate earns its place: unlike JSON's four independent files, all four SQLite
repositories live in ONE database file and share ONE connection and ONE
schema-initialization step. Owning those shared resources is the aggregate's whole job.
If the composition root built four SQLite repos independently, "which db file, is the
schema created yet, whose connection" would be duplicated four ways -- exactly the
scattered-ownership smell. Here it is owned once: open the db, ensure the schema, hand
each repository the shared connection.

Deliberately no foreign keys are declared (see ``schema.py``): the domain's
read-tolerance requires a task pointing at a since-removed member/agent to still load,
so SQLite is kept exactly as permissive as JSON on dangling references.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .agent_repository import SqliteAgentRepository
from .member_repository import SqliteMemberRepository
from .result_repository import SqliteResultRepository
from .schema import ensure_schema
from .task_repository import SqliteTaskRepository


class SqliteStorage:
    def __init__(self, db_path: Path) -> None:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path))
        self._conn.row_factory = sqlite3.Row
        ensure_schema(self._conn)  # create the tables once, on first use

    def tasks(self) -> SqliteTaskRepository:
        return SqliteTaskRepository(self._conn)

    def members(self) -> SqliteMemberRepository:
        return SqliteMemberRepository(self._conn)

    def agents(self) -> SqliteAgentRepository:
        return SqliteAgentRepository(self._conn)

    def results(self) -> SqliteResultRepository:
        return SqliteResultRepository(self._conn)

    def close(self) -> None:
        """Release the connection. The CLI opens one backend per process and lets the
        process exit close it; tests that build many backends can close explicitly."""
        self._conn.close()
