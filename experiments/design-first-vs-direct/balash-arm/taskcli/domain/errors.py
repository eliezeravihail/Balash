"""Domain-level errors.

These describe things that can go wrong in terms of the *concepts* a user works
with (tasks, members, statuses) -- never in terms of how anything is stored.
The CLI turns them into messages a person can act on.
"""


class DomainError(Exception):
    """Base for every rule the domain enforces about its own concepts."""


class InvalidTitleError(DomainError):
    """A task was asked to exist without the title a task requires."""


class InvalidStatusError(DomainError):
    """A value that is not one of the three real task statuses was supplied."""


class UnknownMemberError(DomainError):
    """A task was asked to be assigned to a member the team does not know."""


class UnknownAgentError(DomainError):
    """A task was asked to point at, or be run by, an agent the registry does not know."""


class TaskNotExecutableError(DomainError):
    """A task that cannot be executed (unassigned, or assigned to a human) was asked
    to run. Only agent-assigned tasks can be executed."""


class TaskNotFoundError(DomainError):
    """A task id that no task answers to was used."""
