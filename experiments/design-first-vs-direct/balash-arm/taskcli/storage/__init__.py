"""The persistence boundary.

This package defines one storage *contract* -- four narrow per-entity repository ports
plus one aggregate ``StorageBackend`` -- and two real implementations behind it: the
JSON store (the default) and a SQLite store. The services depend only on the ports; the
composition root selects one aggregate at startup. Nothing above this package knows
which backend is live, and no file name, table name, column name, or SQL string ever
crosses out of it.

The bare names ``TaskRepository``, ``MemberRepository``, ``AgentRepository``,
``ResultRepository`` are the *ports* (structural ``Protocol``s); the concrete classes
state their backend in their names (``Json*`` / ``Sqlite*``).
"""

from .ports import (
    AgentRepository,
    MemberRepository,
    ResultRepository,
    StorageBackend,
    TaskRepository,
)
from .json import JsonStorage
from .sqlite import SqliteStorage

__all__ = [
    # the contract
    "TaskRepository",
    "MemberRepository",
    "AgentRepository",
    "ResultRepository",
    "StorageBackend",
    # the two implementations' aggregates
    "JsonStorage",
    "SqliteStorage",
]
