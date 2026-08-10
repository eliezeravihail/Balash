"""Business operations for the task manager.

:class:`TaskManager` is the single entry point the CLI (or any other caller)
uses. It loads state from a store, applies operations, and persists after every
mutation so that state survives a process restart (write-through).
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .models import (
    Agent,
    AgentAssignee,
    ExecutionResult,
    HumanAssignee,
    Status,
    Task,
)
from .store import State, TaskStore

# A runner turns "this agent runs this task" into an outcome: (success, output).
# The manager wraps that in an ExecutionResult so task/agent ids stay consistent.
# This one seam is what a real provider integration would replace later; the
# default is a deterministic stub because there is no provider to call here.
AgentRunner = Callable[[Agent, Task], Tuple[bool, str]]


def default_runner(agent: Agent, task: Task) -> Tuple[bool, str]:
    return True, (
        f"[{agent.provider}/{agent.model}] executed task {task.id}: {task.title}"
    )


class PrerequisiteError(ValueError):
    """Raised when a task's prerequisites are unknown or would form a cycle."""


def _reaches(starts: Iterable[int], target: int, edges: Dict[int, Sequence[int]]) -> bool:
    """True if `target` is reachable from any node in `starts` following edges.

    Used for cycle detection: a new task -> prereq edge set introduces a cycle
    exactly when one of its prerequisites can reach the new task's id.
    """
    stack = list(starts)
    seen: set[int] = set()
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack.extend(edges.get(node, ()))
    return False


class TaskNotFoundError(KeyError):
    """Raised when an operation references a task id that does not exist."""

    def __init__(self, task_id: int) -> None:
        super().__init__(task_id)
        self.task_id = task_id

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"No task with id {self.task_id}"


class AgentNotFoundError(KeyError):
    """Raised when an operation references an agent id that does not exist."""

    def __init__(self, agent_id: str) -> None:
        super().__init__(agent_id)
        self.agent_id = agent_id

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"No agent with id {self.agent_id}"


class TaskManager:
    def __init__(
        self, store: TaskStore, runner: AgentRunner = default_runner
    ) -> None:
        self._store = store
        self._runner = runner
        self._state: State = store.load()

    # -- queries ---------------------------------------------------------

    def list_tasks(self) -> List[Task]:
        """All tasks, ordered by id (creation order)."""
        return [self._state.tasks[i] for i in sorted(self._state.tasks)]

    def get(self, task_id: int) -> Task:
        try:
            return self._state.tasks[task_id]
        except KeyError:
            raise TaskNotFoundError(task_id) from None

    def list_agents(self) -> List[Agent]:
        return list(self._state.agents.values())

    def get_agent(self, agent_id: str) -> Agent:
        try:
            return self._state.agents[agent_id]
        except KeyError:
            raise AgentNotFoundError(agent_id) from None

    def assignee_label(self, task: Task) -> str:
        """Human-readable rendering of a task's assignee for listings."""
        assignee = task.assignee
        if assignee is None:
            return "(unassigned)"
        if isinstance(assignee, HumanAssignee):
            return assignee.display_name
        if isinstance(assignee, AgentAssignee):
            agent = self._state.agents.get(assignee.agent_id)
            if agent is None:
                return f"{assignee.agent_id} [unknown agent]"
            return f"{agent.id} [{agent.provider}/{agent.model}]"
        raise AssertionError(f"Unhandled assignee type: {assignee!r}")

    # -- task commands ---------------------------------------------------

    def create_task(
        self,
        title: str,
        description: str = "",
        prerequisites: Optional[Sequence[int]] = None,
    ) -> Task:
        if not title or not title.strip():
            raise ValueError("Task title must not be empty")
        new_id = self._state.next_id
        prereqs = self._validate_prerequisites(new_id, prerequisites)
        task = Task(
            id=new_id,
            title=title,
            description=description,
            prerequisites=prereqs,
        )
        self._state.tasks[task.id] = task
        self._state.next_id += 1
        self._persist()
        return task

    def _validate_prerequisites(
        self, new_id: int, prerequisites: Optional[Sequence[int]]
    ) -> List[int]:
        if not prerequisites:
            return []
        # De-duplicate while preserving order.
        prereqs = list(dict.fromkeys(prerequisites))
        unknown = [p for p in prereqs if p != new_id and p not in self._state.tasks]
        if unknown:
            raise PrerequisiteError(
                f"unknown prerequisite task ids: {', '.join(map(str, unknown))}"
            )
        # A cycle appears iff a prerequisite can (transitively) reach the new
        # task. Include the new task's own edges so a self-reference is caught.
        edges: Dict[int, Sequence[int]] = {
            tid: t.prerequisites for tid, t in self._state.tasks.items()
        }
        edges[new_id] = prereqs
        if _reaches(prereqs, new_id, edges):
            raise PrerequisiteError(
                "prerequisites would introduce a dependency cycle"
            )
        return prereqs

    # -- readiness (the blocked/ready rule) ------------------------------

    def unmet_prerequisites(self, task: Task) -> List[int]:
        """Prerequisite ids that are not yet 'done', in the task's own order."""
        return [
            p
            for p in task.prerequisites
            if self._state.tasks[p].status is not Status.DONE
        ]

    def is_ready(self, task: Task) -> bool:
        """A task is ready when all its prerequisites are done (or it has none)."""
        return not self.unmet_prerequisites(task)

    def assign(self, task_id: int, member_id: str, display_name: str) -> Task:
        """Assign a task to a human member (stage-1 behavior)."""
        if not member_id or not member_id.strip():
            raise ValueError("member_id must not be empty")
        if not display_name or not display_name.strip():
            raise ValueError("display_name must not be empty")
        task = self.get(task_id)
        task.assign_human(member_id, display_name)
        self._persist()
        return task

    def assign_agent(self, task_id: int, agent_id: str) -> Task:
        """Assign a task to an AI agent (validated to exist)."""
        task = self.get(task_id)
        self.get_agent(agent_id)  # raises AgentNotFoundError if missing
        task.assign_agent(agent_id)
        self._persist()
        return task

    def advance(self, task_id: int) -> Task:
        """Move a task one step forward: todo -> in progress -> done."""
        task = self.get(task_id)
        task.advance()
        self._persist()
        return task

    # -- agent commands --------------------------------------------------

    def create_agent(self, provider: str, model: str) -> Agent:
        if not provider or not provider.strip():
            raise ValueError("provider must not be empty")
        if not model or not model.strip():
            raise ValueError("model must not be empty")
        agent_id = f"agent-{self._state.next_agent_seq}"
        agent = Agent(id=agent_id, provider=provider, model=model)
        self._state.agents[agent.id] = agent
        self._state.next_agent_seq += 1
        self._persist()
        return agent

    def execute(
        self,
        task_id: int,
        agent_id: str,
        runner: Optional[AgentRunner] = None,
    ) -> ExecutionResult:
        """Have an agent execute a task; append the result to task history.

        Execution is independent of assignment: any existing agent may execute
        any existing task. The result is appended, never overwritten.
        """
        task = self.get(task_id)
        agent = self.get_agent(agent_id)
        success, output = (runner or self._runner)(agent, task)
        result = ExecutionResult(
            task_id=task.id, agent_id=agent.id, success=success, output=output
        )
        task.record_execution(result)
        self._persist()
        return result

    # -- internals -------------------------------------------------------

    def _persist(self) -> None:
        self._store.save(self._state)
