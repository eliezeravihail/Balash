"""Who a task is assigned to -- as a reference the task holds opaquely.

A task no longer holds a bare member id. It holds an ``AssigneeRef``: "whoever this
task is assigned to, which may be a member or an agent." The reference has meaning, a
validity rule (a non-blank id) and a closed notion of *kind* -- but it resolves no
names and runs nothing. It is a value object, deliberately not a behavioural
interface: the task carries it without ever branching on the kind, and the two
authorities (Team, AgentRegistry) resolve the two kinds side by side.

The reference answers exactly one small question about *itself* -- ``is_agent`` -- so
callers tell-don't-ask rather than pulling ``.kind`` out and comparing. Its typed
accessors (``as_member_id`` / ``as_agent_id``) refuse to hand back an id of the wrong
kind, so a member id can never be mistaken for an agent id or the reverse.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .ids import AgentId, MemberId


class AssigneeKind(Enum):
    """The two -- and only two -- kinds of thing a task may be assigned to."""

    MEMBER = "member"
    AGENT = "agent"


@dataclass(frozen=True)
class AssigneeRef:
    kind: AssigneeKind
    id_value: str  # the underlying MemberId/AgentId value

    def __post_init__(self) -> None:
        if not isinstance(self.kind, AssigneeKind):
            raise ValueError("an assignee kind must be an AssigneeKind")
        if not self.id_value or not self.id_value.strip():
            raise ValueError("an assignee id cannot be blank")

    @classmethod
    def member(cls, member_id: MemberId) -> "AssigneeRef":
        return cls(kind=AssigneeKind.MEMBER, id_value=member_id.value)

    @classmethod
    def agent(cls, agent_id: AgentId) -> "AssigneeRef":
        return cls(kind=AssigneeKind.AGENT, id_value=agent_id.value)

    @property
    def is_agent(self) -> bool:
        """Whether this reference points at an agent -- the executability signal."""
        return self.kind is AssigneeKind.AGENT

    def as_member_id(self) -> MemberId:
        """The member id this reference holds. Refuses if the ref is an agent's --
        the typed accessor never silently returns an id of the wrong kind."""
        if self.kind is not AssigneeKind.MEMBER:
            raise ValueError(
                f"this assignee is a {self.kind.value}, not a member; "
                "ask for the agent id instead"
            )
        return MemberId(self.id_value)

    def as_agent_id(self) -> AgentId:
        """The agent id this reference holds. Refuses if the ref is a member's."""
        if self.kind is not AssigneeKind.AGENT:
            raise ValueError(
                f"this assignee is a {self.kind.value}, not an agent; "
                "ask for the member id instead"
            )
        return AgentId(self.id_value)
