"""Identity value objects.

A member id and a task id are not just strings: they are stable identifiers with
one rule (they cannot be blank) and they must never be confused with each other or
with an arbitrary piece of text. Giving each its own tiny type means a reader and a
caller can see at a glance which kind of identifier a function wants, and the blank
rule is enforced in exactly one place instead of re-checked at every call site.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class MemberId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("a member id cannot be blank")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AgentId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("an agent id cannot be blank")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TaskId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("a task id cannot be blank")

    @classmethod
    def new(cls) -> "TaskId":
        """Mint a fresh, unique task id. This is the only source of new ids."""
        return cls(uuid.uuid4().hex)

    def __str__(self) -> str:
        return self.value
