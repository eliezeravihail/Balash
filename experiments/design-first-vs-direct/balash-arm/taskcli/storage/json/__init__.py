"""The JSON storage backend -- one implementation of the storage contract.

Four repositories, each owning one file and the mapping between domain objects and
their stored rows, plus the ``JsonStorage`` aggregate that vends them from a data
directory. Nothing outside this subpackage knows the on-disk JSON format.
"""

from .agent_repository import JsonAgentRepository
from .backend import JsonStorage
from .member_repository import JsonMemberRepository
from .result_repository import JsonResultRepository
from .task_repository import JsonTaskRepository

__all__ = [
    "JsonStorage",
    "JsonAgentRepository",
    "JsonMemberRepository",
    "JsonResultRepository",
    "JsonTaskRepository",
]
