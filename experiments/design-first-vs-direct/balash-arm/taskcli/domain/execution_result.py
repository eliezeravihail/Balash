"""The record of one execution of an agent-assigned task.

An execution result *is* an immutable fact: "this run happened against this task by
this agent, it succeeded or failed, and here is the text it produced." It is
deliberately a record with no rich behaviour -- inventing behaviour on a historical
fact would be artificial. It carries no id of its own: nothing ever references a result
singly (history is append-only and read per task), so a result-id type would have no
second caller.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ids import AgentId, TaskId


@dataclass(frozen=True)
class ExecutionResult:
    task_id: TaskId
    agent_id: AgentId
    succeeded: bool
    output: str

    def __post_init__(self) -> None:
        # One construction funnel: fresh results and rebuilt-from-storage results both
        # pass through here.
        if not isinstance(self.task_id, TaskId):
            raise ValueError("an execution result needs a TaskId")
        if not isinstance(self.agent_id, AgentId):
            raise ValueError("an execution result needs an AgentId")
