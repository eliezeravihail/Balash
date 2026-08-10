"""The provider seam -- where "run the agent's work" is expressed without hard-coding
how the work is done.

Provider is a genuine interface: the plausible second implementation is a real AI
provider that makes an HTTP call to a model API and returns the same succeeded/output
contract -- same behaviour, entirely different mechanism. That real provider is out of
scope and is deliberately NOT built here; only the port and one local implementation
exist.

What the seam legitimately leaks: "work can fail" (succeeded) and "work produces text"
(output). What it must not leak, and does not: that this is or ever will be a network
call, any HTTP/SDK type, or the local implementation's internals. ExecutionRequest and
ExecutionOutcome are plain records that carry no domain ids -- which is exactly why
they live here in the execution layer, not in the domain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExecutionRequest:
    provider_name: str
    model_name: str
    title: str
    description: str


@dataclass(frozen=True)
class ExecutionOutcome:
    succeeded: bool
    output: str


class Provider(Protocol):
    def run(self, request: ExecutionRequest) -> ExecutionOutcome:
        """Run the agent's work and report success/failure plus text output."""
        ...


class LocalProvider:
    """The one real implementation today: deterministic local output that NEVER touches
    the network. It reads provider_name/model_name and the task's title/description to
    shape its text, and invents no network call.

    Success rule (deterministic, network-free): the run succeeds when the task carries
    a description for the agent to act on, and fails when there are no instructions --
    a plausible, reproducible stand-in for "the work could not be completed."
    """

    def run(self, request: ExecutionRequest) -> ExecutionOutcome:
        instructions = request.description.strip()
        if not instructions:
            return ExecutionOutcome(
                succeeded=False,
                output=(
                    f"[{request.provider_name}/{request.model_name}] could not run "
                    f"'{request.title}': no instructions were given for the agent to "
                    "act on; add a description to the task and try again"
                ),
            )
        return ExecutionOutcome(
            succeeded=True,
            output=(
                f"[{request.provider_name}/{request.model_name}] completed "
                f"'{request.title}': {instructions}"
            ),
        )
