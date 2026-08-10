"""The domain: the product's core concepts and the rules they own.

Nothing in this package knows how anything is stored, printed, parsed from a command
line, or run over a network. It speaks only in tasks, members, agents, statuses,
assignments, execution results, and ids.
"""

from .agent import Agent, AgentRegistry
from .assignee import AssigneeKind, AssigneeRef
from .errors import (
    DomainError,
    InvalidStatusError,
    InvalidTitleError,
    TaskNotExecutableError,
    TaskNotFoundError,
    UnknownAgentError,
    UnknownMemberError,
)
from .execution_result import ExecutionResult
from .ids import AgentId, MemberId, TaskId
from .member import Member, Team
from .status import Status
from .task import Task

__all__ = [
    "DomainError",
    "InvalidStatusError",
    "InvalidTitleError",
    "TaskNotExecutableError",
    "TaskNotFoundError",
    "UnknownAgentError",
    "UnknownMemberError",
    "AgentId",
    "MemberId",
    "TaskId",
    "Agent",
    "AgentRegistry",
    "AssigneeKind",
    "AssigneeRef",
    "ExecutionResult",
    "Member",
    "Team",
    "Status",
    "Task",
]
