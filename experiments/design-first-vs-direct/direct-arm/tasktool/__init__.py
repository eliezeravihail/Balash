"""A small, single-machine command-line task manager.

Public surface:
    Status, HumanAssignee, AgentAssignee, Task,
    Agent, ExecutionResult           -- domain model (models.py)
    TaskStore, JsonTaskStore,
    SqliteTaskStore                  -- persistence backends (store.py, sqlite_store.py)
    TaskManager                      -- business operations (manager.py)
"""

from .models import (
    Agent,
    AgentAssignee,
    ExecutionResult,
    HumanAssignee,
    Status,
    Task,
)
from .manager import TaskManager
from .sqlite_store import SqliteTaskStore
from .store import JsonTaskStore, TaskStore

__all__ = [
    "Agent",
    "AgentAssignee",
    "ExecutionResult",
    "HumanAssignee",
    "Status",
    "Task",
    "TaskManager",
    "TaskStore",
    "JsonTaskStore",
    "SqliteTaskStore",
]
