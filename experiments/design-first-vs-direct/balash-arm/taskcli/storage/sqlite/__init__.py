"""The SQLite storage backend -- one implementation of the storage contract.

Four repositories over real tables/rows (stdlib ``sqlite3``, no ORM), the ``schema.py``
that declares the tables once, and the ``SqliteStorage`` aggregate that opens the db,
ensures the schema, and vends the four repos over a shared connection. Nothing outside
this subpackage knows the table/column shape.
"""

from .agent_repository import SqliteAgentRepository
from .backend import SqliteStorage
from .member_repository import SqliteMemberRepository
from .result_repository import SqliteResultRepository
from .task_repository import SqliteTaskRepository

__all__ = [
    "SqliteStorage",
    "SqliteAgentRepository",
    "SqliteMemberRepository",
    "SqliteResultRepository",
    "SqliteTaskRepository",
]
