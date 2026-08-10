"""The execution service: the application-layer seam that runs an agent-assigned task.

It has genuinely different collaborators than task/roster orchestration (a provider and
a result store) and a different reason to change, so it is its own service. It holds no
rules of its own: the "only an agent-assigned task can be executed" rule lives on the
AgentRegistry gate it calls, and the provider owns how work runs. Executing a task does
NOT change the task's status -- it produces and records a result, and nothing else.
"""

from __future__ import annotations

from typing import List

from ..domain import ExecutionResult, TaskId
from ..storage import AgentRepository, ResultRepository, TaskRepository
from .provider import ExecutionRequest, Provider


class ExecutionService:
    def __init__(
        self,
        tasks: TaskRepository,
        agents: AgentRepository,
        results: ResultRepository,
        provider: Provider,
    ) -> None:
        self._tasks = tasks
        self._agents = agents
        self._results = results
        self._provider = provider

    def execute(self, task_id: str) -> ExecutionResult:
        task = self._tasks.get(TaskId(task_id))
        # THE gate: refuses an unassigned or human-assigned task, refuses an unknown
        # agent id, and otherwise hands back the Agent that carries provider/model.
        agent = self._agents.registry().require_executable(task.assignee)
        request = ExecutionRequest(
            provider_name=agent.provider_name,
            model_name=agent.model_name,
            title=task.title,
            description=task.description,
        )
        outcome = self._provider.run(request)
        result = ExecutionResult(
            task_id=task.id,
            agent_id=agent.id,
            succeeded=outcome.succeeded,
            output=outcome.output,
        )
        self._results.append(result)  # append-only history; never overwrites
        return result

    def history(self, task_id: str) -> List[ExecutionResult]:
        """A task's execution results, oldest first."""
        return self._results.for_task(TaskId(task_id))
