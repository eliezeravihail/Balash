"""The status a task can be in.

A status is a closed set of three real values, not an open string. Modelling it as
an enum means "is this a real status?" is answered once, here, and a caller cannot
accidentally set a task to "in-progres" or "archived". Every transition among the
three is deliberately allowed (including reopening a done task) -- that product rule
lives on the Task, which is the thing that changes status; this type's only job is to
be one of exactly three values and to translate to and from the words people type and
read.
"""

from __future__ import annotations

from enum import Enum

from .errors import InvalidStatusError


class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

    @property
    def label(self) -> str:
        """How this status reads to a person."""
        return self.value.replace("_", " ")

    @classmethod
    def parse(cls, text: str) -> "Status":
        """Turn something a person typed into a Status, accepting the natural
        spellings ("in progress", "in-progress", "in_progress"). Raises a domain
        error naming the real choices when the text is not one of them."""
        normalized = text.strip().lower().replace("-", "_").replace(" ", "_")
        for status in cls:
            if status.value == normalized:
                return status
        choices = ", ".join(s.label for s in cls)
        raise InvalidStatusError(
            f"{text!r} is not a task status; choose one of: {choices}"
        )
