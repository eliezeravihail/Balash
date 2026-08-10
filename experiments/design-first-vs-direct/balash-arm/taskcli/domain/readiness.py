"""Whether a task can be worked yet, given its prerequisites.

A task is either READY (everything it waits on is done) or BLOCKED (something it waits
on is not done yet). That is a closed set of exactly two values, so it is modelled like
Status rather than as a bare bool: the rule that decides between them returns a *named*
domain value, and the words shown to a person ("ready"/"blocked") are owned here, not
re-invented by whatever prints a task.

Readiness is never stored. It is derived from the current statuses of the tasks a task
depends on, every time it is asked -- so there is no "mark ready" mutator any entry path
could get wrong. The single place that decides it is ``Prerequisites`` (see
``prerequisites.py``); this type is only the vocabulary that decision speaks in.
"""

from __future__ import annotations

from enum import Enum


class Readiness(Enum):
    """The two -- and only two -- states a task's prerequisites leave it in."""

    READY = "ready"
    BLOCKED = "blocked"

    @property
    def label(self) -> str:
        """How this reads to a person."""
        return self.value

    @property
    def is_ready(self) -> bool:
        return self is Readiness.READY
