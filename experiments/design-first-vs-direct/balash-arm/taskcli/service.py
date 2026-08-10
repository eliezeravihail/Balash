"""The application service: the thin seam between the outside world and the domain.

It sequences the small steps a use case needs -- load, tell a domain object to do
something, save -- but it holds no rules of its own. Every rule it appears to apply
actually lives in a domain object it calls: the title rule is the Task's, the "known
member" rule is the Team's, the "known agent" rule is the AgentRegistry's, the status
rule is the Task's. If you deleted this class the rules would still be intact; only the
wiring would be gone.

It also builds the read-models (TaskView) the CLI prints, so the id-to-name resolution
needed for display happens once here rather than being re-derived by whatever wants to
show a task. Since stage 2 an assignee may be a member or an agent, so the resolver
routes by the reference's kind to the matching authority, and tolerates a stale/removed
assignee of either kind.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet, Iterable, List, Optional, Tuple

from .domain import (
    Agent,
    AgentId,
    AssigneeRef,
    Member,
    MemberId,
    Prerequisites,
    Status,
    Task,
    TaskId,
)
from .storage import AgentRepository, MemberRepository, TaskRepository


@dataclass(frozen=True)
class TaskView:
    """A task as it should be shown to a person: ids as text, the assignee already
    resolved to a display name, and the blocked/ready state already decided. A
    read-only presentation record -- it carries no behaviour because showing a task is
    not a domain decision."""

    id: str
    title: str
    description: str
    status: str
    assignee: str  # a display name, or "unassigned"
    readiness: str = "ready"  # "ready" or "blocked", per the prerequisite rule
    prerequisites: Tuple[str, ...] = ()  # the task ids this task waits on, as text


class TaskService:
    def __init__(
        self,
        tasks: TaskRepository,
        members: MemberRepository,
        agents: AgentRepository,
    ) -> None:
        self._tasks = tasks
        self._members = members
        self._agents = agents

    # --- members ---

    def add_member(self, member_id: str, display_name: str) -> Member:
        member = Member(id=MemberId(member_id), display_name=display_name)
        self._members.add(member)
        return member

    def roster(self) -> List[Member]:
        return self._members.team().roster()

    # --- agents ---

    def add_agent(
        self, agent_id: str, provider: str, model: str, display_name: str
    ) -> Agent:
        agent = Agent(
            id=AgentId(agent_id),
            display_name=display_name,
            provider_name=provider,
            model_name=model,
        )
        self._agents.add(agent)
        return agent

    def agents(self) -> List[Agent]:
        return self._agents.registry().roster()

    # --- tasks: commands ---

    def create_task(
        self, title: str, description: str, needs: Iterable[str] = ()
    ) -> TaskId:
        # Prerequisites are set here, at creation, and never after. Every referenced id
        # must already be a real task -- the one rule that both keeps readiness
        # well-defined and (because a fresh task's own id is never among the existing
        # ones) guarantees the prerequisite graph stays acyclic. The gate lives on
        # Prerequisites; this is the single path that reaches it.
        prerequisites = Prerequisites.of(TaskId(need) for need in needs)
        prerequisites.require_all_known({task.id for task in self._tasks.all()})
        task = Task.create(
            title=title, description=description, prerequisites=prerequisites
        )
        self._tasks.add(task)
        return task.id

    def assign_task(self, task_id: str, member_id: str) -> None:
        # The team is the one gate that decides a member is real; asking it here is
        # what makes "no assigning to unknown members" true for every assign path.
        member = self._members.team().member(MemberId(member_id))
        task = self._tasks.get(TaskId(task_id))
        task.assign_to(AssigneeRef.member(member.id))
        self._tasks.save(task)

    def assign_task_to_agent(self, task_id: str, agent_id: str) -> None:
        # The registry is the one gate that decides an agent is real -- symmetric with
        # the member path; the only new thing is wrapping the id in an AssigneeRef.
        agent = self._agents.registry().agent(AgentId(agent_id))
        task = self._tasks.get(TaskId(task_id))
        task.assign_to(AssigneeRef.agent(agent.id))
        self._tasks.save(task)

    def unassign_task(self, task_id: str) -> None:
        task = self._tasks.get(TaskId(task_id))
        task.unassign()
        self._tasks.save(task)

    def change_status(self, task_id: str, status: str) -> None:
        task = self._tasks.get(TaskId(task_id))
        task.change_status(Status.parse(status))
        self._tasks.save(task)

    # --- tasks: queries ---

    def list_tasks(self) -> List[TaskView]:
        team = self._members.team()
        registry = self._agents.registry()
        all_tasks = self._tasks.all()
        completed = self._completed_ids(all_tasks)
        return [self._view(task, team, registry, completed) for task in all_tasks]

    def show_task(self, task_id: str) -> TaskView:
        team = self._members.team()
        registry = self._agents.registry()
        completed = self._completed_ids(self._tasks.all())
        # get() (not a scan of all_tasks) so a missing id still raises TaskNotFoundError.
        task = self._tasks.get(TaskId(task_id))
        return self._view(task, team, registry, completed)

    @staticmethod
    def _completed_ids(tasks: Iterable[Task]) -> AbstractSet[TaskId]:
        """Which tasks are done -- the only world knowledge the readiness rule needs.
        Built once per read so every task in a listing is judged against the same
        snapshot."""
        return {task.id for task in tasks if task.status is Status.DONE}

    def _view(
        self, task: Task, team, registry, completed: AbstractSet[TaskId]
    ) -> TaskView:
        return TaskView(
            id=task.id.value,
            title=task.title,
            description=task.description,
            status=task.status.label,
            assignee=self._assignee_label(task.assignee, team, registry),
            readiness=task.readiness(completed).label,
            prerequisites=tuple(str(prereq) for prereq in task.prerequisites),
        )

    @staticmethod
    def _assignee_label(
        assignee: Optional[AssigneeRef], team, registry
    ) -> str:
        if assignee is None:
            return "unassigned"
        if not assignee.is_agent:
            # MEMBER -- unchanged stage-1 behaviour, including the tolerance for a
            # member removed after a task was assigned to them.
            member_id = assignee.as_member_id()
            if team.knows(member_id):
                return team.display_name_for(member_id)
            return f"{member_id.value} (unknown member)"
        # AGENT -- the symmetric new tolerance: a removed agent renders rather than
        # crashing a read.
        agent_id = assignee.as_agent_id()
        if registry.knows(agent_id):
            return registry.display_name_for(agent_id)
        return f"{agent_id.value} (unknown agent)"
