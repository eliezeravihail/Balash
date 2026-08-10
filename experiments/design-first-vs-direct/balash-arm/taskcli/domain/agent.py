"""AI agents and the registry that knows them.

An Agent pairs a stable id with a display name and the provider/model that identify
*how* it runs. The AgentRegistry is the one authority on which agents exist -- the
exact analog of Team for people -- and it also owns the single gate that decides "only
an agent-assigned task may be executed."

Provider and model belong to the agent, never to a task: a task holds only a reference
to its assignee and stays ignorant of how any agent runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional

from .assignee import AssigneeRef
from .errors import TaskNotExecutableError, UnknownAgentError
from .ids import AgentId


@dataclass(frozen=True)
class Agent:
    id: AgentId
    display_name: str
    provider_name: str  # belongs to the agent, NOT to any task
    model_name: str  # belongs to the agent, NOT to any task

    def __post_init__(self) -> None:
        # One construction funnel -- fresh registration and rebuild-from-storage both
        # pass through here, so "everything non-blank" holds for every Agent.
        if not self.display_name or not self.display_name.strip():
            raise ValueError("an agent needs a display name")
        if not self.provider_name or not self.provider_name.strip():
            raise ValueError("an agent needs a provider name")
        if not self.model_name or not self.model_name.strip():
            raise ValueError("an agent needs a model name")


class AgentRegistry:
    """The set of AI agents work can be assigned to and run by. Ask it to confirm an
    agent, to name one, or to turn an assignment into a runnable Agent; it answers or
    raises. Like Team, it never exposes a way to 'assign' anything."""

    def __init__(self, agents: Iterable[Agent] = ()) -> None:
        self._agents: Dict[AgentId, Agent] = {a.id: a for a in agents}

    def knows(self, agent_id: AgentId) -> bool:
        return agent_id in self._agents

    def agent(self, agent_id: AgentId) -> Agent:
        """Resolve an agent id to the Agent, or refuse. The single reality gate."""
        try:
            return self._agents[agent_id]
        except KeyError:
            raise UnknownAgentError(
                f"no agent has id {agent_id.value!r}; register it first"
            ) from None

    def display_name_for(self, agent_id: AgentId) -> str:
        """The name to show for an agent assignee id."""
        return self.agent(agent_id).display_name

    def require_executable(self, assignment: Optional[AssigneeRef]) -> Agent:
        """The single place 'only an agent-assigned task can be executed' is enforced.

        Refuses an unassigned or human-assigned task (TaskNotExecutableError); refuses
        an agent id it does not know (UnknownAgentError); otherwise returns the Agent,
        which carries the provider/model needed to run it. Every execute path funnels
        through here.
        """
        if assignment is None:
            raise TaskNotExecutableError(
                "this task is unassigned; assign it to an agent before executing it"
            )
        if not assignment.is_agent:
            raise TaskNotExecutableError(
                "this task is assigned to a person, not an agent; only "
                "agent-assigned tasks can be executed"
            )
        return self.agent(assignment.as_agent_id())

    def __iter__(self) -> Iterator[Agent]:
        return iter(self._agents.values())

    def roster(self) -> List[Agent]:
        return list(self._agents.values())
